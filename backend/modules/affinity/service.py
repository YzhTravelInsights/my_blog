"""
好感度服务

仅主人模式写入。公开模式只读但固定返回 stranger。
等级自动切换，仅看互动次数。
"""

from . import models

LEVELS = ["stranger", "acquaintance", "close_friend", "soul_bond"]
LEVEL_NAMES = {"stranger": "陌生人", "acquaintance": "熟人", "close_friend": "挚友", "soul_bond": "羁绊"}

# 等级切换阈值
THRESHOLDS = {"acquaintance": 10, "close_friend": 50, "soul_bond": 100}


class AffinityService:
    def __init__(self, db_path: str):
        self._db = db_path

    def get(self, mode: str = "public") -> dict:
        """
        获取好感度状态。
        mode="public" → 固定返回 stranger
        mode="owner" → 返回真实值
        """
        if mode == "public":
            return {"level": "stranger", "level_name": "陌生人", "interaction_count": 0}
        row = models.get(self._db)
        if not row:
            return {"level": "stranger", "level_name": "陌生人", "interaction_count": 0}
        return {
            "level": row["level"],
            "level_name": LEVEL_NAMES.get(row["level"], row["level"]),
            "interaction_count": row["interaction_count"],
        }

    def record_interaction(self):
        """每次主人对话后计数+1，自动检查升级。"""
        row = models.get(self._db)
        if not row:
            return self.get("owner")

        new_count = row["interaction_count"] + 1
        new_level = row["level"]

        for lvl_name in LEVELS:
            threshold = THRESHOLDS.get(lvl_name)
            if threshold and new_count >= threshold:
                new_level = lvl_name

        from datetime import datetime
        models.update(
            self._db,
            interaction_count=new_count,
            level=new_level,
            last_interaction_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        return self.get("owner")

    def get_prompt(self) -> str:
        """返回好感度对应的提示词片段。"""
        row = models.get(self._db)
        if not row:
            return ""

        prompts = {
            "stranger": "你和开拓者还不太熟悉，友善但保持一点距离感。用'你好呀'而不是'你终于来了'。",
            "acquaintance": "你和开拓者已经是熟人了。可以主动问'今天想聊什么呀？'，用'你来啦！'打招呼。",
            "close_friend": "你和开拓者是很好的朋友了。可以撒娇、分享小秘密，称呼改为'你呀～'，偶尔关心他的生活。",
            "soul_bond": "开拓者是你最重要的人。温柔而深情，会主动提起过去的回忆，用'还记得那次...'开头。",
        }
        return prompts.get(row["level"], "")
