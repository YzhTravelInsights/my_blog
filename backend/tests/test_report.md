# 模块测试报告

> **日期**: 2025-06-19

---

## 汇总

| 模块 | 通过 | 失败 | 通过率 |
|------|------|------|--------|
| article-loader | 29 | 0 | 100% |
| article-api | 24 | 0 | 100% |
| comments | 37 | 0 | 100% |
| chat-core | **32** | **0** | **100%** |
| **合计** | **122** | **0** | **100%** |

---

## 模块四：chat-core — 测试明细

### C1 prompt_builder 基础提示词

| # | 测试点 | 结果 |
|---|--------|------|
| 1 | 含'流萤'角色名 | PASS |
| 2 | 含'开拓者'称呼 | PASS |
| 3 | 含'公共助手'模式提示 | PASS |
| 4 | owner 模式可注入 RAG 上下文 | PASS |
| 5 | owner 模式可注入好感度 | PASS |

### C2 POST /api/chat 正常对话

| # | 测试点 | 结果 |
|---|--------|------|
| 6 | HTTP 200 | PASS |
| 7 | code=0 | PASS |
| 8 | reply 不为空 | PASS |
| 9 | mode=public | PASS |
| 10 | emotion 字段存在 | PASS |

### C3 空消息校验

| # | 测试点 | 结果 |
|---|--------|------|
| 11 | 空字符串 → 400 | PASS |
| 12 | 纯空格 → 400 | PASS |
| 13 | 无 message 字段 → 400 | PASS |

### C4 超长消息校验

| # | 测试点 | 结果 |
|---|--------|------|
| 14 | 2001 字 → 400 | PASS |
| 15 | 2000 字 → 通过 | PASS |

### C5 guest 截断历史

| # | 测试点 | 结果 |
|---|--------|------|
| 16 | guest 模式 15 条历史正常处理 | PASS |

### C6 owner 历史不截断

| # | 测试点 | 结果 |
|---|--------|------|
| 17 | owner 模式 15 条历史正常处理 | PASS |

### C7 history 格式清洗

| # | 测试点 | 结果 |
|---|--------|------|
| 18 | 含非法元素的 history → 清洗后 200 | PASS |

### C8 故障回退

| # | 测试点 | 结果 |
|---|--------|------|
| 19 | 故障时 HTTP 200（优雅降级） | PASS |
| 20 | 降级回复含'火萤' | PASS |
| 21 | fallback=True 标记 | PASS |

### C9 故障日志

| # | 测试点 | 结果 |
|---|--------|------|
| 22 | api_error.log 已生成 | PASS |

### C10 响应格式

| # | 测试点 | 结果 |
|---|--------|------|
| 23 | 含 code | PASS |
| 24 | 含 msg | PASS |
| 25 | 含 data | PASS |
| 26 | data.reply | PASS |
| 27 | data.emotion | PASS |

### C11 emotion 检测

| # | 测试点 | 结果 |
|---|--------|------|
| 28 | '哈哈' → happy | PASS |
| 29 | '嘿嘿' → happy | PASS |
| 30 | '唔' → thinking | PASS |
| 31 | '没关系' → caring | PASS |
| 32 | 普通文本 → normal | PASS |

---

## 运行方式

```bash
python backend/tests/test_article_loader.py
python backend/tests/test_article_api.py
python backend/tests/test_comments.py
python backend/tests/test_chat_core.py

# 真实对话需配置 .env 中的 DEEPSEEK_API_KEY
python backend/app.py
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好流萤","session_id":"test","history":[]}'
```
