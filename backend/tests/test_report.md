# article-loader 模块测试报告

> **日期**: 2025-06-19
> **分支**: feature/article-loader
> **被测模块**: `backend/modules/articles/loader.py`

---

## 测试结果

| 指标 | 数值 |
|------|------|
| 通过 | **29** |
| 失败 | **0** |
| 总计 | **29** |
| 通过率 | **100%** |

---

## 测试用例明细

| # | 分类 | 用例 | 结果 |
|---|------|------|------|
| 1 | 基础加载 | load_all() 返回正确文章数（5 文件 → 4 发布 + 1 草稿跳过） | PASS |
| 2 | 基础加载 | articles 为列表类型 | PASS |
| 3 | 基础加载 | filters 包含 categories 和 tags | PASS |
| 4 | 单篇文章 | get_article() 找到存在的文章 | PASS |
| 5 | 单篇文章 | title 字段正确 | PASS |
| 6 | 单篇文章 | category 字段正确 | PASS |
| 7 | 单篇文章 | tags 为数组格式 | PASS |
| 8 | 单篇文章 | content 包含 Markdown 正文 | PASS |
| 9 | 单篇文章 | id 字段存在 | PASS |
| 10 | 单篇文章 | date 字段存在 | PASS |
| 11 | 异常情况 | 不存在的 ID 返回 None | PASS |
| 12 | 异常情况 | 空字符串 ID 返回 None | PASS |
| 13 | 缓存机制 | 连续两次 load_all() 不重复扫描文件 | PASS |
| 14 | 缓存机制 | reload() 强制刷新功能正常 | PASS |
| 15 | Frontmatter | YAML 解析正确 | PASS |
| 16 | Frontmatter | 正文提取正确 | PASS |
| 17 | Frontmatter | 无 frontmatter 时 meta 为空，正文完整保留 | PASS |
| 18 | 草稿跳过 | draft: true 的文章不出现在列表 | PASS |
| 19 | Tag 兼容 | 逗号分隔字符串格式 tags 正确解析为数组 | PASS |
| 20 | 统计信息 | total_articles = 4 | PASS |
| 21 | 统计信息 | categories = 3 (Python + AI + 未分类) | PASS |
| 22 | 统计信息 | tags >= 5 | PASS |
| 23 | 文章导航 | 第一篇 prev = None | PASS |
| 24 | 文章导航 | 最后一篇 next = None | PASS |
| 25 | 文章导航 | 中间文章 prev 不为 None | PASS |
| 26 | 文章导航 | 中间文章 next 不为 None | PASS |
| 27 | 摘要 | 无手动 summary 时自动从正文截取 | PASS |
| 28 | 缺省值 | 无 title 字段时 fallback 为文件名 | PASS |
| 29 | 排序 | 文章按 date 倒序排列 | PASS |

---

## 运行方式

```bash
# 在项目根目录
python backend/tests/test_article_loader.py
```
