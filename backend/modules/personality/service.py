"""
人格演化服务 — 印象生成 + 衰减

仅主人模式写入。
"""

from . import models


class PersonalityService:
    def __init__(self, db_path: str):
        self._db = db_path

    def generate_and_store(
        self, user_msg: str, assistant_reply: str, session_id: str, judge_fn
    ) -> str | None:
        """
        judge_fn: (user_msg, reply) -> str  (印象文本)
        返回生成的印象文本或 None。
        """
        impression_text = judge_fn(user_msg, assistant_reply)
        if not impression_text:
            return None

        models.add(self._db, content=impression_text, weight=1.0, session_id=session_id)
        return impression_text

    def decay(self):
        """衰减所有印象权重。"""
        models.decay_weights(self._db, factor=0.95)

    def build_context(self) -> str:
        """构建人格上下文片段。"""
        imp_list = models.get_recent(self._db, limit=10)
        if not imp_list:
            return ""

        lines = ["\n【你对开拓者的了解】"]
        for imp in imp_list:
            lines.append(f"- {imp['content']}（{imp['created_at']}）")
        return "\n".join(lines)
