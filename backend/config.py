"""
全局配置
集中管理项目路径，所有模块从此读取。
"""
import os

# 项目根目录（backend/ 的父目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据目录
DATA_DIR = os.path.join(PROJECT_ROOT, "backend", "data")
ARTICLES_DIR = os.path.join(DATA_DIR, "articles")
DRAFTS_DIR = os.path.join(DATA_DIR, "drafts")
ABOUT_FILE = os.path.join(DATA_DIR, "about.md")

# 数据库
DATABASE_PATH = os.path.join(DATA_DIR, "blog.db")
CHROMA_PERSIST_DIR = os.path.join(DATA_DIR, "chroma")

# 日志
LOG_DIR = os.path.join(PROJECT_ROOT, "backend", "logs")
API_ERROR_LOG = os.path.join(LOG_DIR, "api_error.log")
