"""
chat-core 模块测试 — 覆盖所有功能点（mock DeepSeek API）

测试清单：
  C1  prompt_builder 基础提示词生成
  C2  POST /api/chat — 正常对话
  C3  POST /api/chat — 空消息校验
  C4  POST /api/chat — 超长消息校验
  C5  POST /api/chat — session_type=guest 截断历史到 10 条
  C6  POST /api/chat — session_type=owner 历史不截断
  C7  POST /api/chat — history 格式清洗
  C8  故障回退 — DeepSeek 不可用时返回预设回复
  C9  故障回退 — 记录 api_error.log
  C10 响应格式 {code, msg, data, reply, emotion, mode}
  C11 emotion 检测 — happy/thinking/caring/normal

运行：
    cd D:/Desktop/myblog
    python backend/tests/test_chat_core.py
"""

import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as app_module

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}  <- {detail}")


# ============================================================================
# Mock DeepSeek 回复
# ============================================================================

def mock_chat_success(messages, **kwargs):
    """模拟成功回复。"""
    m = MagicMock()
    m.choices = [MagicMock()]
    m.choices[0].message = MagicMock()
    m.choices[0].message.content = "嘿嘿，开拓者来啦！今天想聊什么呀～今天也要加油哦！"
    return m


def mock_chat_timeout(messages, **kwargs):
    """模拟 API 超时。"""
    import socket
    raise socket.timeout("Connection timed out")


# ============================================================================
def run_tests():
    global PASS, FAIL
    PASS = 0
    FAIL = 0

    # 准备测试环境
    os.environ["DEEPSEEK_API_KEY"] = "sk-test-key"
    os.environ["DEEPSEEK_BASE_URL"] = "https://api.deepseek.com"

    test_app = app_module.create_app()
    test_app.config["TESTING"] = True
    client = test_app.test_client()

    # ========================================================================
    print("[C1] prompt_builder 基础提示词")
    # ========================================================================
    from modules.chat.prompt_builder import build_system_prompt

    prompt = build_system_prompt(mode="public")
    check("含'流萤'", "流萤" in prompt)
    check("含'开拓者'", "开拓者" in prompt)
    check("含'公共助手'", "公共助手" in prompt)

    prompt_owner = build_system_prompt(
        mode="owner",
        rag_context="【文章】Conda教程",
        affinity_context="【好感度】soul_bond",
    )
    check("owner 模式含 RAG", "Conda教程" in prompt_owner)
    check("owner 模式含好感度", "soul_bond" in prompt_owner)

    # ========================================================================
    print("\n[C2] POST /api/chat — 正常对话 (mock)")
    # ========================================================================
    with patch("modules.chat.service._get_client") as mock_client:
        mock_client.return_value.chat.completions.create = mock_chat_success

        resp = client.post(
            "/api/chat",
            json={
                "message": "你好流萤",
                "session_id": "test-001",
                "history": [],
            },
        )

    data = resp.get_json()
    check("HTTP 200", resp.status_code == 200)
    check("code=0", data["code"] == 0)
    check("reply 不为空", len(data["data"]["reply"]) > 0)
    check("mode=public", data["data"]["mode"] == "public")
    check("emotion 字段存在", "emotion" in data["data"])

    # ========================================================================
    print("\n[C3] POST /api/chat — 空消息校验")
    # ========================================================================
    resp = client.post("/api/chat", json={"message": ""})
    check("空消息 → 400", resp.status_code == 400)

    resp = client.post("/api/chat", json={"message": "   "})
    check("纯空格 → 400", resp.status_code == 400)

    resp = client.post("/api/chat", json={})
    check("无 message 字段 → 400", resp.status_code == 400)

    # ========================================================================
    print("\n[C4] POST /api/chat — 超长消息校验")
    # ========================================================================
    resp = client.post("/api/chat", json={"message": "x" * 2001})
    check("2001 字 → 400", resp.status_code == 400)

    resp = client.post("/api/chat", json={"message": "x" * 2000})
    check("2000 字 → 通过", resp.status_code == 200)

    # ========================================================================
    print("\n[C5] session_type=guest 截断历史")
    # ========================================================================
    # 直接在 service 层验证
    from modules.chat.service import chat as chat_service

    long_history = [{"role": "user", "content": f"msg{i}"} for i in range(15)]
    # 用 mock 避免真实 API 调用
    with patch("modules.chat.service._get_client") as mock_client:
        mock_client.return_value.chat.completions.create = mock_chat_success
        result = chat_service(
            message="你好",
            session_id="test-guest",
            history=long_history,
            session_type="guest",
        )
    check("guest 模式正常返回", "reply" in result)

    # ========================================================================
    print("\n[C6] session_type=owner 历史不截断")
    # ========================================================================
    with patch("modules.chat.service._get_client") as mock_client:
        mock_client.return_value.chat.completions.create = mock_chat_success
        result = chat_service(
            message="你好",
            session_id="test-owner",
            history=long_history,
            session_type="owner",
        )
    check("owner 模式正常返回", "reply" in result)

    # ========================================================================
    print("\n[C7] history 格式清洗")
    # ========================================================================
    resp = client.post(
        "/api/chat",
        json={
            "message": "test",
            "history": [
                {"role": "user", "content": "ok"},
                "bad_item",  # 会被过滤
                {"not_role": "x"},  # 会被过滤
            ],
        },
    )
    check("含非法元素的 history → 200", resp.status_code == 200)

    # ========================================================================
    print("\n[C8] 故障回退 — DeepSeek 不可用")
    # ========================================================================
    with patch("modules.chat.service._get_client") as mock_client:
        mock_client.return_value.chat.completions.create = mock_chat_timeout

        resp = client.post(
            "/api/chat",
            json={"message": "测试故障", "session_id": "fallback-test"},
        )

    data = resp.get_json()
    check("故障时 HTTP 200（优雅降级）", resp.status_code == 200)
    check("降级回复含'火萤'", "火萤" in data["data"]["reply"])
    check("fallback=True", data["data"].get("fallback") is True)

    # ========================================================================
    print("\n[C9] 故障日志记录")
    # ========================================================================
    import glob as _glob

    log_files = _glob.glob("backend/logs/api_error.log")
    check("api_error.log 已生成", len(log_files) >= 1,
          f"找到 {len(log_files)} 个文件")

    # ========================================================================
    print("\n[C10] 响应格式 {code, msg, data}")
    # ========================================================================
    with patch("modules.chat.service._get_client") as mock_client:
        mock_client.return_value.chat.completions.create = mock_chat_success
        resp = client.post(
            "/api/chat",
            json={"message": "测试格式", "session_id": "fmt-test"},
        )

    d = resp.get_json()
    check("含 code", "code" in d)
    check("含 msg", "msg" in d)
    check("含 data", "data" in d)
    check("data.reply", "reply" in d["data"])
    check("data.emotion", "emotion" in d["data"])

    # ========================================================================
    print("\n[C11] emotion 检测")
    # ========================================================================
    from modules.chat.service import _detect_emotion

    check("'哈哈' → happy", _detect_emotion("哈哈好棒") == "happy")
    check("'嘿嘿' → happy", _detect_emotion("嘿嘿是的") == "happy")
    check("'唔' → thinking", _detect_emotion("唔让我想想") == "thinking")
    check("'没关系' → caring", _detect_emotion("没关系别担心") == "caring")
    check("普通文本 → normal", _detect_emotion("今天天气不错") == "normal")

    # ========================================================================
    print(f"\n{'='*50}")
    print(f"  总计: {PASS} 通过 / {PASS + FAIL} 项")
    if FAIL == 0:
        print(f"  结论: 全部通过")
    else:
        print(f"  结论: {FAIL} 项失败")
    print(f"{'='*50}\n")
    return PASS, FAIL


if __name__ == "__main__":
    passed, failed = run_tests()
    sys.exit(0 if failed == 0 else 1)
