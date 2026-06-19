---
title: "使用 Conda 管理 Python 环境"
date: 2025-06-18
category: Python
tags: ["Python", "Conda", "环境管理"]
summary: "本文介绍如何使用 Conda 创建和管理 Python 虚拟环境，涵盖安装、常用命令、环境导出与复现。"
---

## 引言

Conda 是一个强大的包管理和环境管理工具，特别适合 Python 数据科学和 AI 开发。

## 安装 Conda

推荐安装 Miniconda，体积小、够用：

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

## 创建环境

```bash
conda create -n myproject python=3.11 -y
conda activate myproject
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `conda env list` | 查看所有环境 |
| `conda list` | 当前环境的包 |
| `conda install xxx` | 安装包 |
| `conda env export > env.yml` | 导出环境 |

## 小结

Conda 让 Python 环境管理变得简单可靠，推荐每个 Python 开发者使用。
