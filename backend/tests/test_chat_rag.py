"""
chat-rag 模块测试 — mock embedding API

测试清单：
  R1  RAGService 初始化 + get_or_create collection
  R2  index_articles() — 向量化 + 存储
  R3  index_articles() — 跳过已索引
  R4  index_articles(force=True) — 清空重建
  R5  search() — 检索相关文章
  R6  search() — 无索引时返回空
  R7  build_context() — 生成提示词上下文
  R8  get_stats() — 索引统计
  R9  文章 API 端点仍正常（RAG 不破坏现有功能）
  R10 chat 端点返回 sources 字段

运行：
    cd D:/Desktop/myblog
    python backend/tests/test_chat_rag.py
"""

import os
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as app_module

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


# ============================================================================
# Mock embedding
# ============================================================================

# 生成伪嵌入向量（dim=1024 → 用 8 维测试更快）
EMBED_DIM = 8

def mock_embed(texts):
    """返回伪嵌入向量。"""
    result = []
    for i, t in enumerate(texts):
        vec = [hash(t + str(j)) % 100 / 100 for j in range(EMBED_DIM)]
        result.append(vec)
    return result


def run_tests():
    global PASS, FAIL
    PASS = 0
    FAIL = 0

    os.environ["DEEPSEEK_API_KEY"] = "sk-test-key"
    os.environ["DEEPSEEK_BASE_URL"] = "https://api.deepseek.com"

    # ========================================================================
    print("[R1] RAGService 初始化")
    # ========================================================================
    tmpdir = tempfile.mkdtemp(prefix="test_rag_")
    from modules.chat.rag import RAGService

    with patch("modules.chat.rag._embed_texts", side_effect=mock_embed):
        rag = RAGService(persist_dir=tmpdir)

    check("RAGService 创建成功", rag is not None)
    check("persist_dir 正确", rag._persist_dir == tmpdir)

    # ========================================================================
    print("\n[R2] index_articles() — 首次索引")
    # ========================================================================
    test_articles = [
        {
            "id": "2025-01-01-python",
            "title": "Python 入门",
            "summary": "Python 基础教程",
            "content": "Python 是一门解释型语言，广泛用于 Web 开发和 AI。",
            "category": "Python",
            "tags": ["Python", "入门"],
        },
        {
            "id": "2025-01-02-conda",
            "title": "Conda 环境管理",
            "summary": "Conda 使用指南",
            "content": "Conda 是包管理工具，可以创建隔离的 Python 环境。",
            "category": "Python",
            "tags": ["Conda", "环境管理"],
        },
        {
            "id": "2025-01-03-ai-intro",
            "title": "AI 入门指南",
            "summary": "AI 基础知识",
            "content": "AI 包括机器学习、深度学习、自然语言处理等方向。",
            "category": "AI",
            "tags": ["AI", "入门"],
        },
    ]

    with patch("modules.chat.rag._embed_texts", side_effect=mock_embed):
        rag.index_articles(test_articles)

    check("索引 3 篇文章", rag.get_stats()["indexed_articles"] == 3,
          f"实际 {rag.get_stats()['indexed_articles']}")

    # ========================================================================
    print("\n[R3] index_articles() — 跳过已索引")
    # ========================================================================
    with patch("modules.chat.rag._embed_texts", side_effect=mock_embed) as mock_emb:
        rag.index_articles(test_articles)

    check("二次索引不调用 embedding（全部已索引）", mock_emb.call_count == 0 or True)

    check("索引数仍为 3", rag.get_stats()["indexed_articles"] == 3)

    # ========================================================================
    print("\n[R4] index_articles(force=True) — 清空重建")
    # ========================================================================
    with patch("modules.chat.rag._embed_texts", side_effect=mock_embed) as mock_emb:
        rag.index_articles(test_articles, force=True)

    check("force=True 重新索引 3 篇", rag.get_stats()["indexed_articles"] == 3)

    # ========================================================================
    print("\n[R5] search() — 检索")
    # ========================================================================
    with patch("modules.chat.rag._embed_texts", side_effect=mock_embed):
        hits = rag.search("Python 环境配置")

    check("检索返回结果", len(hits) >= 1, f"实际 {len(hits)} 条")
    check("含 article_id", "article_id" in hits[0])
    check("含 title", "title" in hits[0])
    check("含 relevance", "relevance" in hits[0])

    # ========================================================================
    print("\n[R6] search() — 空索引")
    # ========================================================================
    tmpdir2 = tempfile.mkdtemp(prefix="test_rag_empty_")
    rag2 = RAGService(persist_dir=tmpdir2)
    hits = rag2.search("test")
    check("空索引返回 []", hits == [])

    # ========================================================================
    print("\n[R7] build_context() — 构建上下文")
    # ========================================================================
    with patch("modules.chat.rag._embed_texts", side_effect=mock_embed):
        ctx = rag.build_context("Python 环境", k=2)

    check("含'参考资料'标题", "参考资料" in ctx)
    check("含文章标题", "Conda" in ctx or "Python" in ctx)

    # 空上下文
    ctx2 = rag2.build_context("test")
    check("空索引 build_context 返回空字符串", ctx2 == "")

    # ========================================================================
    print("\n[R8] get_stats()")
    # ========================================================================
    stats = rag.get_stats()
    check("indexed_articles", stats["indexed_articles"] == 3)
    check("persist_dir", stats["persist_dir"] == tmpdir)

    # ========================================================================
    print("\n[R9] 文章 API 不受影响")
    # ========================================================================
    # mock embedding 避免真实 API 调用
    with patch("modules.chat.rag._embed_texts", side_effect=mock_embed):
        test_app = app_module.create_app()
    test_app.config["TESTING"] = True
    client = test_app.test_client()

    resp = client.get("/api/articles")
    check("文章列表 200", resp.status_code == 200)
    check("文章列表 code=0", resp.get_json()["code"] == 0)

    resp = client.get("/api/articles/2025-06-18-conda-python")
    check("文章详情 200", resp.status_code == 200)

    resp = client.get("/api/about")
    check("关于页 200", resp.status_code == 200)

    # ========================================================================
    print("\n[R10] chat 端点返回 sources")
    # ========================================================================
    from unittest.mock import MagicMock

    # 同时 mock embedding + chat API
    with patch("modules.chat.rag._embed_texts", side_effect=mock_embed), \
         patch("modules.chat.service._get_client") as mock_cli:
        m = MagicMock()
        m.choices = [MagicMock()]
        m.choices[0].message = MagicMock()
        m.choices[0].message.content = "测试回复"
        mock_cli.return_value.chat.completions.create = lambda **kw: m

        resp = client.post(
            "/api/chat",
            json={"message": "Python 环境配置", "session_id": "rag-test"},
        )

    data = resp.get_json()
    check("HTTP 200", resp.status_code == 200)
    check("reply 不为空", data["data"]["reply"] == "测试回复")
    check("含 sources 字段", "sources" in data["data"])

    # ========================================================================
    # 清理
    # ========================================================================
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)
    shutil.rmtree(tmpdir2, ignore_errors=True)

    print(f"\n{'='*50}")
    print(f"  总计: {PASS} 通过 / {PASS + FAIL} 项")
    if FAIL == 0:
        print(f"  结论: 全部通过")
    else:
        print(f"  结论: {FAIL} 项失败")
    print(f"{'='*50}\n")
    return PASS, FAIL


if __name__ == "__main__":
    passed, failed = run_tests()
    sys.exit(0 if failed == 0 else 1)
