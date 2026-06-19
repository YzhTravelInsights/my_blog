"""
article-api 模块测试

测试 Flask API 端点：
  1. GET /api/articles          — 列表 + 分页
  2. GET /api/articles?category — 分类筛选
  3. GET /api/articles?tag      — 标签筛选
  4. GET /api/articles?search   — 标题+正文搜索
  5. GET /api/articles?page=X   — 分页边界
  6. GET /api/articles/<id>     — 文章详情
  7. GET /api/articles/<bad>    — 不存在的文章
  8. GET /api/about             — 关于页
  9. 响应格式校验               — code/msg/data 结构

运行：
    cd D:/Desktop/myblog
    pip install flask flask-cors -q
    python backend/tests/test_article_api.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app

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
def test_list_articles(client):
    """GET /api/articles 基础列表"""
    print("\n[1] 文章列表 GET /api/articles")
    resp = client.get("/api/articles")
    data = resp.get_json()

    check("HTTP 200", resp.status_code == 200, f"status={resp.status_code}")
    check("code=0", data["code"] == 0, f"code={data['code']}")
    check("data.articles 为列表", isinstance(data["data"]["articles"], list))
    check("至少 1 篇文章", len(data["data"]["articles"]) >= 1)
    check("pagination 完整",
          all(k in data["data"]["pagination"] for k in ["page", "page_size", "total", "total_pages"]))
    check("filters 返回分类标签", "categories" in data["data"]["filters"])
    check("列表项不含 content",
          "content" not in data["data"]["articles"][0])


def test_pagination(client):
    """分页边界"""
    print("\n[2] 分页")
    resp = client.get("/api/articles?page=1&page_size=1")
    data = resp.get_json()
    check("page_size=1 返回 1 条",
          len(data["data"]["articles"]) == 1)

    resp2 = client.get("/api/articles?page=999")
    check("超出范围的 page 返回空列表",
          resp2.get_json()["data"]["articles"] == [])

    resp3 = client.get("/api/articles?page=abc")
    check("非法 page 回退到 page=1",
          resp3.get_json()["data"]["pagination"]["page"] == 1)


def test_category_filter(client):
    """分类筛选"""
    print("\n[3] 分类筛选 GET /api/articles?category=Python")
    resp = client.get("/api/articles?category=Python")
    articles = resp.get_json()["data"]["articles"]
    check("筛选后只返回 Python 分类",
          all(a["category"] == "Python" for a in articles))


def test_tag_filter(client):
    """标签筛选"""
    print("\n[4] 标签筛选 GET /api/articles?tag=Conda")
    resp = client.get("/api/articles?tag=Conda")
    articles = resp.get_json()["data"]["articles"]
    check("筛选后每条都含 Conda 标签",
          all("Conda" in a["tags"] for a in articles))


def test_search(client):
    """全文搜索"""
    print("\n[5] 搜索 GET /api/articles?search=Conda")
    resp = client.get("/api/articles?search=Conda")
    articles = resp.get_json()["data"]["articles"]
    check("search=Conda 筛出文章", len(articles) >= 1)


def test_article_detail(client):
    """文章详情"""
    print("\n[6] 文章详情 GET /api/articles/<id>")
    resp = client.get("/api/articles/2025-06-18-conda-python")
    data = resp.get_json()

    check("HTTP 200", resp.status_code == 200)
    check("code=0", data["code"] == 0)
    check("title 正确", data["data"]["title"] == "使用 Conda 管理 Python 环境")
    check("含 content", len(data["data"]["content"]) > 0)
    check("含 prev/next", "prev" in data["data"] and "next" in data["data"])


def test_article_not_found(client):
    """不存在的文章"""
    print("\n[7] 文章不存在 GET /api/articles/no-such")
    resp = client.get("/api/articles/no-such-article")
    data = resp.get_json()
    check("HTTP 404", resp.status_code == 404)
    check("code != 0", data["code"] != 0)


def test_about(client):
    """关于页"""
    print("\n[8] 关于页 GET /api/about")
    resp = client.get("/api/about")
    data = resp.get_json()

    check("HTTP 200", resp.status_code == 200)
    check("code=0", data["code"] == 0)
    check("name 不为空", len(data["data"]["name"]) > 0)
    check("content 不为空", len(data["data"]["content"]) > 0)


# ============================================================================
def run_tests():
    global PASS, FAIL
    PASS = 0
    FAIL = 0

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as c:
        test_list_articles(c)
        test_pagination(c)
        test_category_filter(c)
        test_tag_filter(c)
        test_search(c)
        test_article_detail(c)
        test_article_not_found(c)
        test_about(c)

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
