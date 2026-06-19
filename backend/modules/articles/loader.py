"""
文章加载器 — ArticleLoader

纯 Python 模块，零外部依赖（除 PyYAML）。
读取 data/articles/*.md，解析 frontmatter + Markdown 正文，
构建内存索引缓存。不依赖 Flask、不依赖数据库。

使用：
    from modules.articles.loader import ArticleLoader
    loader = ArticleLoader("backend/data/articles")
    all_articles = loader.load_all()
    one_article  = loader.get_article("2025-06-18-conda-python")
"""

import os
import re
import glob
import time
from datetime import datetime
from typing import Optional

import yaml


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """分离 frontmatter (YAML) 和 Markdown 正文。"""
    # 匹配开头的 ---\n...\n---
    pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    match = pattern.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    body = text[match.end():]
    return meta, body


def _extract_summary(body: str, meta: dict, max_chars: int = 200) -> str:
    """获取摘要：优先 meta.summary，否则截取正文前 max_chars 字。"""
    if meta.get("summary"):
        return meta["summary"]
    # 去掉 Markdown 标记后截取纯文本
    clean = re.sub(r"[#*>`\[\]()!_~|]", "", body).replace("\n", " ").strip()
    if len(clean) <= max_chars:
        return clean
    return clean[:max_chars].rsplit(" ", 1)[0] + "…"


def _generate_id(filename: str) -> str:
    """从文件名生成文章 ID：去掉 .md 后缀和路径。"""
    return os.path.splitext(os.path.basename(filename))[0]


# ---------------------------------------------------------------------------
# 加载器
# ---------------------------------------------------------------------------

class ArticleLoader:
    """
    扫描 Markdown 文章目录，解析并缓存。

    缓存策略：
        - 记录每个文件的 mtime
        - load_all() 时检查是否有文件变更，有则刷新
        - reload() 强制刷新
    """

    def __init__(self, articles_dir: str, about_file: str | None = None):
        self._dir = articles_dir
        self._about_file = about_file
        self._articles: list[dict] = []
        self._by_id: dict[str, dict] = {}
        self._categories: list[str] = []
        self._tags: list[str] = []
        self._file_mtimes: dict[str, float] = {}
        self._loaded_at: float = 0.0

    # ---- 公开接口 ----

    def load_all(self) -> dict:
        """
        加载全部已发布文章。
        返回:
            {
                "articles": [ 按 date 倒序排列的文章列表 ],
                "filters": {
                    "categories": [按拼音/字母排序],
                    "tags": [按拼音/字母排序]
                }
            }
        """
        if self._needs_refresh():
            self._do_load()
        return {
            "articles": self._articles,
            "filters": {
                "categories": sorted(self._categories),
                "tags": sorted(self._tags),
            },
        }

    def get_article(self, article_id: str) -> Optional[dict]:
        """获取单篇文章详情（含 prev / next）。"""
        if self._needs_refresh():
            self._do_load()
        article = self._by_id.get(article_id)
        if not article:
            return None
        # 深拷贝避免外部修改污染缓存
        result = dict(article)
        result["prev"] = self._get_adjacent(article_id, -1)
        result["next"] = self._get_adjacent(article_id, 1)
        return result

    def reload(self):
        """强制刷新缓存。"""
        self._do_load()

    def get_stats(self) -> dict:
        """统计信息。"""
        if self._needs_refresh():
            self._do_load()
        return {
            "total_articles": len(self._articles),
            "categories": len(self._categories),
            "tags": len(self._tags),
        }

    def get_about(self) -> dict:
        """
        加载关于页。
        从 data/about.md 读取 frontmatter + Markdown，无缓存（改动少）。
        """
        if not self._about_file or not os.path.isfile(self._about_file):
            return {"name": "", "avatar": "", "content": ""}

        with open(self._about_file, "r", encoding="utf-8") as f:
            raw = f.read()

        meta, body = _parse_frontmatter(raw)
        return {
            "name": meta.get("name", ""),
            "avatar": meta.get("avatar", ""),
            "content": body.strip(),
        }

    # ---- 内部实现 ----

    def _needs_refresh(self) -> bool:
        """检查是否有文件变更。"""
        if not self._articles:
            return True
        current_files = set(glob.glob(os.path.join(self._dir, "*.md")))
        known_files = set(self._file_mtimes.keys())
        if current_files != known_files:
            return True
        for fpath in current_files:
            if os.path.getmtime(fpath) != self._file_mtimes.get(fpath, 0):
                return True
        return False

    def _do_load(self):
        """完整加载流程。"""
        files = sorted(glob.glob(os.path.join(self._dir, "*.md")))

        articles = []
        by_id: dict[str, dict] = {}
        categories: set[str] = set()
        tags: set[str] = set()
        file_mtimes: dict[str, float] = {}

        for fpath in files:
            mtime = os.path.getmtime(fpath)
            file_mtimes[fpath] = mtime

            with open(fpath, "r", encoding="utf-8") as f:
                raw = f.read()

            meta, body = _parse_frontmatter(raw)

            # 跳过草稿
            if meta.get("draft"):
                continue

            article_id = _generate_id(fpath)

            # tag 可能在 YAML 里写成逗号分隔字符串，统一处理
            raw_tags = meta.get("tags", [])
            if isinstance(raw_tags, str):
                tag_list = [t.strip() for t in raw_tags.split(",") if t.strip()]
            elif isinstance(raw_tags, list):
                tag_list = [t.strip() for t in raw_tags if t and isinstance(t, str)]
            else:
                tag_list = []

            category = meta.get("category", "未分类")
            categories.add(category)
            for t in tag_list:
                tags.add(t)

            article = {
                "id": article_id,
                "title": meta.get("title", article_id),
                "date": str(meta.get("date", "")),
                "category": category,
                "tags": tag_list,
                "summary": _extract_summary(body, meta),
                "content": body,
            }
            articles.append(article)
            by_id[article_id] = article

        # 按 date 倒序
        articles.sort(key=lambda a: str(a.get("date", "")), reverse=True)

        self._articles = articles
        self._by_id = by_id
        self._categories = list(categories)
        self._tags = list(tags)
        self._file_mtimes = file_mtimes
        self._loaded_at = time.time()

    def _get_adjacent(self, article_id: str, offset: int) -> Optional[dict]:
        """获取前一/后一篇文章（仅 id + title）。"""
        ids = [a["id"] for a in self._articles]
        try:
            idx = ids.index(article_id)
            neighbor_idx = idx + offset
            if 0 <= neighbor_idx < len(ids):
                neighbor = self._articles[neighbor_idx]
                return {"id": neighbor["id"], "title": neighbor["title"]}
        except ValueError:
            pass
        return None
