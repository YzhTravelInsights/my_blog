"""
RAG 知识库服务

职责：
    - 文章向量化（本地 sentence-transformers 模型）
    - Chroma 持久化存储
    - 检索相关文章上下文
    - 注入 chat service 的 RAG context

依赖：
    - chromadb（嵌入式向量数据库）
    - sentence-transformers（本地向量模型 all-MiniLM-L6-v2，384维）
    - ArticleLoader（获取文章全文）
"""

import os
import logging
import threading

logger = logging.getLogger("rag")

# ---------------------------------------------------------------------------
# 本地 SentenceTransformer 模型
# ---------------------------------------------------------------------------

_MODEL_NAME = "all-MiniLM-L6-v2"
_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
os.makedirs(_MODEL_DIR, exist_ok=True)

_model = None
_model_lock = threading.Lock()
_model_available = True  # 设为 False 表示模型不可用


def _get_model():
    """延迟加载 SentenceTransformer 模型（线程安全）。"""
    global _model, _model_available
    if _model is not None:
        return _model
    with _model_lock:
        if _model is not None:
            return _model
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"加载本地 embedding 模型: {_MODEL_NAME}")
            _model = SentenceTransformer(
                _MODEL_NAME,
                cache_folder=_MODEL_DIR,
            )
            logger.info(f"模型加载完成，维度: {_model.get_sentence_embedding_dimension()}")
            return _model
        except Exception as e:
            _model_available = False
            logger.warning(f"模型加载失败，RAG 将降级: {e}")
            return None


def _embed_texts(texts: list[str]) -> list[list[float]]:
    """使用本地 SentenceTransformer 批量向量化。"""
    if not texts:
        return []
    model = _get_model()
    if model is None:
        raise RuntimeError("Embedding 模型不可用")
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()

def is_embedding_available() -> bool:
    """返回 embedding 模型是否可用（用于外部判断是否降级）。"""
    return _model_available


class RAGService:
    """
    文章知识库检索服务。

    使用：
        rag = RAGService(persist_dir="data/chroma")
        rag.index_articles(articles)          # 全量索引
        results = rag.search("Conda 环境配置") # 检索
        context = rag.build_context("Conda")   # 构建提示词上下文
    """

    COLLECTION_NAME = "article_embeddings"

    def __init__(self, persist_dir: str):
        self._persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        self._collection = None  # lazy init

    def _ensure_collection(self):
        """延迟初始化 Chroma collection。"""
        if self._collection is not None:
            return
        import chromadb
        client = chromadb.PersistentClient(path=self._persist_dir)
        self._collection = client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    # -------------------------------------------------------------------
    # 索引
    # -------------------------------------------------------------------

    def index_articles(self, articles: list[dict], force: bool = False):
        """
        将文章列表向量化并存入 Chroma。

        参数:
            articles: [{id, title, content, category, tags, summary}, ...]
            force: True 时清空重建，False 时跳过已索引
        """
        self._ensure_collection()

        if force:
            # 清空重建
            existing = self._collection.get()
            if existing["ids"]:
                self._collection.delete(ids=existing["ids"])
            logger.info("RAG: 清空旧索引，全量重建")

        # 找出未索引的文章
        existing_ids = set(self._collection.get().get("ids", []))
        new_articles = [a for a in articles if a["id"] not in existing_ids]

        if not new_articles:
            logger.info(f"RAG: 所有 {len(articles)} 篇文章已索引，跳过")
            return

        # 准备数据
        texts = []
        ids = []
        metadatas = []
        for a in new_articles:
            # 向量化文本 = title + summary + content（截断控制 token）
            text = f"{a['title']}\n{a['summary']}\n{a['content'][:2000]}"
            texts.append(text)
            ids.append(a["id"])
            metadatas.append({
                "title": a["title"],
                "category": a.get("category", ""),
                "tags": ",".join(a.get("tags", [])),
                "article_id": a["id"],
            })

        # 批量嵌入
        logger.info(f"RAG: 正在向量化 {len(new_articles)} 篇文章...")
        embeddings = _embed_texts(texts)

        # 存入 Chroma
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        logger.info(f"RAG: 索引完成，{len(new_articles)} 篇新文章")

    # -------------------------------------------------------------------
    # 检索
    # -------------------------------------------------------------------

    def search(self, query: str, k: int = 3) -> list[dict]:
        """
        检索与查询最相关的文章。

        返回: [{article_id, title, relevance, content_snippet}, ...]
        """
        self._ensure_collection()

        existing = self._collection.get()
        if not existing["ids"]:
            return []

        query_embedding = _embed_texts([query])[0]

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, len(existing["ids"])),
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                relevance = max(0, 1 - distance)  # cosine distance → similarity
                hits.append({
                    "article_id": meta["article_id"],
                    "title": meta["title"],
                    "relevance": round(relevance, 4),
                    "content_snippet": results["documents"][0][i][:300],
                })
        return hits

    # -------------------------------------------------------------------
    # 上下文构建
    # -------------------------------------------------------------------

    def build_context(self, query: str, k: int = 3) -> str:
        """
        检索并构建可供注入 prompt 的文本上下文。

        返回: "【参考资料：博客相关文章】
                - 《Conda 教程》: 本文介绍 Conda 的使用...
                - 《Python 入门》: Python 是一门..."
        """
        hits = self.search(query, k=k)
        if not hits:
            return ""

        lines = ["\n【参考资料：博客相关文章】"]
        for h in hits:
            lines.append(f"- 《{h['title']}》(相关度 {h['relevance']:.0%})")
        return "\n".join(lines)

    # -------------------------------------------------------------------
    # 状态
    # -------------------------------------------------------------------

    def get_stats(self) -> dict:
        """RAG 索引统计。"""
        self._ensure_collection()
        data = self._collection.get()
        return {
            "indexed_articles": len(data.get("ids", [])),
            "persist_dir": self._persist_dir,
        }
