# 个人博客 + AI 虚拟人物「流萤」

一个个人技术博客网站，核心特色是在页面右下角嵌入 AI 虚拟人物「流萤」——她来自《崩坏：星穹铁道》，能基于博客内容与访客进行智能对话，并对博主本人生成持续演化的人格。

**所有权模型**：博主是内容与 AI 人格的唯一所有者。文章通过本地 Markdown + Git 发布；AI 人格通过「主人模式」专属演化；访客只能读取静态内容、进行基础对话。

---

## 功能特性

| 模块 | 说明 |
|------|------|
| 📝 文章展示 | Markdown + YAML frontmatter 渲染，列表 / 详情 / 分类 / 标签筛选 |
| 💬 AI 公开对话 | 访客与「萤宝」聊天，基于 DeepSeek，可引用博客文章 |
| 📚 RAG 知识库 | 文章向量化（本地 embedding 模型）+ ChromaDB 检索，回答引用博客内容；新增/修改文章自动增量更新索引 |
| 👑 主人模式 | 仅博主可触发（Bearer Token），启用好感度 / 记忆 / 人格全功能 |
| 💖 好感度系统 | 互动次数自动升级：陌生人 → 熟人 → 挚友 → 羁绊 |
| 🧠 长期记忆 | Chroma 向量存储 + DeepSeek 判断重要性，最多 500 条 |
| 🎭 人格演化 | 每次主人对话生成印象，权重随时间衰减，影响后续对话 |
| 💸 每日限额 | 访客聊天按天计费封顶（默认 1 元/天），超了自动回绝；博主本人不受限 |
| 🗣 评论系统 | 文章评论、嵌套回复（SQLite） |
| 🧚 3D 虚拟人 | 右下角 Three.js 渲染 GLB 模型，程序化呼吸 / 摇摆 / 浮动 / 情绪动画 + 问候气泡 |
| 👤 主人专属功能 | 独立私聊页 `/chat`、管理后台 `/admin`、在线发布文章 `/write`；URL 令牌自动登录，访客完全看不到入口、体验不变 |

---

## 技术栈

**后端**（`backend/`）
- Python 3 · Flask 3 · Flask-CORS
- ChromaDB（嵌入式向量数据库）
- sentence-transformers（本地 embedding：`all-MiniLM-L6-v2`，384 维，离线运行）
- OpenAI SDK（调用 DeepSeek Chat API）
- SQLite（评论 / 好感度 / 人格）

**前端**（`frontend/`）
- Vue 3（`<script setup>`）· Vue Router（hash 路由）
- Vite 6 · Tailwind CSS 4
- Three.js（3D 虚拟人 GLB 渲染 + 程序化动画）
- Vitest + Vue Test Utils

---

## 目录结构

```
myblog/
├── backend/
│   ├── app.py                  # Flask 应用工厂（注册全部模块）
│   ├── config.py               # 全局路径配置
│   ├── manage.py               # 博客管理 CLI（init-db / reindex / list / add-article / stats）
│   ├── requirements.txt
│   ├── .env.example            # 环境变量模板
│   ├── data/
│   │   ├── articles/           # Markdown 文章（frontmatter + 正文）
│   │   ├── about.md            # 关于页内容
│   │   ├── blog.db             # SQLite 数据库
│   │   └── chroma/             # Chroma 向量索引（文章 + 记忆）
│   ├── models/                 # 本地 embedding 模型缓存（首次启动下载）
│   ├── modules/
│   │   ├── articles/           # 文章加载 + API
│   │   ├── comments/           # 评论系统
│   │   ├── chat/               # AI 对话（DeepSeek + RAG + 三层拟人化编排）
│   │   ├── affinity/           # 好感度
│   │   ├── memory/             # 长期记忆
│   │   ├── personality/        # 人格演化
│   │   ├── quota/              # 每日 API 花费限额（访客限额，主人豁免）
│   │   ├── admin/              # 管理后台 API（summary / 发布文章）
│   │   ├── auth.py             # 主人鉴权中间件
│   │   ├── security.py         # DeepSeek API Key 加密/解密（DPAPI，进程内缓存）
│   │   ├── kb_watcher.py       # 知识库自动更新线程（新增/修改文章自动入索引）
│   │   └── logging_config.py   # 日志配置（终端 INFO + logs/app.log 关键/报错）
│   ├── logs/                   # 运行日志（app.log 滚动、api_error.log）
│   └── tests/                  # pytest 测试
└── frontend/
    ├── vite.config.js          # 开发端口 3000，代理 /api → 127.0.0.1:5000
    ├── src/
    │   ├── views/              # Home / Article / About / Gallery / OwnerChat / Admin / Write
    │   ├── components/         # NavBar、ArticleCard、ChatWidget、Live2DCharacter 等
    │   ├── api/                # 后端 API 客户端
    │   └── router/
    └── public/
        ├── firefly-avatar.png          # 静态头像（备选）
        └── live2d/firefly/firefly.glb  # 3D 虚拟人模型
```

---

## 快速开始

### 1. 启动后端

```bash
cd backend

# 安装依赖（首次，含 torch / sentence-transformers，体积较大）
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
#   编辑 .env：填入 DEEPSEEK_API_KEY_ENC（加密密文）、OWNER_SECRET（详见下方配置）
#   生成密文：python -c "from modules.security import encrypt_secret; print(encrypt_secret('sk-你的key'))"

# 启动
python app.py          # 监听 http://127.0.0.1:5000
```

> **首次启动**会自动下载本地 embedding 模型（约 80MB，存于 `backend/models/`），此后离线运行。
> 国内网络访问 HuggingFace 超时已通过 `TRANSFORMERS_OFFLINE=1` 解决（见 `modules/chat/rag.py`）。
> 模型不可用或下载失败时，RAG 会优雅降级，聊天功能不受影响。

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev           # 监听 http://localhost:3000，自动代理 /api 到后端
```

打开浏览器访问 `http://localhost:3000` 即可。页面右下角会出现「萤宝」3D 虚拟人，点击即可聊天。

---

## 环境变量配置（`backend/.env`）

| 变量 | 必填 | 说明 |
|------|------|------|
| `DEEPSEEK_API_KEY_ENC` | ✅ | DeepSeek API Key 的**加密密文**（Windows DPAPI 加密，明文不落盘） |
| `DEEPSEEK_BASE_URL` | 可选 | DeepSeek API 地址，默认 `https://api.deepseek.com` |
| `OWNER_SECRET` | 主人模式必填 | 主人模式鉴权密钥，通过 `Authorization: Bearer <OWNER_SECRET>` 调用 `/api/chat/owner` |
| `QUOTA_DAILY_CNY` | 可选 | 访客每天最多花多少钱（元），默认 `1.0`；`0` 或负数 = 不限制。主人不受此限制 |
| `DEEPSEEK_PRICE_INPUT_MISS` | 可选 | 输入单价（元/百万 token，缓存未命中），默认 `2.0` |
| `DEEPSEEK_PRICE_INPUT_HIT` | 可选 | 输入单价（元/百万 token，缓存命中），默认 `0.5` |
| `DEEPSEEK_PRICE_OUTPUT` | 可选 | 输出单价（元/百万 token），默认 `8.0` |
| `FLASK_ENV` | 可选 | `development` / `production` |

> **API Key 加密存储**：`backend/.env` 只保存 `DEEPSEEK_API_KEY_ENC`（base64 密文），
> 由 `modules/security.py` 在**进程内解密一次并缓存**，明文不落盘 / 不进 Git / 不打日志。
> 生成密文：`python -c "from modules.security import encrypt_secret; print(encrypt_secret('sk-你的key'))"`
> （加密绑定当前 Windows 用户，换机器/用户需重新生成）。密钥只存在于后端，不出现在前端代码中。

---

## 每日 API 花费限额

访客聊天会真实消耗 DeepSeek 额度，所以默认**按天封顶 1 元**；博主本人走主人模式，**完全不受限**。

- **计价**：每次调用记录 `usage` 里的 token 数，按「缓存未命中输入 / 缓存命中输入 / 输出」三档单价折算人民币，
  写入 SQLite 的 `usage_daily` 表（按「日期 + 身份」聚合，一天一行）。
- **拦截点**：额度用尽后后端**不再调用 DeepSeek**，直接返回一句友好提示
  （`fallback: true, quota_exhausted: true`），成本为零。
- **主人豁免**：`/api/chat/owner`（以及主人模式下的记忆/人格判断）照样记账，方便你知道自己花了多少，但**永不拦截**。
- **调整**：改 `.env` 的 `QUOTA_DAILY_CNY` 即可，设 `0` 关闭限额。
- **查看**：管理后台 `GET /api/admin/summary` → `system.quota`，含今日访客花费、剩余额度、主人花费与最近 14 天记录。

> 单价默认取 DeepSeek `deepseek-chat` 官方价（输入 2 元/百万、缓存命中 0.5 元/百万、输出 8 元/百万）。
> 换模型或官方调价时用 `DEEPSEEK_PRICE_*` 覆盖即可，不必改代码。

---

## 内容管理

文章是带 YAML frontmatter 的 Markdown 文件，存放在 `backend/data/articles/`：

```markdown
---
title: "使用 Conda 管理 Python 环境"
date: 2025-06-18
category: Python
tags: ["Python", "Conda", "环境管理"]
summary: "本文介绍如何使用 Conda 创建和管理 Python 虚拟环境。"
---

## 引言
Conda 是一个强大的包管理和环境管理工具……
```

写 Markdown 后**无需手动重建索引**：后端常驻时，KB Watcher 自动检测到新增/修改文章
（文件「写稳 60 秒」后）增量入向量库，终端/日志打印「KB 已自动更新」清单。

```bash
cd backend
python manage.py add-article     # 交互式创建文章模板
python manage.py reindex         # 手动全量重建 Chroma 索引（换新机器或彻底重建时）
python manage.py list            # 列出所有文章
python manage.py stats           # 显示博客统计（文章 / 评论 / 索引数）
python manage.py init-db         # 初始化数据库表
```

发布流程：写 Markdown → `git add && git commit && git push`。

---

## 主人特殊访问方式（部署到云端后）

主人专属功能（私聊 `/chat`、管理后台 `/admin`、发布文章 `/write`）用 **令牌**识别你本人。
导航栏**始终可见**一个「👑 主人」按钮，访客点进去只有输钥匙的框，**看不到也进不去**任何主人功能；聊天 / 评论等原有功能完全不变。

**使用方法一（首选）**：点右上角「👑 主人」→ 输入 `OWNER_SECRET` →「进入」。
登录成功后，**💬 私聊 / ⚙️ 管理 / ✍️ 发布 三个标签直接出现在导航栏**（与「首页 / 图库 / 关于」并排），随时一点直达。

**使用方法二（带令牌访问）**：在任意页面地址后拼 `?owner_token=<OWNER_SECRET>`（即后端 `.env` 里的 `OWNER_SECRET`）：

```text
https://你的域名/#/chat?owner_token=你的密钥      # 主人私聊
https://你的域名/#/admin?owner_token=你的密钥     # 管理后台
https://你的域名/#/write?owner_token=你的密钥     # 发布文章
```

- 首次登录后令牌写入浏览器 localStorage（`blog_owner_token`）并自动从地址栏清除；**只输一次，之后打开任何页面都是登录态**，切换页面不丢。
- 登录后右上角按钮变「👑 主人·已登录」并带**萤火绿小点**提示状态；点开可「退出登录」，退出后三个标签随之消失，恢复访客样子。
- 令牌在 hash 路由的 `#` 片段内，**不会进入服务器访问日志 / Referer**；只存你本机浏览器，不进前端代码 / git。
- 三层防护：① 前端按令牌隐藏标签；② 后端 `/api/admin/*`、`/api/chat/owner` 全部 `Bearer OWNER_SECRET` 鉴权（401 拦截）；③ 令牌不落盘、不进 Git。

---

## API 一览

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/api/articles` | 无 | 文章列表（支持分类 / 标签筛选） |
| GET | `/api/articles/<id>` | 无 | 文章详情 |
| GET | `/api/about` | 无 | 关于页内容 |
| GET / POST | `/api/comments` | 无 | 评论列表 / 发表评论 |
| POST | `/api/chat` | 无 | 公开聊天（guest，截断历史，固定「陌生人」好感度；超出每日额度时返回 `quota_exhausted`） |
| POST | `/api/chat/owner` | Bearer `OWNER_SECRET` | 主人聊天（启用好感度 / 记忆 / 人格全链路，并写入状态） |
| GET | `/api/admin/summary` | Bearer `OWNER_SECRET` | 管理后台汇总：内容统计（含分类/标签计数、最近文章/评论/印象）+ 系统运行信息 |
| POST | `/api/admin/article` | Bearer `OWNER_SECRET` | 主人发布文章：写 md 文件并立即入知识库（标题/分类/标签/正文） |
| DELETE | `/api/admin/article/<id>` | Bearer `OWNER_SECRET` | 主人删除文章：删文件 + 清知识库索引 + 删该文章全部评论 |
| DELETE | `/api/admin/comment/<id>` | Bearer `OWNER_SECRET` | 主人删除单条评论（含其回复，CASCADE） |
| GET | `/` | 无 | 健康检查 `{message, version}` |

响应统一格式：`{ code: 0, msg: "ok", data: ... }`，`code !== 0` 为失败。

**对话上下文流水线**（主人模式）：RAG 检索 → 好感度提示词 → 长期记忆召回 → 人格印象 → 组装 system prompt → DeepSeek 生成 → 情绪检测 → 好感度/记忆/人格状态写入。

---

## 测试

```bash
# 后端（pytest）
cd backend && python -m pytest

# 前端（Vitest）
cd frontend && npm run test
```

---

## 相关文档

- [技术设计文档](文档/技术设计文档.md) — 完整架构设计（v1.3，12 个模块已整合）
- [部署指南](文档/部署指南.md) — 阿里云 ECS 部署步骤、限额配置与故障排查
- [部署记录](文档/部署记录.md) — 2026-09-12 上线记录与踩坑复盘
- [Live2D 模型接入指南](文档/Live2D模型接入指南.md) — 虚拟人模型获取与接入说明
- [主人专属访问指南](文档/主人专属访问指南.md) — 私聊 / 管理后台 / 发布文章 的钥匙访问方法

---

## 说明

- AI 角色「流萤」为《崩坏：星穹铁道》角色，本项目为技术学习 / 个人博客用途，角色设定仅用于 AI 对话人设。
- 3D 虚拟人通过 Three.js 加载 GLB 模型并程序化驱动动画（呼吸、摇摆、浮动、情绪色氛围光），非传统 Live2D 格式。
