"""
每日 API 花费限额测试

覆盖：
  Q1  建表 + 初始状态（未用尽）
  Q2  成本计算（缓存命中/未命中/输出分别计价）
  Q3  访客用量累计，超过限额即用尽
  Q4  用尽后 guest_exhausted() 为 True（service 层据此不再调用 DeepSeek）
  Q5  主人（owner）不受限额约束，但仍记账
  Q6  QUOTA_DAILY_CNY=0 → 不限制
  Q7  usage 为 None / dict 时记录不崩
  Q8  同一天同一身份累加成一行（不是多行）

运行：
    python backend/tests/test_quota.py
    python -m pytest backend/tests/test_quota.py -q
"""

import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from modules.quota.models import init_table, get as get_usage, recent  # noqa: E402
from modules.quota.service import QuotaService  # noqa: E402

TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_quota_tmp")


class FakeUsage:
    """模拟 openai SDK 的 usage（DeepSeek 的缓存字段走 model_extra）"""

    def __init__(self, prompt=0, completion=0, hit=0, miss=0):
        self.prompt_tokens = prompt
        self.completion_tokens = completion
        self.prompt_cache_hit_tokens = hit
        self.prompt_cache_miss_tokens = miss
        self.model_extra = {}


def _fresh(name: str) -> str:
    os.makedirs(TMP_DIR, exist_ok=True)
    db = os.path.join(TMP_DIR, name)
    if os.path.exists(db):
        os.remove(db)
    init_table(db)
    return db


# ---------------------------------------------------------------------------
def test_q1_init_state():
    db = _fresh("q1.db")
    svc = QuotaService(db, daily_limit_cny=1.0)
    today = svc.today("guest")
    assert today["requests"] == 0
    assert today["spent_cny"] == 0
    assert today["exhausted"] is False
    assert svc.guest_exhausted() is False
    assert get_usage(db, today["day"], "guest") is None


def test_q2_cost_calculation():
    db = _fresh("q2.db")
    svc = QuotaService(db, daily_limit_cny=1.0)
    # miss 200×2元/M + hit 1000×0.5元/M + out 400×8元/M = 0.0004+0.0005+0.0032
    cost = svc.cost_of(1200, 400, cache_hit_tokens=1000, cache_miss_tokens=200)
    assert abs(cost - 0.0041) < 1e-9, cost
    # 不给 miss 时用 prompt - hit 推算
    assert abs(svc.cost_of(1200, 0, 1000) - 0.0009) < 1e-9


def test_q3_q4_guest_exhausts_and_blocks():
    db = _fresh("q3.db")
    svc = QuotaService(db, daily_limit_cny=0.01)
    usage = FakeUsage(1200, 400, 1000, 200)  # 每次 ¥0.0041

    svc.record("guest", usage)
    svc.record("guest", usage)
    assert svc.guest_exhausted() is False, "两次共 ¥0.0082，还没到 ¥0.01"
    assert svc.today("guest")["exhausted"] is False

    svc.record("guest", usage)
    assert svc.guest_exhausted() is True, "三次共 ¥0.0123，应已用尽"
    today = svc.today("guest")
    assert today["exhausted"] is True
    assert today["remaining_cny"] == 0.0
    assert today["requests"] == 3


def test_q5_owner_exempt_but_tracked():
    db = _fresh("q5.db")
    svc = QuotaService(db, daily_limit_cny=0.01)
    big = FakeUsage(100000, 50000, 0, 100000)  # 远超限额

    svc.record("owner", big)
    owner = svc.today("owner")
    assert owner["spent_cny"] > 0.01
    assert owner["exhausted"] is False, "主人不受限额约束"
    assert owner["limited"] is False
    assert owner["remaining_cny"] is None
    # 主人用量不应影响访客额度
    assert svc.guest_exhausted() is False


def test_q6_unlimited_when_zero():
    db = _fresh("q6.db")
    svc = QuotaService(db, daily_limit_cny=0)
    assert svc.unlimited is True
    svc.record("guest", FakeUsage(10 ** 6, 10 ** 6))
    assert svc.guest_exhausted() is False
    assert svc.today("guest")["unlimited"] is True


def test_q7_record_robust():
    db = _fresh("q7.db")
    svc = QuotaService(db, daily_limit_cny=1.0)
    svc.record("guest", None)                                   # 无 usage
    svc.record("guest", {"prompt_tokens": 100, "completion_tokens": 50})  # dict 形式
    svc.record("guest", FakeUsage())                            # 全 0
    today = svc.today("guest")
    assert today["requests"] == 3
    assert today["prompt_tokens"] == 100
    assert today["completion_tokens"] == 50


def test_q8_single_row_per_day():
    db = _fresh("q8.db")
    svc = QuotaService(db, daily_limit_cny=1.0)
    for _ in range(5):
        svc.record("guest", FakeUsage(100, 100, 0, 100))
    rows = [r for r in recent(db, 50) if r["scope"] == "guest"]
    assert len(rows) == 1, "同一天同身份应累加为一行"
    assert rows[0]["requests"] == 5


def test_q9_summary_shape():
    db = _fresh("q9.db")
    svc = QuotaService(db, daily_limit_cny=1.0)
    svc.record("guest", FakeUsage(100, 100, 0, 100))
    svc.record("owner", FakeUsage(100, 100, 0, 100))
    s = svc.summary()
    for key in ("limit_cny", "unlimited", "price_per_million_cny", "guest", "owner", "recent"):
        assert key in s, key
    assert s["guest"]["scope"] == "guest"
    assert s["owner"]["scope"] == "owner"


# ---------------------------------------------------------------------------
def main():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
    shutil.rmtree(TMP_DIR, ignore_errors=True)
    print(f"\n{len(tests) - failed}/{len(tests)} 通过")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
