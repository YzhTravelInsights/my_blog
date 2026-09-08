"""
admin 删除接口测试 — 主人删除文章 / 删除评论（含鉴权拦截）

覆盖：
  1. 无钥匙访问 admin 接口 → 401
  2. 发布临时文章 → 评论 → 删除评论（含不存在 404）→ 删除文章 → 公开列表消失 → 重复删除 404

注意：该测试会用真实数据目录临时创建并删除一篇测试文章（自清理）。
请在后端未运行时执行，避免与运行中的 Chroma / SQLite 争锁。

运行：
    cd D:/Desktop/myblog
    python backend/tests/test_admin_delete.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["OWNER_SECRET"] = "test-owner-secret"

from app import create_app  # noqa: E402

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}  <- {detail}")


def test_auth_required(client):
    """无钥匙 → 401"""
    print("\n[1] 鉴权拦截（无钥匙）")
    check("DELETE 文章被拦",
          client.delete("/api/admin/article/whatever").status_code == 401)
    check("DELETE 评论被拦",
          client.delete("/api/admin/comment/1").status_code == 401)
    check("GET summary 被拦",
          client.get("/api/admin/summary").status_code == 401)


def test_publish_then_delete(client, db_path):
    """发布临时文章 → 评论 → 删除评论 → 删除文章"""
    print("\n[2] 发布 → 删除文章 / 评论")
    headers = {"Authorization": "Bearer test-owner-secret"}

    # 发布临时文章
    resp = client.post("/api/admin/article", headers=headers, json={
        "title": "删除功能测试文章",
        "category": "测试",
        "tags": ["测试"],
        "content": "# 删除功能测试\n\n临时文章，验证删除后即消失。",
    })
    data = resp.get_json()
    check("发布临时文章 code=0", resp.status_code == 200 and data.get("code") == 0, str(data))
    aid = data["data"]["id"]

    # 插入一条测试评论（直接走数据层，绕开 IP 速率限制）
    from modules.comments.models import create_comment
    c = create_comment(db_path, aid, "127.0.0.1", "测试评论，待删除", "测试访客")
    cid = c["id"]
    check("已插入测试评论", cid > 0)

    # 删除评论
    resp = client.delete(f"/api/admin/comment/{cid}", headers=headers)
    check("删除评论 code=0", resp.status_code == 200 and resp.get_json()["code"] == 0, str(resp.get_json()))
    check("返回删除条数 hint", "hint" in resp.get_json()["data"])

    # 评论已删除 → 再删返回 404
    resp = client.delete(f"/api/admin/comment/{cid}", headers=headers)
    check("评论不存在时 404", resp.status_code == 404)

    # 删除文章
    resp = client.delete(f"/api/admin/article/{aid}", headers=headers)
    check("删除文章 code=0", resp.status_code == 200 and resp.get_json()["code"] == 0, str(resp.get_json()))
    check("返回 deleted_comments", resp.get_json()["data"].get("deleted_comments") is not None)

    # 公开列表消失
    resp = client.get(f"/api/articles/{aid}")
    check("文章公开后已 404", resp.status_code == 404)

    # 重复删除 → 404
    resp = client.delete(f"/api/admin/article/{aid}", headers=headers)
    check("重复删除文章 404", resp.status_code == 404)


def run_tests():
    global PASS, FAIL
    PASS = 0
    FAIL = 0

    app = create_app()
    app.config["TESTING"] = True
    db_path = app.config["DATABASE_PATH"]

    with app.test_client() as c:
        test_auth_required(c)
        test_publish_then_delete(c, db_path)

    print(f"\n{'='*50}")
    print(f"  总计: {PASS} 通过 / {PASS + FAIL} 项")
    print(f"  结论: {'全部通过' if FAIL == 0 else f'{FAIL} 项失败'}")
    print(f"{'='*50}\n")
    return PASS, FAIL


if __name__ == "__main__":
    passed, failed = run_tests()
    sys.exit(0 if failed == 0 else 1)
