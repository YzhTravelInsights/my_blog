"""
Flask 应用工厂
创建并配置 Flask app，注册所有 Blueprint 和扩展。
"""

import os
import sys

# 确保 backend 目录在 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# 日志初始化：终端 + logs/app.log 双输出（INFO 级别，含时间戳/模块名）
from modules.logging_config import setup_logging
setup_logging()

from flask import Flask
from flask_cors import CORS

from config import ARTICLES_DIR, ABOUT_FILE, DATABASE_PATH, CHROMA_PERSIST_DIR
from modules.articles.loader import ArticleLoader
from modules.articles.routes import articles_bp
from modules.comments.models import init_db
from modules.comments.routes import comments_bp
from modules.chat.routes import chat_bp
from modules.chat.rag import RAGService, _embed_texts
from modules.affinity.models import init_table as init_affinity
from modules.affinity.service import AffinityService
from modules.memory.service import MemoryService
from modules.personality.models import init_table as init_personality
from modules.personality.service import PersonalityService
from modules.quota.models import init_table as init_quota
from modules.quota.service import get_quota_service
from modules.admin.routes import admin_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # 记录后端启动时间（供管理后台展示运行时长）
    import time as _time
    app.extensions["_started_at"] = _time.time()

    # CORS 允许前端开发地址
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config["DATABASE_PATH"] = DATABASE_PATH

    # 初始化数据库表
    init_db(DATABASE_PATH)
    init_affinity(DATABASE_PATH)
    init_personality(DATABASE_PATH)
    init_quota(DATABASE_PATH)

    # 注册 ArticleLoader 为扩展单例
    loader = ArticleLoader(ARTICLES_DIR, about_file=ABOUT_FILE)
    app.extensions["article_loader"] = loader

    # 初始化 RAG 知识库（本地 embedding 模型，不可用时优雅降级）
    from modules.chat.rag import is_embedding_available, _get_model as _preload_model
    rag = RAGService(persist_dir=CHROMA_PERSIST_DIR)
    try:
        # 预热模型（首次下载 ~80MB，后续秒加载）
        _preload_model()
        if is_embedding_available():
            all_data = loader.load_all()
            rag.index_articles(all_data["articles"])
        else:
            logger = __import__("logging").getLogger(__name__)
            logger.warning("Embedding 模型不可用，RAG 索引跳过")
    except Exception as e:
        import logging as _logging
        _logging.getLogger(__name__).warning(f"RAG 初始化失败: {e}")
    app.extensions["rag_service"] = rag

    # 初始化好感度
    affinity = AffinityService(DATABASE_PATH)
    app.extensions["affinity_service"] = affinity

    # 初始化长期记忆（单字符串 → 列表适配）
    def _single_embed(text: str) -> list[float]:
        return _embed_texts([text])[0]

    memory = MemoryService(
        persist_dir=os.path.join(CHROMA_PERSIST_DIR, "memories"),
        embed_fn=_single_embed,
    )
    app.extensions["memory_service"] = memory

    # 初始化人格演化
    personality = PersonalityService(DATABASE_PATH)
    app.extensions["personality_service"] = personality

    # 每日 API 花费限额（访客限额，主人豁免）
    app.extensions["quota_service"] = get_quota_service()

    # 注册 Blueprint
    app.register_blueprint(articles_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        return {"message": "My Blog API", "version": "1.0"}

    return app


if __name__ == "__main__":
    app = create_app()
    # 知识库自动更新：检测到新文章/修改文章时增量入向量库（只由服务器入口启动）
    from modules.kb_watcher import start_kb_watcher
    start_kb_watcher(app)
    app.run(host="127.0.0.1", port=5000, debug=True)
