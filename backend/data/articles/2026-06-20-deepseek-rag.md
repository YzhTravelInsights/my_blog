---
title: "给个人博客接上 DeepSeek + RAG 智能问答"
date: 2026-06-20
category: AI
tags: ["RAG", "DeepSeek", "向量检索", "知识库"]
summary: "记录把个人博客改造为 AI 问答机器人的完整过程：向量化、ChromaDB 检索、大模型生成，以及遇到的各种坑。"
---

## 背景

写博客的人都会有一个烦恼：内容越写越多，访客想找某篇旧文很费劲。如果能有一个「读过我所有文章」的 AI 助手，直接回答访客问题，体验会好很多。

## 整体架构

RAG（检索增强生成）的核心是三步：

1. 把文章切成小块，用 embedding 模型转成向量
2. 提问时，在向量库中找到最相关的片段
3. 把片段拼进 prompt，交给大模型生成回答

## 向量化与检索

### 选型

本地用 `sentence-transformers` 的 `all-MiniLM-L6-v2`，384 维，体积小、离线可用，对个人博客足够。

### ChromaDB 存储

ChromaDB 是嵌入式向量数据库，一个 Python 库就能跑，适合个人项目：

```python
import chromadb
client = chromadb.PersistentClient(path="data/chroma")
collection = client.get_or_create_collection("articles")
```

## 与大模型对接

用 OpenAI SDK 兼容协议调用 DeepSeek：

```python
from openai import OpenAI
client = OpenAI(base_url="https://api.deepseek.com", api_key=API_KEY)
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": prompt}],
)
```

## 踩过的坑

- 国内访问 HuggingFace 超时：设置 `TRANSFORMERS_OFFLINE=1` 并预下载模型
- 向量库与文章不同步：每次发文章后要重建索引
- 上下文太长：只取 top-3 片段，控制 token

## 小结

RAG 让个人知识库「活」了起来。如果你也在写博客，强烈推荐试一试。
