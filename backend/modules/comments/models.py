"""
评论数据层 — 表创建 + CRUD + 速率限制

独立模块，仅依赖 SQLite。
"""

import sqlite3
import os


def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# 建表
# ---------------------------------------------------------------------------

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS comments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id  TEXT NOT NULL,
    parent_id   INTEGER DEFAULT NULL,
    nickname    TEXT DEFAULT '匿名',
    content     TEXT NOT NULL,
    ip          TEXT NOT NULL,
    is_private  INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_comments_article ON comments(article_id);
CREATE INDEX IF NOT EXISTS idx_comments_ip ON comments(ip);
"""


def init_db(db_path: str):
    """初始化评论表（幂等）。"""
    conn = _get_conn(db_path)
    conn.executescript(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_comment(
    db_path: str,
    article_id: str,
    ip: str,
    content: str,
    nickname: str = "匿名",
    parent_id: int | None = None,
    is_private: bool = False,
) -> dict:
    """新增评论。返回新建评论的 id。"""
    conn = _get_conn(db_path)
    cursor = conn.execute(
        """INSERT INTO comments (article_id, parent_id, nickname, content, ip, is_private)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (article_id, parent_id, nickname, content, ip, int(is_private)),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id}


def delete_comments_for_article(db_path: str, article_id: str) -> int:
    """删除某篇文章的全部评论（含回复，靠 ON DELETE CASCADE）。返回删除条数。"""
    conn = _get_conn(db_path)
    cur = conn.execute("DELETE FROM comments WHERE article_id=?", (article_id,))
    conn.commit()
    n = cur.rowcount
    conn.close()
    return n


def delete_comment(db_path: str, comment_id: int) -> int:
    """删除单条评论（含其全部回复，靠 ON DELETE CASCADE）。返回删除条数。"""
    conn = _get_conn(db_path)
    cur = conn.execute("DELETE FROM comments WHERE id=?", (comment_id,))
    conn.commit()
    n = cur.rowcount
    conn.close()
    return n


def get_comments_by_article(
    db_path: str,
    article_id: str,
    include_private: bool = False,
) -> list[dict]:
    """
    获取某篇文章的所有评论（嵌套树结构）。

    include_private=False → 隐藏 is_private=1 的评论
    include_private=True  → 返回全部
    """
    conn = _get_conn(db_path)

    if include_private:
        rows = conn.execute(
            "SELECT * FROM comments WHERE article_id=? ORDER BY created_at ASC",
            (article_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM comments WHERE article_id=? AND is_private=0 ORDER BY created_at ASC",
            (article_id,),
        ).fetchall()

    conn.close()

    comment_list = [dict(r) for r in rows]
    return _build_tree(comment_list)


def get_comment_count(
    db_path: str,
    article_id: str,
    ip: str | None = None,
    parent_id: int | None = None,
) -> dict:
    """
    统计评论数。
    - 给 article_id + ip + parent_id → 返回特定维度的计数
    - parent_id=None 时统计该文章下该 IP 的顶级评论数
    - parent_id 不为 None 时统计该父评论下该 IP 的回复数
    - ip=None 时统计该文章的总评论数
    """
    conn = _get_conn(db_path)

    if ip is None:
        count = conn.execute(
            "SELECT COUNT(*) as c FROM comments WHERE article_id=?",
            (article_id,),
        ).fetchone()["c"]
        conn.close()
        return {"count": count}

    if parent_id is None:
        count = conn.execute(
            "SELECT COUNT(*) as c FROM comments WHERE article_id=? AND ip=? AND parent_id IS NULL",
            (article_id, ip),
        ).fetchone()["c"]
    else:
        count = conn.execute(
            "SELECT COUNT(*) as c FROM comments WHERE ip=? AND parent_id=?",
            (ip, parent_id),
        ).fetchone()["c"]

    conn.close()
    return {"count": count}


# ---------------------------------------------------------------------------
# 树构建
# ---------------------------------------------------------------------------

def _build_tree(comments: list[dict]) -> list[dict]:
    """将平铺评论列表转为嵌套树，顶级按时间正序。"""
    by_id: dict[int, dict] = {}
    roots: list[dict] = []

    for c in comments:
        c["replies"] = []
        by_id[c["id"]] = c

    for c in comments:
        pid = c.get("parent_id")
        if pid and pid in by_id:
            by_id[pid]["replies"].append(c)
        else:
            roots.append(c)

    return roots
