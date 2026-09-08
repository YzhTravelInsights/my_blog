---
title: "我的 Git 工作流：分支、提交信息与回滚"
date: 2026-04-12
category: 工具
tags: ["Git", "工作流", "版本管理"]
summary: "分享日常开发的 Git 使用习惯，包括分支策略、提交信息规范与安全的回滚姿势。"
---

## 分支策略

### 简单够用

个人项目不用太复杂：`main` 是稳定分支，功能都在 `feature/xxx` 分支上开发，合完就删。

### 命名习惯

- 功能：`feature/3d-avatar`
- 修复：`fix/login-bug`
- 重构：`refactor/chat-module`

## 提交信息规范

写清楚「为什么」，而不是「改了啥」：

```
feat(chat): 新增 RAG 引用展示

访客提问时可以直观看到引用了哪篇文章。
```

## 安全回滚

回滚前先看清历史，确认哪些提交需要撤销：

```bash
git log --oneline -10
git revert <commit-id>
```

`revert` 会生成一条新提交，保留历史，比 `reset` 更安全。

## 小结

工作流是习惯问题，不追求最酷，追求**可回滚、可追溯**。
