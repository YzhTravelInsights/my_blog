"""
AI 对话 API Blueprint

端点：
    POST /api/chat — 公开聊天（当前阶段）
    POST /api/chat/owner — 主人聊天（chat-owner 模块扩展）
"""

from flask import Blueprint, request, jsonify, current_app
from .service import chat

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
