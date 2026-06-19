"""
人格演化数据层 — SQLite 印象表
"""

import sqlite3

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS impressions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    content     TEXT NOT NULL,
    weight      REAL DEFAULT 1.0,
    session_id  TEXT,
    created_at  TEXT DEFAULT (datetime('now', 'localtime'))
);
"""


def init_table(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TABLE)
    conn.commit()
    conn.close()


def add(db_path: str, content: str, weight: float, session_id: str) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.execute(
        "INSERT INTO impressions (content, weight, session_id) VALUES (?, ?, ?)",
        (content, weight, session_id),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_recent(db_path: str, limit: int = 10) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM impressions WHERE weight >= 0.1 ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def decay_weights(db_path: str, factor: float = 0.95):
    """所有印象权重乘以衰减因子。"""
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE impressions SET weight = weight * ?", (factor,))
    conn.commit()
    conn.close()
