"""
长期记忆服务 — Chroma 向量存储 + DeepSeek 重要性判断

仅主人模式写入。
"""

import uuid
from .chroma_store import ChromaMemoryStore


class MemoryService:
    MAX_MEMORIES = 500

    def __init__(self, persist_dir: str, embed_fn):
        """
        embed_fn: (text: str) -> list[float]  嵌入函数
        """
        self._store = ChromaMemoryStore(persist_dir)
        self._embed = embed_fn

    def remember(self, text: str, metadata: dict | None = None):
        """存储一条记忆。"""
        if self._store.count() >= self.MAX_MEMORIES:
            self._store.trim(self.MAX_MEMORIES - 1)

        embedding = self._embed(text)
        mem_id = f"mem_{uuid.uuid4().hex[:12]}"
        meta = metadata or {}
        self._store.add(mem_id, text, embedding, meta)

    def recall(self, query: str, k: int = 5) -> list[dict]:
        """检索相关记忆。"""
        embedding = self._embed(query)
        return self._store.search(embedding, k=k)

    def build_context(self, query: str) -> str:
        """构建记忆上下文片段。"""
        hits = self.recall(query, k=5)
        if not hits:
            return ""
        lines = ["\n【流萤记得的关于开拓者的事情】"]
        for h in hits:
            lines.append(f"- {h['content']}")
        return "\n".join(lines)

    def decide_and_store(
        self, user_msg: str, assistant_reply: str, session_id: str, judge_fn
    ):
        """
        judge_fn: (user_msg, reply) -> {"memorable": bool, "text": str, "importance": float}
        由外部（chat service）调用 DeepSeek 判断，这里只负责存储。
        """
        decision = judge_fn(user_msg, assistant_reply)
        if decision.get("memorable"):
            self.remember(
                decision["text"],
                metadata={
                    "importance": decision.get("importance", 0.5),
                    "session_id": session_id,
                },
            )
            return True
        return False

    def stats(self) -> dict:
        return {"total_memories": self._store.count()}
