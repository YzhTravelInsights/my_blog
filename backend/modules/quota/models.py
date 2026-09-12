"""
用量与额度数据层 — SQLite 表 + CRUD

按「日期 + 身份」聚合，身份（scope）取值：
    guest —— 访客（公开 /api/chat），计入每日限额
    owner —— 博主本人（/api/chat/owner），不受限额约束，仅统计便于查看花了多少

一天一行，累计 requests / tokens / 花费（人民币）。
"""

import sqlite3

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS usage_daily (
    day               TEXT    NOT NULL,
    scope             TEXT    NOT NULL,
    requests          INTEGER NOT NULL DEFAULT 0,
    prompt_tokens     INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    cache_hit_tokens  INTEGER NOT NULL DEFAULT 0,
    cache_miss_tokens INTEGER NOT NULL DEFAULT 0,
    cost_cny          REAL    NOT NULL DEFAULT 0,
    updated_at        TEXT    DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (day, scope)
);
"""

_UPSERT = """
INSERT INTO usage_daily (
    day, scope, requests, prompt_tokens, completion_tokens,
    cache_hit_tokens, cache_miss_tokens, cost_cny, updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
ON CONFLICT(day, scope) DO UPDATE SET
    requests          = requests          + excluded.requests,
    prompt_tokens     = prompt_tokens     + excluded.prompt_tokens,
    completion_tokens = completion_tokens + excluded.completion_tokens,
    cache_hit_tokens  = cache_hit_tokens  + excluded.cache_hit_tokens,
    cache_miss_tokens = cache_miss_tokens + excluded.cache_miss_tokens,
    cost_cny          = cost_cny          + excluded.cost_cny,
    updated_at        = datetime('now', 'localtime');
"""


def init_table(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TABLE)
    conn.commit()
    conn.close()


def get(db_path: str, day: str, scope: str) -> dict | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM usage_daily WHERE day=? AND scope=?", (day, scope)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_usage(
    db_path: str,
    day: str,
    scope: str,
    requests: int = 0,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    cache_hit_tokens: int = 0,
    cache_miss_tokens: int = 0,
    cost_cny: float = 0.0,
):
    """累加一条用量（同一天同一身份自动合并）。"""
    conn = sqlite3.connect(db_path)
    conn.execute(
        _UPSERT,
        (
            day, scope, int(requests), int(prompt_tokens), int(completion_tokens),
            int(cache_hit_tokens), int(cache_miss_tokens), float(cost_cny),
        ),
    )
    conn.commit()
    conn.close()


def recent(db_path: str, limit: int = 14) -> list[dict]:
    """最近若干条记录（按日期倒序），供主人查看历史花费。"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM usage_daily ORDER BY day DESC, scope ASC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
