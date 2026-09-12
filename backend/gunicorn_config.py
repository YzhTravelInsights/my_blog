"""
Gunicorn 生产配置（2 核 2 GiB 阿里云 ECS）

关键取舍：
    - workers = 1：torch + sentence-transformers 每个 worker 要独占约 400~600 MiB
      常驻内存，2 GiB 机器开 2 个 worker 极易被 OOM Killer 干掉。
    - worker_class = gthread + threads = 4：单进程多线程扛并发，
      聊天的慢请求（DeepSeek 数十秒）不会阻塞其它访客。
    - preload_app = False：本项目在 worker 里才初始化模型与 Chroma，
      预加载后再 fork 容易和 Chroma/SQLite 的连接状态打架；单 worker 也省不下内存。
    - timeout = 180：首次加载本地 embedding 模型在 2 核机器上要十几秒，
      聊天请求还要等 DeepSeek，超时给足避免 worker 被判定卡死。
"""

import os

# 监听地址：只绑本机，由 Nginx 反代对外
bind = os.environ.get("BLOG_BIND", "127.0.0.1:5000")

# 并发
workers = int(os.environ.get("BLOG_WORKERS", "1"))
worker_class = "gthread"
threads = int(os.environ.get("BLOG_THREADS", "4"))

# 稳定性
preload_app = False
timeout = 180
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100

# 日志（backend/logs/ 目录随部署创建）
_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(_log_dir, exist_ok=True)
accesslog = os.path.join(_log_dir, "gunicorn-access.log")
errorlog = os.path.join(_log_dir, "gunicorn-error.log")
loglevel = "info"
capture_output = True

# 进程名（便于 ps / top 里辨认）
proc_name = "myblog-gunicorn"
