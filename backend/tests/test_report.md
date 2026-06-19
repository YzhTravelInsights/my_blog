# 模块测试报告

> **日期**: 2025-06-19

---

## 汇总

| 模块 | 通过 | 失败 | 通过率 |
|------|------|------|--------|
| article-loader | 29 | 0 | 100% |
| article-api | 24 | 0 | 100% |
| comments | 37 | 0 | 100% |
| chat-core | 36 | 0 | 100% |
| chat-rag | 23 | 0 | 100% |
| chat-owner | 25 | 0 | 100% |
| frontend-core | **30** | **0** | **100%** |
| **合计** | **204** | **0** | **100%** |

---

## 模块七：frontend-core — 测试明细

### F1 API 层：getArticles

| # | 测试点 | 结果 |
|---|--------|------|
| 1 | 构建正确的 URL（无参数）含 page & page_size | PASS |
| 2 | 含 category 参数 | PASS |
| 3 | 含 search 参数 | PASS |
| 4 | 含 tag 参数 | PASS |
| 5 | 返回解析后的 JSON | PASS |

### F2 API 层：getArticle / getAbout

| # | 测试点 | 结果 |
|---|--------|------|
| 6 | getArticle 构建带 ID 的 URL | PASS |
| 7 | getArticle 返回文章详情 | PASS |
| 8 | getAbout 调用 /api/about | PASS |

### F3 API 层：getComments / postComment

| # | 测试点 | 结果 |
|---|--------|------|
| 9 | getComments 构建正确的 URL | PASS |
| 10 | getComments 返回评论数据 | PASS |
| 11 | postComment 发送 POST 含正确 body | PASS |
| 12 | postComment 私密评论发送 is_private=true | PASS |
| 13 | postComment 默认昵称逻辑 | PASS |

### F4 Vue Router

| # | 测试点 | 结果 |
|---|--------|------|
| 14 | 有 3 条路由 | PASS |
| 15 | / 映射到 Home | PASS |
| 16 | /article/:id 映射到 Article（含 params） | PASS |
| 17 | /about 映射到 About | PASS |
| 18 | 使用 hash 模式 | PASS |

### F5 NavBar 组件

| # | 测试点 | 结果 |
|---|--------|------|
| 19 | 渲染博客标题 "My Blog" | PASS |
| 20 | 包含"首页"链接 | PASS |
| 21 | 包含"关于"链接 | PASS |

### F6 ArticleCard 组件

| # | 测试点 | 结果 |
|---|--------|------|
| 22 | 渲染文章标题 | PASS |
| 23 | 渲染摘要 | PASS |
| 24 | 渲染分类标签 | PASS |
| 25 | 渲染 Tag 列表 | PASS |
| 26 | 包含文章链接（含 article id） | PASS |

### F7 TagFilter 组件

| # | 测试点 | 结果 |
|---|--------|------|
| 27 | 渲染所有分类 + "全部" | PASS |
| 28 | 渲染所有标签 | PASS |
| 29 | 点击分类触发 select-category 事件 | PASS |
| 30 | activeCategory 高亮样式 | PASS |

---

## 运行方式

```bash
# 后端测试
python backend/tests/test_article_loader.py
python backend/tests/test_article_api.py
python backend/tests/test_comments.py
python backend/tests/test_chat_core.py
python backend/tests/test_chat_rag.py
python backend/tests/test_chat_owner.py

# 前端测试
cd frontend && npx vitest run

# 前端构建验证
cd frontend && npm run build
```
