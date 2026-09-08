"""
日志配置

统一日志体系：INFO 级别、终端 + 文件（logs/app.log）双输出、
时间戳 + 级别 + 模块名格式化、文件按 2MB 滚动保留 5 份。

未配置时，Python 默认只输出 WARNING 以上日志 —— 这也是此前
终端看不到「KB 已自动更新」等 INFO 消息的原因。

用法：
    from modules.logging_config import setup_logging
    setup_logging()

调用一次即可（幂等），后续各模块用 logging.getLogger(__name__) 直接使用。
"""

import logging
import os
from logging.handlers import RotatingFileHandler

_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)-14s | %(message)s"
_DATE_FMT = "%H:%M:%S"


def setup_logging():
    """配置 root logger（INFO），终端 + logs/app.log 双输出。幂等。"""
    root = logging.getLogger()
    if getattr(root, "_myblog_configured", False):
        return
    root._myblog_configured = True

    fmt = logging.Formatter(_FORMAT, datefmt=_DATE_FMT)
    root.setLevel(logging.INFO)

    # 终端
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    root.addHandler(console)

    # 文件（logs/app.log，滚动）：只存「报错 + 关键事件」
    #   · WARNING/ERROR 等一律落盘（便于排查）
    #   · kb_watcher 的知识库自动更新清单属关键事件，也落盘
    #   · 其余日常 INFO（模型加载、请求、测试输出等）不写入，避免刷屏
    class _KeyEventsOnly(logging.Filter):
        def filter(self, record):
            return record.levelno >= logging.WARNING or record.name == "kb_watcher"

    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=2 * 1024 * 1024,  # 2MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)  # 级别放行到 INFO，由 filter 进一步收窄
    file_handler.addFilter(_KeyEventsOnly())
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    # Flask 自带 werkzeug 请求日志提到 INFO（终端可见每次请求）
    logging.getLogger("werkzeug").setLevel(logging.INFO)

    logging.getLogger(__name__).info("日志已初始化：终端 INFO（详细），文件仅报错 + 关键事件")
