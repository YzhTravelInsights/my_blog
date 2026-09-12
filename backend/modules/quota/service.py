"""
每日 API 花费限额服务

背景：
    访客聊天走 DeepSeek 会产生真实费用。这里按天累计 token 用量并估算人民币花费，
    访客额度用尽后 **不再调用 DeepSeek**，直接返回一句友好提示，
    博主本人（owner）完全不受限额约束，只记录用量便于随时查看花了多少。

单位与价格：
    价格按「人民币 / 百万 token」，默认取 DeepSeek 官方 deepseek-chat 价位，
    可用环境变量覆盖（不同模型/不同时期价格会变，不用改代码）：

        QUOTA_DAILY_CNY=1.0                 # 访客每天最多花多少元（0 或负数 = 不限）
        DEEPSEEK_PRICE_INPUT_MISS=2.0       # 输入（缓存未命中）
        DEEPSEEK_PRICE_INPUT_HIT=0.5        # 输入（缓存命中）
        DEEPSEEK_PRICE_OUTPUT=8.0           # 输出

限额判定：
    已花费 >= 限额即视为用尽（保守取整，宁可早一点停，不会超支太多）。
"""

import logging
import os
import threading
from datetime import datetime

from . import models

logger = logging.getLogger("quota")

DEFAULT_LIMIT_CNY = 1.0
DEFAULT_PRICE_INPUT_MISS = 2.0
DEFAULT_PRICE_INPUT_HIT = 0.5
DEFAULT_PRICE_OUTPUT = 8.0

# 访客额度用尽时的回复（不调用 DeepSeek，零成本）
QUOTA_REPLY = "萤宝今天说了好多话，嗓子有点哑啦～明天再来找我聊天好不好？"


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        logger.warning("环境变量 %s=%r 不是数字，回退默认值 %s", name, raw, default)
        return default


def _usage_to_dict(usage) -> dict:
    """
    把 openai SDK 返回的 usage 统一成 dict。

    DeepSeek 会额外返回 prompt_cache_hit_tokens / prompt_cache_miss_tokens，
    这些字段在 SDK 里属于「额外字段」，需要从 model_extra 里取。
    """
    if usage is None:
        return {}
    if isinstance(usage, dict):
        data = dict(usage)
    elif hasattr(usage, "model_dump"):
        try:
            data = usage.model_dump()
        except Exception:
            data = {}
    else:
        data = {}

    extra = getattr(usage, "model_extra", None)
    if isinstance(extra, dict):
        for k, v in extra.items():
            data.setdefault(k, v)

    # 兜底：逐个属性读一遍
    for key in (
        "prompt_tokens", "completion_tokens", "total_tokens",
        "prompt_cache_hit_tokens", "prompt_cache_miss_tokens",
    ):
        if key not in data and hasattr(usage, key):
            try:
                data[key] = getattr(usage, key)
            except Exception:
                pass
    return data


def _as_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class QuotaService:
    """按天统计并限制访客的 DeepSeek 花费。"""

    def __init__(self, db_path: str, daily_limit_cny: float | None = None):
        self._db = db_path
        self._limit = (
            float(daily_limit_cny)
            if daily_limit_cny is not None
            else _env_float("QUOTA_DAILY_CNY", DEFAULT_LIMIT_CNY)
        )
        self._price_in_miss = _env_float("DEEPSEEK_PRICE_INPUT_MISS", DEFAULT_PRICE_INPUT_MISS)
        self._price_in_hit = _env_float("DEEPSEEK_PRICE_INPUT_HIT", DEFAULT_PRICE_INPUT_HIT)
        self._price_out = _env_float("DEEPSEEK_PRICE_OUTPUT", DEFAULT_PRICE_OUTPUT)

    # -- 基础 ---------------------------------------------------------------

    @staticmethod
    def today_str() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    @property
    def limit_cny(self) -> float:
        return self._limit

    @property
    def unlimited(self) -> bool:
        """限额 <= 0 视为不限制。"""
        return self._limit <= 0

    def cost_of(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cache_hit_tokens: int = 0,
        cache_miss_tokens: int | None = None,
    ) -> float:
        """按 token 数估算人民币花费。"""
        hit = max(0, _as_int(cache_hit_tokens))
        if cache_miss_tokens is None:
            miss = max(0, _as_int(prompt_tokens) - hit)
        else:
            miss = max(0, _as_int(cache_miss_tokens))
        return (
            miss / 1_000_000 * self._price_in_miss
            + hit / 1_000_000 * self._price_in_hit
            + max(0, _as_int(completion_tokens)) / 1_000_000 * self._price_out
        )

    # -- 记录 ---------------------------------------------------------------

    def record(self, scope: str, usage) -> dict:
        """
        记录一次调用的用量。scope: "guest" | "owner"。
        永不抛异常（记账失败不能影响对话）。
        """
        data = _usage_to_dict(usage)
        prompt = _as_int(data.get("prompt_tokens"))
        completion = _as_int(data.get("completion_tokens"))
        hit = _as_int(data.get("prompt_cache_hit_tokens"))
        miss = data.get("prompt_cache_miss_tokens")
        miss = _as_int(miss) if miss is not None else max(0, prompt - hit)

        cost = self.cost_of(prompt, completion, hit, miss)
        day = self.today_str()
        models.add_usage(
            self._db, day, scope,
            requests=1,
            prompt_tokens=prompt,
            completion_tokens=completion,
            cache_hit_tokens=hit,
            cache_miss_tokens=miss,
            cost_cny=cost,
        )
        logger.info(
            "用量已记 | %s | %s | in=%d out=%d | ¥%.4f",
            day, scope, prompt, completion, cost,
        )
        return {"day": day, "scope": scope, "cost_cny": round(cost, 6)}

    # -- 查询 ---------------------------------------------------------------

    def today(self, scope: str = "guest") -> dict:
        row = models.get(self._db, self.today_str(), scope) or {}
        spent = float(row.get("cost_cny") or 0.0)
        limit = self._limit
        # 只有访客受限额约束；主人只统计不限制
        is_limited = (scope == "guest") and not self.unlimited
        return {
            "day": self.today_str(),
            "scope": scope,
            "requests": int(row.get("requests") or 0),
            "prompt_tokens": int(row.get("prompt_tokens") or 0),
            "completion_tokens": int(row.get("completion_tokens") or 0),
            "cache_hit_tokens": int(row.get("cache_hit_tokens") or 0),
            "spent_cny": round(spent, 4),
            "limit_cny": limit,
            "unlimited": self.unlimited,
            "limited": is_limited,
            "remaining_cny": round(max(0.0, limit - spent), 4) if is_limited else None,
            "exhausted": is_limited and spent >= limit,
        }

    def guest_exhausted(self) -> bool:
        """访客今日额度是否已用尽。"""
        if self.unlimited:
            return False
        row = models.get(self._db, self.today_str(), "guest")
        if not row:
            return False
        return float(row.get("cost_cny") or 0.0) >= self._limit

    def summary(self) -> dict:
        """给管理后台用：限额、今日访客/主人花费、最近记录。"""
        return {
            "limit_cny": self._limit,
            "unlimited": self.unlimited,
            "price_per_million_cny": {
                "input_cache_miss": self._price_in_miss,
                "input_cache_hit": self._price_in_hit,
                "output": self._price_out,
            },
            "guest": self.today("guest"),
            "owner": self.today("owner"),
            "recent": models.recent(self._db, 14),
        }


# ---------------------------------------------------------------------------
# 模块级单例（service 层在没有 app context 时也能用）
# ---------------------------------------------------------------------------

_instance: QuotaService | None = None
_lock = threading.Lock()


def get_quota_service() -> QuotaService:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                from config import DATABASE_PATH
                _instance = QuotaService(DATABASE_PATH)
    return _instance
