# 模块测试报告

> **日期**: 2025-06-19

---

## 汇总

| 模块 | 通过 | 失败 | 通过率 |
|------|------|------|--------|
| article-loader | 29 | 0 | 100% |
| article-api | 24 | 0 | 100% |
| comments | 37 | 0 | 100% |
| chat-core | 32 | 0 | 100% |
| chat-rag | **23** | **0** | **100%** |
| **合计** | **145** | **0** | **100%** |

---

## 模块五：chat-rag — 测试明细

### R1 RAGService 初始化

| # | 测试点 | 结果 |
|---|--------|------|
| 1 | RAGService 创建成功 | PASS |
| 2 | persist_dir 正确 | PASS |

### R2 首次索引

| # | 测试点 | 结果 |
|---|--------|------|
| 3 | 索引 3 篇文章 | PASS |

### R3 跳过已索引

| # | 测试点 | 结果 |
|---|--------|------|
| 4 | 二次索引不重复调用 embedding | PASS |
| 5 | 索引数仍然为 3 | PASS |

### R4 清空重建

| # | 测试点 | 结果 |
|---|--------|------|
| 6 | force=True 重新索引 3 篇 | PASS |

### R5 检索相关文章

| # | 测试点 | 结果 |
|---|--------|------|
| 7 | search() 返回结果 | PASS |
| 8 | 结果含 article_id | PASS |
| 9 | 结果含 title | PASS |
| 10 | 结果含 relevance | PASS |

### R6 空索引

| # | 测试点 | 结果 |
|---|--------|------|
| 11 | 空索引 search() 返回 [] | PASS |

### R7 上下文构建

| # | 测试点 | 结果 |
|---|--------|------|
| 12 | build_context() 含'参考资料'标题 | PASS |
| 13 | build_context() 含文章标题 | PASS |
| 14 | 空索引 build_context() 返回 "" | PASS |

### R8 统计

| # | 测试点 | 结果 |
|---|--------|------|
| 15 | indexed_articles = 3 | PASS |
| 16 | persist_dir 正确 | PASS |

### R9 现有 API 不受影响

| # | 测试点 | 结果 |
|---|--------|------|
| 17 | 文章列表 200 | PASS |
| 18 | 文章列表 code=0 | PASS |
| 19 | 文章详情 200 | PASS |
| 20 | 关于页 200 | PASS |

### R10 chat 端点返回 sources

| # | 测试点 | 结果 |
|---|--------|------|
| 21 | HTTP 200 | PASS |
| 22 | reply 不为空 | PASS |
| 23 | 含 sources 字段 | PASS |

---

## 运行方式

```bash
python backend/tests/test_article_loader.py
python backend/tests/test_article_api.py
python backend/tests/test_comments.py
python backend/tests/test_chat_core.py
python backend/tests/test_chat_rag.py

# 重建索引
python backend/manage.py reindex
```
