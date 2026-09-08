---
title: "本地语义搜索：从零搭建 ChromaDB 向量索引"
date: 2026-04-30
category: AI
tags: ["ChromaDB", "embedding", "语义搜索"]
summary: "不依赖任何云端服务，纯本地搭建一套语义搜索索引，支持『模糊找得到』的搜索体验。"
---

## 为什么需要语义搜索

传统关键词搜索靠字符串匹配，搜「装环境」可能搜不到「Conda 配置」。语义搜索理解意思，容错高很多。

## 原理速览

- embedding 把文本变成高维向量
- 语义相近的文本，向量距离近
- 查询时算相似度，取最近的前 N 条

## 实战

### 建库

```python
import chromadb

client = chromadb.PersistentClient(path="./data/chroma")
collection = client.get_or_create_collection(name="articles")
```

### 写入

```python
collection.add(
    ids=["2026-05-15-flask-blueprint"],
    documents=["Flask Blueprint 模块化指南"],
    metadatas=[{"title": "Flask Blueprint 模块化"}],
)
```

### 查询

```python
results = collection.query(query_texts=["怎么拆分路由"], n_results=3)
```

## 与关键词搜索互补

向量搜索适合「意思相近」，关键词搜索适合「精确命中」。两者结合，体验最佳。

## 小结

本地向量库门槛已经很低了，一个库、几十行代码就能跑起来，值得一试。
