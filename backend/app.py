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


def create_app() -> Flask:
    app = Flask(__name__)

    # CORS 允许前端开发地址
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config["DATABASE_PATH"] = DATABASE_PATH

    # 初始化数据库表
    init_db(DATABASE_PATH)
    init_affinity(DATABASE_PATH)
    init_personality(DATABASE_PATH)

    # 注册 ArticleLoader 为扩展单例
    loader = ArticleLoader(ARTICLES_DIR, about_file=ABOUT_FILE)
    app.extensions["article_loader"] = loader

    # 初始化 RAG 知识库（embedding 不可用时优雅跳过）
    try:
        rag = RAGService(persist_dir=CHROMA_PERSIST_DIR)
        all_data = loader.load_all()
        rag.index_articles(all_data["articles"])
        app.extensions["rag_service"] = rag
    except Exception:
        app.extensions["rag_service"] = RAGService(persist_dir=CHROMA_PERSIST_DIR)

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

    # 注册 Blueprint
    app.register_blueprint(articles_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(chat_bp)

    @app.route("/")
    def index():
        return {"message": "My Blog API", "version": "1.0"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
