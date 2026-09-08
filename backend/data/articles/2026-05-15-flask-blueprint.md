---
title: "Flask Blueprint 模块化：让路由不再是一团乱麻"
date: 2026-05-15
category: Python
tags: ["Flask", "Python", "API"]
summary: "用 Blueprint 把 Flask 应用拆成清晰的功能模块，附应用工厂模式示例。"
---

## 问题

Flask 单文件项目刚起步很爽，路由一多就乱了。几十个 `@app.route` 挤在一起，改一个功能要翻半天。

## Blueprint 是什么

Blueprint 是 Flask 的模块化工具，可以把一组相关路由打包，再注册到应用上。

```python
# modules/articles/routes.py
from flask import Blueprint

articles_bp = Blueprint("articles", __name__)

@articles_bp.route("/api/articles")
def list_articles():
    return {"articles": []}
```

```python
# app.py
app.register_blueprint(articles_bp)
```

## 应用工厂模式

配合应用工厂，模块化更彻底：

```python
def create_app():
    app = Flask(__name__)
    from modules.articles.routes import articles_bp
    app.register_blueprint(articles_bp)
    return app
```

### 好处

- 每个模块独立文件，职责清晰
- 测试可以针对单个 Blueprint
- 新增功能不影响其他模块

## 小结

小项目也建议一开始就用 Blueprint 划分边界，省得后面重构。
