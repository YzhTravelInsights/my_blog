"""
Chroma 封装 — 记忆嵌入向量存储
"""

import os
import chromadb


class ChromaMemoryStore:
    COLLECTION = "memory_embeddings"

    def __init__(self, persist_dir: str):
        os.makedirs(persist_dir, exist_ok=True)
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._col = self._client.get_or_create_collection(
            name=self.COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, mem_id: str, text: str, embedding: list[float], metadata: dict):
        self._col.add(
            ids=[mem_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
        )

    def search(self, query_embedding: list[float], k: int = 5) -> list[dict]:
        data = self._col.get()
        if not data["ids"]:
            return []
        results = self._col.query(
            query_embeddings=[query_embedding],
            n_results=min(k, len(data["ids"])),
            include=["documents", "metadatas", "distances"],
        )
        hits = []
        if results["ids"] and results["ids"][0]:
            for i, mid in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i]
                dist = results["distances"][0][i]
                hits.append({
                    "id": mid,
                    "content": results["documents"][0][i],
                    "metadata": meta,
                    "relevance": round(max(0, 1 - dist), 4),
                })
        return hits

    def delete(self, mem_id: str):
        self._col.delete(ids=[mem_id])

    def count(self) -> int:
        return len(self._col.get().get("ids", []))

    def trim(self, max_items: int = 500):
        """保留最新 max_items 条，删除多余的。"""
        data = self._col.get()
        ids = data.get("ids", [])
        if len(ids) > max_items:
            # 简单裁剪：删除最旧的
            excess = ids[: len(ids) - max_items]
            if excess:
                self._col.delete(ids=excess)
