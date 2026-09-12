"""
AI 对话服务层

职责：
    - 调用 DeepSeek Chat API
    - 处理故障回退
    - 按 session_type 截断对话历史
    - 编排写入（后续模块接入时扩展）

当前阶段（chat-core）：仅公开模式基础对话。
"""

import os
import time
import logging
from openai import OpenAI

from .prompt_builder import build_system_prompt
from ..security import get_deepseek_api_key
from ..quota.service import get_quota_service, QUOTA_REPLY

logger = logging.getLogger("chat")


def _record_usage(scope: str, resp):
    """记录 token 用量与花费（scope: guest / owner）。记不上也不影响对话。"""
    try:
        get_quota_service().record(scope, getattr(resp, "usage", None))
    except Exception as e:  # noqa: BLE001 —— 记账失败绝不能影响对话
        logger.warning(f"用量记录失败: {e}")


# ---------------------------------------------------------------------------
# DeepSeek 客户端
# ---------------------------------------------------------------------------

def _get_client() -> OpenAI:
    return OpenAI(
        api_key=get_deepseek_api_key(),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )


# ---------------------------------------------------------------------------
# 故障回退
# ---------------------------------------------------------------------------

FALLBACK_REPLY = "萤宝今晚似乎有点累了，暂时没办法回应你……晚点再来找我好吗？"


def _log_error(error_type: str, elapsed_ms: float, session_id: str):
    log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "api_error.log")
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {error_type} | {elapsed_ms:.0f}ms | {session_id}\n")


# ---------------------------------------------------------------------------
# 对话编排
# ---------------------------------------------------------------------------

GUEST_HISTORY_LIMIT = 10


def chat(
    message: str,
    session_id: str,
    history: list[dict],
    session_type: str = "guest",
    mode: str = "public",
    rag_context: str = "",
    affinity_context: str = "",
    memory_context: str = "",
    personality_context: str = "",
) -> dict:
    """
    执行一轮对话。

    参数:
        message:            用户最新消息
        session_id:         会话标识
        history:            历史消息 [{role, content}, ...]
        session_type:       "guest" | "owner"
        mode:               "public" | "owner"
        rag_context:        RAG 检索结果文本
        affinity_context:   好感度提示词片段（仅 owner）
        memory_context:     记忆上下文（仅 owner）
        personality_context: 人格上下文（仅 owner）

    返回:
        { reply, emotion, mode, fallback?, sources? }
    """
    # 截断历史（仅 guest 模式）
    if session_type == "guest" and len(history) > GUEST_HISTORY_LIMIT:
        history = history[-GUEST_HISTORY_LIMIT:]

    # 构建消息列表
    system_prompt = build_system_prompt(
        mode=mode,
        rag_context=rag_context,
        affinity_context=affinity_context,
        memory_context=memory_context,
        personality_context=personality_context,
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    # ---- 每日额度：访客超限直接回绝，不再调用 DeepSeek（零成本）----
    # 博主本人（mode="owner"）不受限额约束，只记账不拦截。
    if mode != "owner":
        try:
            if get_quota_service().guest_exhausted():
                logger.info(f"chat quota exhausted | guest | {session_id}")
                return {
                    "reply": QUOTA_REPLY,
                    "emotion": "normal",
                    "mode": mode,
                    "fallback": True,
                    "quota_exhausted": True,
                }
        except Exception as e:  # noqa: BLE001 —— 额度查询异常不能挡住正常聊天
            logger.warning(f"额度检查失败，放行本次对话: {e}")

    # 调用 DeepSeek
    start = time.time()
    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=500,
            temperature=0.8,
            timeout=15,
        )
        reply = resp.choices[0].message.content or ""
        emotion = _detect_emotion(reply)
        _record_usage("owner" if mode == "owner" else "guest", resp)

        # 记录成功日志（可选）
        elapsed = (time.time() - start) * 1000
        logger.info(f"chat success | {elapsed:.0f}ms | {session_id} | {session_type}")

        return {"reply": reply, "emotion": emotion, "mode": mode}

    except Exception as e:
        elapsed = (time.time() - start) * 1000
        error_type = type(e).__name__
        _log_error(error_type, elapsed, session_id)
        logger.warning(f"chat fallback | {error_type} | {session_id}")

        return {
            "reply": FALLBACK_REPLY,
            "emotion": "normal",
            "mode": mode,
            "fallback": True,
        }


# ---------------------------------------------------------------------------
# 情绪检测（简单规则，后续可升级为 DeepSeek 输出）
# ---------------------------------------------------------------------------

def judge_memory(user_msg: str, assistant_reply: str) -> dict:
    """调用 DeepSeek 判断是否值得存入长期记忆。"""
    try:
        import json
        client = _get_client()
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "判断对话是否值得长期记忆。返回JSON: {\"memorable\": bool, \"text\": \"记忆摘要\", \"importance\": 0-1}"},
                {"role": "user", "content": f"用户: {user_msg}\n流萤: {assistant_reply}"},
            ],
            max_tokens=150, temperature=0.3,
        )
        _record_usage("owner", resp)
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return {"memorable": False, "text": "", "importance": 0}


def judge_impression(user_msg: str, assistant_reply: str) -> str | None:
    """调用 DeepSeek 生成人格印象。"""
    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "基于对话生成对用户的印象，一句话。格式如'开拓者今天...'"},
                {"role": "user", "content": f"用户: {user_msg}\n流萤: {assistant_reply}"},
            ],
            max_tokens=80, temperature=0.5,
        )
        _record_usage("owner", resp)
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


def _detect_emotion(text: str) -> str:
    """简单关键词匹配，后续可让 DeepSeek 直接返回 emotion 字段。"""
    happy_words = ["哈哈", "嘿嘿", "太好了", "棒", "开心", "厉害", "喜欢"]
    thinking_words = ["唔", "让我想想", "这个嘛", "嗯..."]
    caring_words = ["没关系", "别担心", "辛苦", "抱抱", "没事的"]

    for w in happy_words:
        if w in text:
            return "happy"
    for w in thinking_words:
        if w in text:
            return "thinking"
    for w in caring_words:
        if w in text:
            return "caring"
    return "normal"
