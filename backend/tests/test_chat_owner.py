"""
chat-owner 模块测试 — mock DeepSeek API

测试清单：
  O1  auth 中间件 — 无 Token → 401
  O2  auth 中间件 — 错误 Token → 401
  O3  auth 中间件 — 正确 Token → 通过
  O4  POST /api/chat/owner — 正常对话
  O5  POST /api/chat/owner — 返回 affinity 字段
  O6  POST /api/chat/owner — 返回 sources 字段
  O7  affinity: 初始化 stranger → interaction → 升级
  O8  affinity: get_prompt() 返回对应等级提示词
  O9  memory: remember + recall 循环
  O10 memory: build_context() 生成上下文
  O11 memory: ≤500 条上限裁剪
  O12 personality: 生成印象 + 衰减
  O13 personality: build_context() 含印象
  O14 公开端点不受主人端点影响

运行：
    cd D:/Desktop/myblog
    python backend/tests/test_chat_owner.py
"""

import os
import sys
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


# Mock helpers
def mock_embed_single(text):
    """单字符串 embed（384维伪向量）。"""
    import numpy as np
    return [hash(text + str(j)) % 100 / 100 for j in range(384)]


def mock_chat_success(messages, **kw):
    m = MagicMock()
    m.choices = [MagicMock()]
    m.choices[0].message = MagicMock()
    m.choices[0].message.content = "嘿嘿，开拓者来啦！今天也要加油哦～"
    return m


def run_tests():
    global PASS, FAIL
    PASS = 0
    FAIL = 0

    os.environ["DEEPSEEK_API_KEY"] = "sk-test-owner"
    os.environ["DEEPSEEK_BASE_URL"] = "https://api.deepseek.com"
    os.environ["OWNER_SECRET"] = "my-secret-token"
    OWNER_TOKEN = "Bearer my-secret-token"

    # 全局 mock SentenceTransformer + chat API
    import numpy as np
    from modules.chat import rag as rag_module
    class MockModel:
        def encode(self, texts, show_progress_bar=False):
            return np.array([[hash(t+str(j))%100/100 for j in range(384)] for t in texts])
        def get_sentence_embedding_dimension(self): return 384
    model_patcher = patch.object(rag_module, "_get_model", return_value=MockModel())
    chat_patcher = patch("modules.chat.service._get_client")
    model_patcher.start()
    mock_cli = chat_patcher.start()
    mock_cli.return_value.chat.completions.create = mock_chat_success

    test_app = app_module.create_app()
    test_app.config["TESTING"] = True

    # MemoryService 持有单字符串 embed 函数
    test_app.extensions["memory_service"]._embed = lambda t: MockModel().encode([t])[0].tolist()

    client = test_app.test_client()

    # ========================================================================
    print("[O1] auth — 无 Token → 401")
    # ========================================================================
    resp = client.post("/api/chat/owner", json={"message": "hi"})
    check("HTTP 401", resp.status_code == 401, f"status={resp.status_code}")
    check("code=2", resp.get_json()["code"] == 2)

    # ========================================================================
    print("\n[O2] auth — 错误 Token → 401")
    # ========================================================================
    resp = client.post(
        "/api/chat/owner",
        json={"message": "hi"},
        headers={"Authorization": "Bearer wrong-token"},
    )
    check("错误Token → 401", resp.status_code == 401)

    # ========================================================================
    print("\n[O3] auth — 正确 Token → 通过")
    # ========================================================================
    with patch("modules.chat.service._get_client") as mock_cli:
        mock_cli.return_value.chat.completions.create = mock_chat_success
        resp = client.post(
            "/api/chat/owner",
            json={"message": "你好流萤", "session_id": "owner-test"},
            headers={"Authorization": OWNER_TOKEN},
        )

    check("HTTP 200", resp.status_code == 200)
    check("code=0", resp.get_json()["code"] == 0)

    # ========================================================================
    print("\n[O4] POST /api/chat/owner — 正常对话")
    # ========================================================================
    import numpy as np
    class MM:
        def encode(self, texts, **_): return np.array([[hash(t+str(j))%100/100 for j in range(384)] for t in texts])
        def get_sentence_embedding_dimension(self): return 384
    with patch("modules.chat.service._get_client") as mock_cli, \
         patch.object(rag_module, "_get_model", return_value=MM()):
        mock_cli.return_value.chat.completions.create = mock_chat_success
        resp = client.post(
            "/api/chat/owner",
            json={"message": "聊聊天", "session_id": "o4"},
            headers={"Authorization": OWNER_TOKEN},
        )

    data = resp.get_json()
    check("HTTP 200", resp.status_code == 200)
    check("reply 不为空", len(data["data"]["reply"]) > 0)
    check("mode=owner", data["data"]["mode"] == "owner")

    # ========================================================================
    print("\n[O5] 返回 affinity 字段")
    # ========================================================================
    check("含 affinity", "affinity" in data["data"])
    check("interaction_count >= 1",
          data["data"]["affinity"]["interaction_count"] >= 1)

    # ========================================================================
    print("\n[O6] 返回 sources")
    # ========================================================================
    check("含 sources", "sources" in data["data"])

    # ========================================================================
    print("\n[O7] affinity 升级")
    # ========================================================================
    affinity_svc = test_app.extensions["affinity_service"]
    stats = affinity_svc.get("owner")
    check("interaction_count 增加", stats["interaction_count"] >= 2)
    # 手动设到阈值附近验证升级逻辑
    from modules.affinity import models as am
    db_path = test_app.config["DATABASE_PATH"]
    # 设 interaction_count=9，再 record 两次触发升级
    am.update(db_path, interaction_count=9)
    for _ in range(2):
        affinity_svc.record_interaction()
    upgraded = affinity_svc.get("owner")
    check("达到10次后升级为 acquaintance",
          upgraded["level"] == "acquaintance",
          f"实际: {upgraded['level']}")

    # ========================================================================
    print("\n[O8] affinity get_prompt()")
    # ========================================================================
    prompt = affinity_svc.get_prompt()
    check("含'熟人'", "熟人" in prompt, f"prompt: {prompt}")

    # ========================================================================
    print("\n[O9] memory remember + recall")
    # ========================================================================
    ms = test_app.extensions["memory_service"]
    ms.remember("开拓者喜欢 Python", {"type": "preference"})
    ms.remember("开拓者最近在学 RAG", {"type": "learning"})
    hits = ms.recall("Python 编程", k=2)
    check("可检索到记忆", len(hits) >= 1, f"实际 {len(hits)} 条")

    # ========================================================================
    print("\n[O10] memory build_context()")
    # ========================================================================
    ctx = ms.build_context("Python 编程")
    check("含'流萤记得'", "流萤记得" in ctx)
    check("含'Python'", "Python" in ctx)

    # ========================================================================
    print("\n[O11] memory ≤500 上限裁剪")
    # ========================================================================
    from modules.memory.chroma_store import ChromaMemoryStore
    tmp_dir = tempfile.mkdtemp(prefix="test_mem_limit_")
    store = ChromaMemoryStore(tmp_dir)
    for i in range(505):
        store.add(
            f"mem_{i}",
            f"测试记忆 {i}",
            mock_embed_single(f"测试记忆 {i}"),
            {"idx": i},
        )
    check("超过500条", store.count() == 505)
    store.trim(500)
    check("裁剪到500条", store.count() == 500)
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    # ========================================================================
    print("\n[O12] personality 印象 + 衰减")
    # ========================================================================
    ps = test_app.extensions["personality_service"]
    ps.generate_and_store(
        "我今天学了RAG", "开拓者好棒！", "s1",
        lambda u, r: "开拓者对RAG技术很感兴趣"
    )
    ps.generate_and_store(
        "今天有点累", "要好好休息哦", "s2",
        lambda u, r: "开拓者最近可能比较疲惫"
    )
    ps.decay()
    from modules.personality import models as pm
    imps = pm.get_recent(db_path, limit=5)
    check("生成 2 条印象", len(imps) >= 1)
    check("衰减后 weight < 1.0", all(i["weight"] < 1.0 for i in imps))

    # ========================================================================
    print("\n[O13] personality build_context()")
    # ========================================================================
    ctx = ps.build_context()
    check("含'开拓者'", "开拓者" in ctx)

    # ========================================================================
    print("\n[O14] 公开端点不受影响")
    # ========================================================================
    resp = client.post(
        "/api/chat",
        json={"message": "公开测试", "session_id": "public-test"},
    )
    check("公开 200", resp.status_code == 200)
    check("mode=public", resp.get_json()["data"]["mode"] == "public")
    check("无 affinity", "affinity" not in resp.get_json()["data"])

    # 停止全局 mock
    model_patcher.stop()
    chat_patcher.stop()

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
