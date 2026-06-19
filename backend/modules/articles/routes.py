"""
文章 API Blueprint

端点：
    GET /api/articles              — 文章列表（分页、分类、标签、搜索）
    GET /api/articles/<article_id> — 文章详情
    GET /api/about                 — 关于页
"""

from flask import Blueprint, request, jsonify, current_app
from .loader import ArticleLoader

articles_bp = Blueprint("articles", __name__)

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50


def _ok(data, msg="ok"):
    return jsonify({"code": 0, "msg": msg, "data": data})


def _err(code, msg):
    return jsonify({"code": code, "msg": msg, "data": None})


def _get_loader() -> ArticleLoader:
    """从 Flask app 上下文获取 ArticleLoader 单例。"""
    return current_app.extensions["article_loader"]


# ---------------------------------------------------------------------------
# GET /api/articles
# ---------------------------------------------------------------------------
@articles_bp.route("/api/articles", methods=["GET"])
def list_articles():
    loader = _get_loader()
    all_data = loader.load_all()
    articles = all_data["articles"]
    all_categories = all_data["filters"]["categories"]
    all_tags = all_data["filters"]["tags"]

    # ---- 筛选 ----
    category = request.args.get("category", "").strip()
    tag = request.args.get("tag", "").strip()
    search = request.args.get("search", "").strip()

    if category:
        articles = [a for a in articles if a["category"] == category]
    if tag:
        articles = [a for a in articles if tag in a["tags"]]
    if search:
        kw = search.lower()
        articles = [
            a
            for a in articles
            if kw in a["title"].lower() or kw in a["content"].lower()
        ]

    # ---- 分页 ----
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1
    try:
        page_size = int(request.args.get("page_size", DEFAULT_PAGE_SIZE))
        page_size = min(max(1, page_size), MAX_PAGE_SIZE)
    except ValueError:
        page_size = DEFAULT_PAGE_SIZE

    total = len(articles)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    paged = articles[start : start + page_size]

    # 列表接口去掉 content 字段
    list_data = []
    for a in paged:
        list_data.append(
            {
                "id": a["id"],
                "title": a["title"],
                "summary": a["summary"],
                "category": a["category"],
                "tags": a["tags"],
                "date": a["date"],
            }
        )

    return _ok(
        {
            "articles": list_data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            },
            "filters": {
                "categories": sorted(all_categories),
                "tags": sorted(all_tags),
            },
        }
    )


# ---------------------------------------------------------------------------
# GET /api/articles/<article_id>
# ---------------------------------------------------------------------------
@articles_bp.route("/api/articles/<article_id>", methods=["GET"])
def get_article(article_id):
    loader = _get_loader()
    article = loader.get_article(article_id)
    if article is None:
        return _err(1, "文章不存在"), 404
    return _ok(article)


# ---------------------------------------------------------------------------
# GET /api/about
# ---------------------------------------------------------------------------
@articles_bp.route("/api/about", methods=["GET"])
def about():
    loader = _get_loader()
    about_data = loader.get_about()
    return _ok(about_data)
