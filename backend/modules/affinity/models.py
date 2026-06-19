"""
好感度数据层 — SQLite 表 + CRUD

设计：单例表（id=1），记录博主与流萤的互动。
"""

import sqlite3

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS affinity (
    id                  INTEGER PRIMARY KEY CHECK (id = 1),
    level               TEXT NOT NULL DEFAULT 'stranger',
    interaction_count   INTEGER DEFAULT 0,
    first_met_at        TEXT DEFAULT (datetime('now', 'localtime')),
    last_interaction_at TEXT DEFAULT (datetime('now', 'localtime')),
    notes               TEXT DEFAULT ''
);
"""


def init_table(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TABLE)
    # 确保单例行存在
    conn.execute("""
        INSERT OR IGNORE INTO affinity (id, level)
        VALUES (1, 'stranger')
    """)
    conn.commit()
    conn.close()


def get(db_path: str) -> dict | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM affinity WHERE id=1").fetchone()
    conn.close()
    return dict(row) if row else None


def update(db_path: str, **kwargs):
    allowed = {"level", "interaction_count", "last_interaction_at", "notes"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    sets = ", ".join(f"{k}=?" for k in updates)
    vals = list(updates.values())
    conn = sqlite3.connect(db_path)
    conn.execute(f"UPDATE affinity SET {sets} WHERE id=1", vals)
    conn.commit()
    conn.close()
