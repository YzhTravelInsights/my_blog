"""
管理后台 API — 仅主人可访问（Bearer OWNER_SECRET）

GET  /api/admin/summary   → 后台数据（文章 / 分类 / 标签 / 评论 / 私密评论 /
                            长期记忆 / 人格印象 / RAG 索引 / 好感度）+ 系统运行信息。
POST /api/admin/article   → 主人发布文章：写 markdown 文件 → 刷新加载器 → 增量入 RAG 向量库。
"""

import os
import platform
import re
import sqlite3
import sys
import time
from datetime import datetime

import flask
import yaml
from flask import Blueprint, current_app, jsonify, request

from modules.auth import require_owner
from config import API_ERROR_LOG, ARTICLES_DIR

admin_bp = Blueprint("admin", __name__)


def _ok(data):
    return jsonify({"code": 0, "msg": "ok", "data": data})


def _count(db_path: str, table: str, where: str = "") -> int:
    try:
        conn = sqlite3.connect(db_path)
        sql = f"SELECT COUNT(*) AS n FROM {table}"
        if where:
            sql += f" WHERE {where}"
        n = conn.execute(sql).fetchone()[0]
        conn.close()
        return n
    except Exception:
        return -1


def _format_uptime(seconds: int) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h} 小时 {m} 分 {s} 秒"
    if m:
        return f"{m} 分 {s} 秒"
    return f"{s} 秒"


def _format_size(num_bytes: int) -> str:
    """字节数 → 人类可读（KB / MB）。"""
    if num_bytes < 0:
        return "未知"
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / 1024 / 1024:.2f} MB"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes} B"


def _query_rows(db_path: str, sql: str, params: tuple = ()) -> list[dict]:
    """安全执行只读查询，返回 dict 列表；出错返回空列表。"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


@admin_bp.route("/api/admin/summary", methods=["GET"])
@require_owner
def summary():
    app = current_app
    db = app.config["DATABASE_PATH"]

    loader = app.extensions.get("article_loader")
    rag = app.extensions.get("rag_service")
    affinity_svc = app.extensions.get("affinity_service")
    memory_svc = app.extensions.get("memory_service")
    quota_svc = app.extensions.get("quota_service")
    started_at = app.extensions.get("_started_at")

    # ---- 文章全量（缓存带 mtime 检查，仅在管理页读取）----
    articles: list[dict] = []
    if loader:
        try:
            articles = loader.load_all().get("articles", [])
        except Exception:
            articles = []
    article_stats = loader.get_stats() if loader else {}
    title_by_id = {a["id"]: a["title"] for a in articles}

    # 分类 / 标签 计数
    cat_counts: dict[str, int] = {}
    tag_counts: dict[str, int] = {}
    for a in articles:
        cat = a.get("category", "未分类")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        for t in a.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    # 全量文章（管理页「文章管理」用，按日期倒序）
    recent_articles = [
        {
            "id": a["id"],
            "title": a["title"],
            "date": a.get("date", ""),
            "category": a.get("category", ""),
            "tags": a.get("tags", []),
        }
        for a in articles
    ]

    memory_total = -1
    if memory_svc and hasattr(memory_svc, "stats"):
        try:
            memory_total = memory_svc.stats().get("total_memories", -1)
        except Exception:
            memory_total = -1

    indexed = -1
    if rag and hasattr(rag, "indexed_ids"):
        try:
            indexed = len(rag.indexed_ids())
        except Exception:
            indexed = -1

    affinity = affinity_svc.get("owner") if affinity_svc else {}
    try:
        from modules.affinity.models import get as _get_affinity_row
        _row = _get_affinity_row(db)
        if _row and "last_interaction_at" in _row:
            affinity["last_interaction_at"] = _row["last_interaction_at"]
    except Exception:
        pass

    recent_comments = _query_rows(
        db,
        "SELECT id, article_id, nickname, content, is_private, created_at "
        "FROM comments ORDER BY created_at DESC",
    )
    for c in recent_comments:
        c["article_title"] = title_by_id.get(c.get("article_id", ""), c.get("article_id", ""))

    recent_impressions = _query_rows(
        db,
        "SELECT id, content, weight, created_at FROM impressions "
        "WHERE weight >= 0.1 ORDER BY created_at DESC LIMIT 10",
    )

    # ---- 系统运行信息 ----
    uptime_seconds = max(0, int(time.time() - started_at)) if started_at else None
    api_errors = 0
    try:
        with open(API_ERROR_LOG, encoding="utf-8") as f:
            api_errors = sum(1 for line in f if line.strip())
    except FileNotFoundError:
        api_errors = 0
    except Exception:
        api_errors = -1

    db_size = -1
    try:
        db_size = os.path.getsize(db)
    except Exception:
        db_size = -1

    return _ok({
        "content": {
            "articles": article_stats.get("total_articles", -1),
            "categories": article_stats.get("categories", -1),
            "tags": article_stats.get("tags", -1),
            "comments": _count(db, "comments"),
            "private_comments": _count(db, "comments", "is_private=1"),
            "memory": memory_total,
            "impressions": _count(db, "impressions"),
            "indexed": indexed,
            "affinity": affinity,
            "category_counts": [
                {"name": k, "count": v} for k, v in sorted(cat_counts.items(), key=lambda x: -x[1])
            ],
            "tag_counts": [
                {"name": k, "count": v} for k, v in sorted(tag_counts.items(), key=lambda x: -x[1])
            ],
            "recent_articles": recent_articles,
            "recent_comments": recent_comments,
            "recent_impressions": recent_impressions,
        },
        "system": {
            "version": "1.0",
            "started_at": started_at,
            "uptime_seconds": uptime_seconds,
            "uptime": _format_uptime(uptime_seconds) if uptime_seconds is not None else "未知",
            "api_errors": api_errors,
            "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "python": sys.version.split()[0],
            "flask": flask.__version__,
            "platform": platform.system(),
            "hostname": platform.node(),
            "pid": os.getpid(),
            "db": db,
            "db_size": db_size,
            "db_size_text": _format_size(db_size),
            "api_error_log": API_ERROR_LOG,
            # 每日 API 花费限额：访客额度 / 主人用量 / 历史记录
            "quota": quota_svc.summary() if quota_svc else {},
        },
    })


# ---------------------------------------------------------------------------
# 发布文章
# ---------------------------------------------------------------------------

def _slugify(title: str) -> str:
    """标题 → 文件名 slug：保留中英文/数字，其余转 -，最多 40 字符。"""
    s = re.sub(r"[^\w一-鿿]+", "-", title.lower()).strip("-")
    if not s:
        s = "article"
    return s[:40]


def _unique_filename(date: str, slug: str) -> str:
    """生成不重名的 md 文件名：YYYY-MM-DD-slug.md，冲突时追加 -n。"""
    base = f"{date}-{slug}"
    candidate = f"{base}.md"
    n = 2
    while os.path.exists(os.path.join(ARTICLES_DIR, candidate)):
        candidate = f"{base}-{n}.md"
        n += 1
    return candidate


@admin_bp.route("/api/admin/article", methods=["POST"])
@require_owner
def create_article():
    """主人发布文章：{title, category, tags, content} → 写 md → 刷新加载器 → 入 RAG。"""
    app = current_app
    body = request.get_json(silent=True) or {}

    title = str(body.get("title", "")).strip()
    content = str(body.get("content", "")).strip()
    if not title or not content:
        return jsonify({"code": 1, "msg": "标题和正文不能为空", "data": None}), 400

    category = str(body.get("category", "")).strip() or "未分类"

    raw_tags = body.get("tags")
    if isinstance(raw_tags, str):
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    elif isinstance(raw_tags, list):
        tags = [str(t).strip() for t in raw_tags if str(t).strip()]
    else:
        tags = []

    # frontmatter：标题 / 日期 / 分类 / 标签（yaml 序列化保证特殊字符安全）
    date = datetime.now().strftime("%Y-%m-%d")
    meta = {"title": title, "date": date, "category": category, "tags": tags}
    front = "---\n" + yaml.safe_dump(
        meta, allow_unicode=True, sort_keys=False, default_flow_style=False
    ) + "---\n"

    fname = _unique_filename(date, _slugify(title))
    fpath = os.path.join(ARTICLES_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(front + "\n" + content + "\n")

    # 让文章立即生效：刷新加载器缓存 + 增量入向量库（kb_watcher 稍后也会幂等补入）
    loader = app.extensions.get("article_loader")
    rag = app.extensions.get("rag_service")
    article_id = os.path.splitext(fname)[0]
    if loader is not None:
        loader.reload()
    if loader is not None and rag is not None:
        new_article = loader.get_article(article_id)
        if new_article is not None:
            try:
                rag.upsert_articles([new_article])
            except Exception:
                # 向量化失败不影响文章发布，稍后 kb_watcher 会重试
                pass

    return _ok({
        "id": article_id,
        "title": title,
        "filename": fname,
        "url": f"/article/{article_id}",
    })


# ---------------------------------------------------------------------------
# 删除（仅主人可用）
# ---------------------------------------------------------------------------

@admin_bp.route("/api/admin/article/<article_id>", methods=["DELETE"])
@require_owner
def delete_article(article_id: str):
    """主人删除文章：删 md 文件 → 清 RAG 索引 → 刷新加载器 → 删该文章全部评论。"""
    app = current_app
    db = app.config["DATABASE_PATH"]
    loader = app.extensions.get("article_loader")
    rag = app.extensions.get("rag_service")

    fpath = os.path.join(ARTICLES_DIR, article_id + ".md")
    if not os.path.isfile(fpath):
        return jsonify({"code": 1, "msg": "文章不存在", "data": None}), 404

    # 1. 删 md 文件（源文件删除失败则整体回滚）
    os.remove(fpath)

    # 2. 清 RAG 向量索引（失败不影响文件删除，kb_watcher 不处理删除）
    if rag is not None:
        try:
            rag.delete_article(article_id)
        except Exception as e:
            app.logger.warning("删除文章 RAG 索引失败: %s", e)

    # 3. 刷新加载器，文章立即可见地从列表消失
    if loader is not None:
        try:
            loader.reload()
        except Exception:
            pass

    # 4. 删该文章的全部评论（含回复，CASCADE）
    deleted_comments = -1
    try:
        from modules.comments.models import delete_comments_for_article
        deleted_comments = delete_comments_for_article(db, article_id)
    except Exception as e:
        app.logger.warning("删除文章评论失败: %s", e)

    return _ok({
        "id": article_id,
        "deleted_comments": deleted_comments,
        "hint": f"已删除文章及其 {max(deleted_comments, 0)} 条评论",
    })


@admin_bp.route("/api/admin/comment/<int:comment_id>", methods=["DELETE"])
@require_owner
def delete_comment(comment_id: int):
    """主人删除单条评论（含其全部回复，CASCADE）。"""
    app = current_app
    db = app.config["DATABASE_PATH"]
    n = 0
    try:
        from modules.comments.models import delete_comment as _delete_comment
        n = _delete_comment(db, comment_id)
    except Exception as e:
        app.logger.warning("删除评论失败: %s", e)

    if n == 0:
        return jsonify({"code": 1, "msg": "评论不存在或已删除", "data": None}), 404
    return _ok({"id": comment_id, "deleted": n, "hint": f"已删除评论（含 {n - 1} 条回复）"})
