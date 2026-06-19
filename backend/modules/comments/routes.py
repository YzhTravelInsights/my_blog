"""
评论 API Blueprint

端点：
    GET  /api/comments?article_id=<id>[&admin_key=xxx]
    POST /api/comments
"""

import os
from flask import Blueprint, request, jsonify, current_app
from . import models

comments_bp = Blueprint("comments", __name__)

MAX_TOP_LEVEL = 5   # 同IP同文章最多5条顶级评论
MAX_REPLIES = 5     # 同IP同父评论最多5条回复


def _db_path() -> str:
    return current_app.config["DATABASE_PATH"]


def _admin_key() -> str:
    return os.getenv("ADMIN_KEY", "")


def _client_ip() -> str:
    """获取客户端 IP（兼容代理）。"""
    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def _ok(data, msg="ok"):
    return jsonify({"code": 0, "msg": msg, "data": data})


def _err(code, msg):
    return jsonify({"code": code, "msg": msg, "data": None})


# ---------------------------------------------------------------------------
# GET /api/comments
# ---------------------------------------------------------------------------
@comments_bp.route("/api/comments", methods=["GET"])
def list_comments():
    article_id = request.args.get("article_id", "").strip()
    if not article_id:
        return _err(1, "缺少 article_id 参数"), 400

    # 判断是否显示私密评论
    admin_key = request.args.get("admin_key", "").strip()
    is_admin = bool(admin_key and admin_key == _admin_key())
    include_private = is_admin

    comment_tree = models.get_comments_by_article(
        _db_path(), article_id, include_private=include_private
    )

    # 统计
    stats = models.get_comment_count(_db_path(), article_id)

    return _ok({"comments": comment_tree, "count": stats["count"]})


# ---------------------------------------------------------------------------
# POST /api/comments
# ---------------------------------------------------------------------------
@comments_bp.route("/api/comments", methods=["POST"])
def create_comment():
    body = request.get_json(silent=True) or {}

    article_id = body.get("article_id", "").strip()
    content = body.get("content", "").strip()
    nickname = body.get("nickname", "").strip() or "匿名"
    parent_id = body.get("parent_id")
    is_private = bool(body.get("is_private", False))

    # 校验
    if not article_id:
        return _err(1, "缺少 article_id"), 400
    if not content:
        return _err(1, "评论内容不能为空"), 400
    if len(content) > 5000:
        return _err(1, "评论内容过长（最多5000字）"), 400

    ip = _client_ip()

    # 速率限制
    limit = models.get_comment_count(_db_path(), article_id, ip=ip, parent_id=parent_id)
    if parent_id is None and limit["count"] >= MAX_TOP_LEVEL:
        return _err(4, f"该文章下评论已达上限（{MAX_TOP_LEVEL}条）"), 429
    if parent_id is not None and limit["count"] >= MAX_REPLIES:
        return _err(4, f"该评论下回复已达上限（{MAX_REPLIES}条）"), 429

    result = models.create_comment(
        _db_path(),
        article_id=article_id,
        ip=ip,
        content=content,
        nickname=nickname,
        parent_id=parent_id,
        is_private=is_private,
    )

    return _ok(result, "评论成功")
