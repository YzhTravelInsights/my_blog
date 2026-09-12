"""
生产环境 WSGI 入口（gunicorn 使用）

本地开发仍然用 `python app.py`（Werkzeug 内置服务器 + debug 重载）；
服务器上用 gunicorn 加载本模块：

    gunicorn -c gunicorn_config.py wsgi:app

与 app.py 的 __main__ 区别：
    - 不在本文件里开 debug / 内置服务器
    - 显式启动知识库守护线程（app.py 的 __main__ 里那段逻辑在 gunicorn 下不会执行）
"""

import os
import sys

# 确保 backend 目录在 Python 路径（systemd 的 WorkingDirectory 已经保证，这里再兜一层）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app  # noqa: E402  （必须先插入 sys.path）

app = create_app()

# 知识库自动更新：新增/修改文章在「写稳 60 秒」后增量入向量库。
# 生产环境固定单 worker（2 GiB 内存装不下两份 torch 模型），因此不会重复起线程。
from modules.kb_watcher import start_kb_watcher  # noqa: E402

start_kb_watcher(app)
