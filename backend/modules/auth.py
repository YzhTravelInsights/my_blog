"""
鉴权中间件 — 验证 OWNER_SECRET Bearer Token

使用:
    @require_owner
    def my_owner_route():
        ...
"""

import os
from functools import wraps
from flask import request, jsonify


def _get_owner_secret() -> str:
    return os.getenv("OWNER_SECRET", "")


def require_owner(f):
    """装饰器：验证 Authorization: Bearer <OWNER_SECRET>"""
    @wraps(f)
    def decorated(*args, **kwargs):
        secret = _get_owner_secret()
        if not secret:
            return jsonify({"code": 2, "msg": "服务未配置 OWNER_SECRET"}), 500

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or auth[7:] != secret:
            return jsonify({"code": 2, "msg": "unauthorized"}), 401

        return f(*args, **kwargs)
    return decorated
