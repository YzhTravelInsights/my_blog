#!/usr/bin/env python3
"""
博客管理 CLI 工具

命令：
    init-db    初始化 SQLite 数据库表
    reindex    重建 Chroma 向量索引
    list       列出所有文章
    add-article  交互式创建新文章
    stats      显示统计信息
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

COMMANDS = {}


def command(name: str, help_text: str):
    """注册 CLI 命令。"""
    def decorator(fn):
        COMMANDS[name] = {"fn": fn, "help": help_text}
        return fn
    return decorator


# ---------------------------------------------------------------------------
# 命令实现
# ---------------------------------------------------------------------------

@command("init-db", "初始化 SQLite 数据库表")
def cmd_init_db():
    from config import DATABASE_PATH
    from modules.comments.models import init_db
    init_db(DATABASE_PATH)
    print(f"数据库已初始化: {DATABASE_PATH}")


@command("reindex", "重建 Chroma 向量索引")
def cmd_reindex():
    from config import ARTICLES_DIR, CHROMA_PERSIST_DIR
    from modules.articles.loader import ArticleLoader
    from modules.chat.rag import RAGService

    loader = ArticleLoader(ARTICLES_DIR)
    articles = loader.load_all()["articles"]

    rag = RAGService(CHROMA_PERSIST_DIR)
    rag.index_articles(articles, force=True)
    stats = rag.get_stats()
    print(f"索引完成: {stats['indexed_articles']} 篇文章")


@command("list", "列出所有文章")
def cmd_list():
    from config import ARTICLES_DIR
    from modules.articles.loader import ArticleLoader

    loader = ArticleLoader(ARTICLES_DIR)
    articles = loader.load_all()["articles"]
    for i, a in enumerate(articles, 1):
        print(f"{i}. [{a['category']}] {a['title']} ({a['date']})")


@command("stats", "显示统计信息")
def cmd_stats():
    from config import ARTICLES_DIR, CHROMA_PERSIST_DIR, DATABASE_PATH
    from modules.articles.loader import ArticleLoader
    from modules.comments.models import get_comment_count
    from modules.chat.rag import RAGService

    loader = ArticleLoader(ARTICLES_DIR)
    stats = loader.get_stats()

    print("=== 博客统计 ===")
    print(f"文章数: {stats['total_articles']}")
    print(f"分类数: {stats['categories']}")
    print(f"标签数: {stats['tags']}")

    total_comments = 0
    for a in loader.load_all()["articles"]:
        c = get_comment_count(DATABASE_PATH, a["id"])
        total_comments += c["count"]
    print(f"评论数: {total_comments}")

    try:
        rag = RAGService(CHROMA_PERSIST_DIR)
        rag_stats = rag.get_stats()
        print(f"Chroma 已索引: {rag_stats['indexed_articles']}")
    except Exception:
        print("Chroma: 未初始化")


# ---------------------------------------------------------------------------
@command("add-article", "交互式创建新文章")
def cmd_add_article():
    import re
    from datetime import date

    print("=== 新建文章 ===\n")
    title = input("标题: ").strip()
    if not title:
        print("取消")
        return

    category = input("分类 (默认'未分类'): ").strip() or "未分类"
    tags_raw = input("标签 (逗号分隔): ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    summary = input("摘要 (可选，回车跳过): ").strip()

    slug = re.sub(r"[^\w\-]", "-", title.lower()).strip("-")
    today = date.today().isoformat()
    filename = f"{today}-{slug}.md"

    frontmatter = f"---\ntitle: \"{title}\"\ndate: {today}\ncategory: {category}\n"
    if tags:
        frontmatter += f"tags: {tags}\n"
    if summary:
        frontmatter += f"summary: \"{summary}\"\n"
    frontmatter += "---\n\n## \n"

    target = os.path.join(os.path.dirname(__file__), "data", "articles", filename)
    with open(target, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    print(f"\n已创建: {target}")
    print("请编辑该文件补充正文，然后 git add + commit + push 发布。")


# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("可用命令:")
        for name, info in COMMANDS.items():
            print(f"  {name:16s} {info['help']}")
        return

    cmd_name = sys.argv[1]
    if cmd_name not in COMMANDS:
        print(f"未知命令: {cmd_name}")
        print("可用:", ", ".join(COMMANDS.keys()))
        return

    COMMANDS[cmd_name]["fn"]()


if __name__ == "__main__":
    main()
