# 模块测试报告

> **日期**: 2025-06-19
> **分支**: feature/comments

---

## 汇总

| 模块 | 通过 | 失败 | 通过率 |
|------|------|------|--------|
| article-loader | 29 | 0 | 100% |
| article-api | 24 | 0 | 100% |
| comments | **37** | **0** | **100%** |
| **合计** | **90** | **0** | **100%** |

---

## 模块三：comments — 测试明细

### F1 数据库自动建表

| # | 测试点 | 结果 |
|---|--------|------|
| 1 | comments 表已创建 | PASS |

### F2 POST 发表顶级评论

| # | 测试点 | 结果 |
|---|--------|------|
| 2 | HTTP 200 | PASS |
| 3 | code=0 | PASS |
| 4 | 返回新评论 id=1 | PASS |

### F3 POST 发表回复（嵌套）

| # | 测试点 | 结果 |
|---|--------|------|
| 5 | 回复 HTTP 200 | PASS |
| 6 | 回复 id=2（自增） | PASS |

### F4 GET 评论树结构

| # | 测试点 | 结果 |
|---|--------|------|
| 7 | 返回 1 条顶级评论 | PASS |
| 8 | 顶级评论 id=1 | PASS |
| 9 | 顶级评论含 2 条 replies | PASS |
| 10 | 回复 id=2 在 replies 中 | PASS |
| 11 | count 统计正确（3条） | PASS |

### F5 空文章返回空数组

| # | 测试点 | 结果 |
|---|--------|------|
| 12 | 无评论的文章返回 [] | PASS |
| 13 | count=0 | PASS |

### F6 昵称默认值

| # | 测试点 | 结果 |
|---|--------|------|
| 14 | POST 不传 nickname → 默认"匿名" | PASS |
| 15 | GET 返回 nickname="匿名" | PASS |

### F7 IP 速率限制：顶级评论 ≤5

| # | 测试点 | 结果 |
|---|--------|------|
| 16 | 前5条正常通过 | PASS |
| 17 | 第6条 HTTP 429 | PASS |
| 18 | code=4（限额错误码） | PASS |
| 19 | 消息包含"上限" | PASS |

### F8 IP 速率限制：回复 ≤5

| # | 测试点 | 结果 |
|---|--------|------|
| 20 | 第6条回复被拒绝 (429) | PASS |

### F9 不同 IP 计数隔离

| # | 测试点 | 结果 |
|---|--------|------|
| 21 | 1.1.1.1 和 2.2.2.2 各自计数=0，互不影响 | PASS |

### F10 私密评论默认隐藏

| # | 测试点 | 结果 |
|---|--------|------|
| 22 | is_private=True 的评论对普通访客不可见 | PASS |

### F11 私密评论管理员可见

| # | 测试点 | 结果 |
|---|--------|------|
| 23 | admin_key 正确 → 返回私密评论 | PASS |
| 24 | 私密评论内容正确 | PASS |
| 25 | nickname 正确 | PASS |
| 26 | 错误的 admin_key → 不返回私密 | PASS |

### F12 参数校验：缺少 article_id

| # | 测试点 | 结果 |
|---|--------|------|
| 27 | GET 无 article_id → 400 | PASS |
| 28 | POST 无 article_id → 400 | PASS |

### F13 参数校验：content 为空

| # | 测试点 | 结果 |
|---|--------|------|
| 29 | 空字符串 content → 400 | PASS |
| 30 | 消息含"不能为空" | PASS |
| 31 | 纯空格 content → 400 | PASS |

### F14 参数校验：content 超长

| # | 测试点 | 结果 |
|---|--------|------|
| 32 | 5001 字 content → 400 | PASS |

### F15 响应格式

| # | 测试点 | 结果 |
|---|--------|------|
| 33 | 含 code 字段 | PASS |
| 34 | 含 msg 字段 | PASS |
| 35 | 含 data 字段 | PASS |
| 36 | code 是 int 类型 | PASS |

### F16 数据持久化

| # | 测试点 | 结果 |
|---|--------|------|
| 37 | 重复查询 count 一致 | PASS |

---

## 运行方式

```bash
# 模块一：文章加载器
python backend/tests/test_article_loader.py

# 模块二：文章 API
python backend/tests/test_article_api.py

# 模块三：评论系统
python backend/tests/test_comments.py

# 启动 Flask 手动测试
python backend/app.py
curl http://127.0.0.1:5000/api/comments?article_id=2025-06-18-conda-python
curl -X POST http://127.0.0.1:5000/api/comments \
  -H "Content-Type: application/json" \
  -d '{"article_id":"2025-06-18-conda-python","nickname":"test","content":"hello"}'
```
