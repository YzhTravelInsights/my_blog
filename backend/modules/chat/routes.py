"""
AI 对话 API Blueprint

端点：
    POST /api/chat — 公开聊天（当前阶段）
    POST /api/chat/owner — 主人聊天（chat-owner 模块扩展）
"""

from flask import Blueprint, request, jsonify, current_app
from .service import chat
from modules.auth import require_owner

chat_bp = Blueprint("chat", __name__)


def _ok(data, msg="ok"):
    return jsonify({"code": 0, "msg": msg, "data": data})


def _err(code, msg):
    return jsonify({"code": code, "msg": msg, "data": None})


# ---------------------------------------------------------------------------
# POST /api/chat
# ---------------------------------------------------------------------------
@chat_bp.route("/api/chat", methods=["POST"])
def public_chat():
    body = request.get_json(silent=True) or {}

    message = body.get("message", "").strip()
    if not message:
        return _err(1, "消息不能为空"), 400
    if len(message) > 2000:
        return _err(1, "消息过长"), 400

    session_id = body.get("session_id", "anonymous")
    session_type = body.get("session_type", "guest")
    history = body.get("history", [])

    # 校验 history 格式
    if not isinstance(history, list):
        history = []
    history = [
        h for h in history
        if isinstance(h, dict) and "role" in h and "content" in h
    ]

    # RAG 检索
    rag = current_app.extensions.get("rag_service")
    rag_context = rag.build_context(message) if rag else ""

    result = chat(
        message=message,
        session_id=session_id,
        history=history,
        session_type=session_type,
        mode="public",
        rag_context=rag_context,
    )

    # 追加 sources（RAG 引用）
    if rag:
        hits = rag.search(message, k=3)
        result["sources"] = [
            {"article_id": h["article_id"], "title": h["title"], "relevance": h["relevance"]}
            for h in hits
        ]

    return _ok(result)


# ---------------------------------------------------------------------------
# POST /api/chat/owner
# ---------------------------------------------------------------------------
@chat_bp.route("/api/chat/owner", methods=["POST"])
@require_owner
def owner_chat():
    body = request.get_json(silent=True) or {}

    message = body.get("message", "").strip()
    if not message:
        return _err(1, "消息不能为空"), 400

    session_id = body.get("session_id", "owner")
    history = body.get("history", [])
    if not isinstance(history, list):
        history = []
    history = [h for h in history if isinstance(h, dict) and "role" in h and "content" in h]

    # RAG 检索
    rag = current_app.extensions.get("rag_service")
    rag_context = rag.build_context(message) if rag else ""

    # 好感度
    affinity_svc = current_app.extensions.get("affinity_service")
    affinity_ctx = affinity_svc.get_prompt() if affinity_svc else ""
    affinity_status = affinity_svc.get("owner") if affinity_svc else {}

    # 长期记忆
    memory_svc = current_app.extensions.get("memory_service")
    memory_ctx = memory_svc.build_context(message) if memory_svc else ""

    # 人格演化
    personality_svc = current_app.extensions.get("personality_service")
    personality_ctx = personality_svc.build_context() if personality_svc else ""

    # 对话
    result = chat(
        message=message,
        session_id=session_id,
        history=history,
        session_type="owner",
        mode="owner",
        rag_context=rag_context,
        affinity_context=affinity_ctx,
        memory_context=memory_ctx,
        personality_context=personality_ctx,
    )

    # 写入（好感度、记忆、人格）
    if affinity_svc:
        affinity_svc.record_interaction()
        result["affinity"] = affinity_svc.get("owner")

    if memory_svc:
        from .service import judge_memory
        memory_svc.decide_and_store(message, result["reply"], session_id, judge_memory)

    if personality_svc:
        from .service import judge_impression
        generated = personality_svc.generate_and_store(
            message, result["reply"], session_id, judge_impression
        )
        if generated:
            result["impression_generated"] = generated

    # 衰减印象
    if personality_svc:
        personality_svc.decay()

    # RAG sources
    if rag:
        hits = rag.search(message, k=3)
        result["sources"] = [
            {"article_id": h["article_id"], "title": h["title"], "relevance": h["relevance"]}
            for h in hits
        ]

    return _ok(result)
