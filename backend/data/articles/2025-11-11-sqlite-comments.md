---
title: "用 SQLite 做一个支持嵌套回复的评论系统"
date: 2025-11-11
category: 后端
tags: ["SQLite", "数据库", "评论系统"]
summary: "不引入 MySQL，用 SQLite 实现文章评论与嵌套回复，含表结构设计与查询优化。"
---

## 为什么选 SQLite

个人博客流量不大，SQLite 单文件、零运维、开箱即用，完全够。

## 表设计

```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT NOT NULL,
    parent_id INTEGER DEFAULT NULL,
    nickname TEXT NOT NULL,
    content TEXT NOT NULL,
    is_private INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);
```

`parent_id` 为 NULL 表示顶层评论，否则指向父评论。

## 查询嵌套

一次查全再在内存里组树，比递归查询简单：

```python
comments = db.fetch_all()
tree = build_tree(comments)  # 按 parent_id 组装
```

## 私密评论

`is_private` 标记仅博主可见，查询时按当前身份过滤。

## 小结

SQLite 很轻，但不代表设计可以随便。**合理的表结构 + 应用层组装**，就能撑起一个不错的评论系统。
