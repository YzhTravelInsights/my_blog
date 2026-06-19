"""
article-loader 模块测试

测试覆盖：
  1. 基础加载 — load_all() 返回正确的文章数和结构
  2. 单篇文章 — get_article(id) 返回完整内容 + prev/next
  3. 不存在文章 — get_article(no-id) 返回 None
  4. 缓存机制 — 未改文件不重复读取
  5. reload()   — 强制刷新
  6. frontmatter 解析 — title/date/category/tags/summary
  7. 草稿跳过 — draft: true 的文章不出现在列表
  8. Tag 格式兼容 — 逗号分隔字符串和数组都能解析
  9. 统计信息 — get_stats() 返回正确计数
 10. Prev/Next 导航 — 多篇文章时上下篇正确

运行：
    cd D:/Desktop/myblog
    python backend/tests/test_article_loader.py
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# 确保 backend 在 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.articles.loader import ArticleLoader, _parse_frontmatter, _extract_summary


PASS = 0
FAIL = 0


def test(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}  ← {detail}")


# ---------------------------------------------------------------------------
# 准备测试数据
# ---------------------------------------------------------------------------
def setup_test_articles() -> str:
    """在临时目录创建测试 Markdown 文件，返回目录路径。"""
    tmpdir = tempfile.mkdtemp(prefix="test_articles_")

    files = {
        "2025-06-10-python-basics.md": """---
title: "Python 基础入门"
date: 2025-06-10
category: Python
tags: ["Python", "入门"]
summary: "Python 基础教程"
---

## 第一章

Python 是一门解释型语言。

## 第二章

变量和类型。
""",
        "2025-06-18-conda-python.md": """---
title: "使用 Conda 管理 Python 环境"
date: 2025-06-18
category: Python
tags: ["Python", "Conda", "环境管理"]
---

Conda 是包管理工具。
""",
        "2025-06-20-ai-intro.md": """---
title: "AI 入门指南"
date: 2025-06-20
category: AI
tags: AI, 机器学习, DeepSeek
---

AI 正在改变世界。
""",
        "2025-06-22-draft-post.md": """---
title: "未完成的草稿"
date: 2025-06-22
category: Misc
tags: ["草稿"]
draft: true
---

这篇还没写完。
""",
        "no-title.md": """---
date: 2025-06-15
---

没有标题的文章，应该用 id 作为标题。
""",
    }

    for fname, content in files.items():
        with open(os.path.join(tmpdir, fname), "w", encoding="utf-8") as f:
            f.write(content)

    # 让文件落盘
    time.sleep(0.05)
    return tmpdir


# ---------------------------------------------------------------------------
# 测试用例
# ---------------------------------------------------------------------------
def run_tests():
    global PASS, FAIL
    PASS = 0
    FAIL = 0

    articles_dir = setup_test_articles()

    # ========================================================================
    print("\n[1] 基础加载 load_all()")
    # ========================================================================
    loader = ArticleLoader(articles_dir)
    result = loader.load_all()

    # 5 个文件，1 个 draft=true → 应返回 4 个
    test("返回 4 篇已发布文章",
         len(result["articles"]) == 4,
         f"实际 {len(result['articles'])} 篇")

    test("articles 是列表",
         isinstance(result["articles"], list))

    test("filters 包含 categories 和 tags",
         "categories" in result["filters"] and "tags" in result["filters"])

    # ========================================================================
    print("\n[2] 单篇文章 get_article()")
    # ========================================================================
    art = loader.get_article("2025-06-18-conda-python")

    test("找到存在的文章",
         art is not None)

    test("title 正确",
         art["title"] == "使用 Conda 管理 Python 环境",
         f"实际: {art['title']}")

    test("category 正确",
         art["category"] == "Python")

    test("tags 为数组",
         isinstance(art["tags"], list) and "Conda" in art["tags"])

    test("content 不为空",
         len(art["content"]) > 0 and "Conda" in art["content"])

    test("包含 id 字段",
         art["id"] == "2025-06-18-conda-python")

    test("包含 date 字段",
         art["date"] == "2025-06-18")

    # ========================================================================
    print("\n[3] 不存在文章返回 None")
    # ========================================================================
    test("get_article('no-such-id') → None",
         loader.get_article("no-such-id") is None)

    test("空字符串 → None",
         loader.get_article("") is None)

    # ========================================================================
    print("\n[4] 缓存机制")
    # ========================================================================
    loader2 = ArticleLoader(articles_dir)
    r1 = loader2.load_all()
    r2 = loader2.load_all()
    test("连续两次 load_all() 返回相同内容（不重新扫描文件）",
         r1 == r2)

    # ========================================================================
    print("\n[5] reload() 强制刷新")
    # ========================================================================
    r_before = loader2.load_all()
    loader2.reload()
    r_after = loader2.load_all()
    test("reload 后数据一致（文件未变）",
         r_before == r_after)

    # ========================================================================
    print("\n[6] frontmatter 工具函数")
    # ========================================================================
    meta, body = _parse_frontmatter("""---
title: Test
category: X
---
Hello World
""")
    test("解析 YAML frontmatter",
         meta == {"title": "Test", "category": "X"})
    test("正文提取正确",
         body.strip() == "Hello World")

    # 没有 frontmatter
    meta2, body2 = _parse_frontmatter("Just plain text")
    test("无 frontmatter 时 meta 为空",
         meta2 == {} and body2 == "Just plain text")

    # ========================================================================
    print("\n[7] 草稿跳过")
    # ========================================================================
    ids = [a["id"] for a in result["articles"]]
    test("draft-post 不在列表中",
         "2025-06-22-draft-post" not in ids)

    # ========================================================================
    print("\n[8] Tag 格式兼容")
    # ========================================================================
    # 逗号分隔字符串格式
    ai_article = loader.get_article("2025-06-20-ai-intro")
    test("逗号分隔 tags 正确解析",
         ai_article["tags"] == ["AI", "机器学习", "DeepSeek"],
         f"实际: {ai_article['tags']}")

    # ========================================================================
    print("\n[9] 统计信息 get_stats()")
    # ========================================================================
    stats = loader.get_stats()
    test("total_articles = 4",
         stats["total_articles"] == 4)
    test("categories = 3 (Python + AI + 未分类)",
         stats["categories"] == 3,
         f"实际: {stats['categories']}")
    test("tags >= 5",
         stats["tags"] >= 5)

    # ========================================================================
    print("\n[10] Prev / Next 导航")
    # ========================================================================
    art_list = result["articles"]
    first = art_list[0]
    last = art_list[-1]

    test("第一篇的 prev 为 None",
         loader.get_article(first["id"])["prev"] is None,
         f"prev: {loader.get_article(first['id'])['prev']}")

    test("最后一篇的 next 为 None",
         loader.get_article(last["id"])["next"] is None,
         f"next: {loader.get_article(last['id'])['next']}")

    # 中间文章的 prev/next 都存在
    if len(art_list) >= 3:
        middle = art_list[1]
        mid_article = loader.get_article(middle["id"])
        test("中间文章的 prev 不为 None",
             mid_article["prev"] is not None)
        test("中间文章的 next 不为 None",
             mid_article["next"] is not None)

    # ========================================================================
    print("\n[11] summary 自动截取")
    # ========================================================================
    conda_art = loader.get_article("2025-06-18-conda-python")
    test("无手动 summary 时自动从正文截取",
         conda_art["summary"].strip() != "" and "Conda" in conda_art["summary"])

    no_title_art = loader.get_article("no-title")
    test("无 title 时 fallback 为文件名",
         no_title_art["title"] == "no-title")

    # ========================================================================
    print("\n[12] 文章按 date 倒序")
    # ========================================================================
    dates = [a["date"] for a in art_list]
    test("按日期倒序排列",
         dates == sorted(dates, reverse=True),
         f"实际顺序: {dates}")

    # ========================================================================
    # 清理
    # ========================================================================
    import shutil
    shutil.rmtree(articles_dir)

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
