"""
知识库自动更新守护线程（KB Watcher）

只在「文章文件被新增 / 被修改」时触发增量更新，其余时间零开销：
    - 不参与对话、不周期性全量重建（全量重建仍用 `python manage.py reindex`）
    - 新文章 / 改动文章「写稳」后才入向量库：文件距上次修改超过 SETTLE_SECONDS
      （默认 60 秒）才算写完，避免索引到编辑到一半的半成品
    - 新增用 add，修改用 upsert 覆盖旧向量（同一 id 幂等，不产生重复）
    - 每次更新打印详细的「KB 已自动更新」清单（新增/修改、id、标题），
      并写入 logs/app.log 与终端（见 modules/logging_config.py）

启动方式：
    - 仅由后端入口 `python app.py` 显式调用（见 app.py 的 __main__）
    - debug 重载器（WERKZEUG_RUN_MAIN）下只跑在子进程，避免双线程
"""

import logging
import os
import threading
import time

logger = logging.getLogger("kb_watcher")

CHECK_INTERVAL = 10   # 轮询间隔（秒）
SETTLE_SECONDS = 60   # 文件「写稳」判定：距上次修改 ≥ 该秒数才视为写完


def start_kb_watcher(app):
    """启动后台守护线程（幂等：重复调用不会叠加线程）。"""
    if getattr(app, "_kb_watcher_started", False):
        logger.info("KB watcher 已运行，跳过重复启动")
        return
    app._kb_watcher_started = True

    # debug 重载器：父进程 WERKZEUG_RUN_MAIN 为空串，子进程为 "true"；
    # 只在子进程（或无重载器）启动，避免父/子双线程同时写索引。
    if os.environ.get("WERKZEUG_RUN_MAIN") == "":
        logger.info("debug 重载器父进程：KB watcher 交由子进程启动")
        return

    loader = app.extensions.get("article_loader")
    rag = app.extensions.get("rag_service")
    if not loader or not rag:
        logger.warning("KB watcher 未启动：缺少 loader 或 rag_service")
        return

    # 每个文章 id 最近一次「已入索引」时的文件 mtime，用于判断是否有改动
    indexed_mtime: dict[str, float] = {}

    def _settled(article_id: str) -> bool:
        mtime = loader.file_mtime(article_id)
        return bool(mtime) and (time.time() - mtime) >= SETTLE_SECONDS

    def watch():
        primed = False
        while True:
            time.sleep(CHECK_INTERVAL)
            try:
                data = loader.load_all()  # 文件有变更才真正刷新缓存
                articles = data["articles"]

                if not primed:
                    # 首轮只记录基线 mtime，不做任何更新
                    for a in articles:
                        indexed_mtime.setdefault(a["id"], loader.file_mtime(a["id"]))
                    primed = True
                    logger.info(
                        "KB watcher 基线就绪：已记录 %d 篇文章的修改时间，此后只监听新写/改动文章",
                        len(indexed_mtime),
                    )
                    continue

                changed = []
                for a in articles:
                    cur = loader.file_mtime(a["id"])
                    if cur and cur != indexed_mtime.get(a["id"]) and _settled(a["id"]):
                        changed.append(a)

                if changed:
                    # 先判断新增/修改，再更新基线
                    details = []
                    for a in changed:
                        prev = indexed_mtime.get(a["id"])
                        kind = "新增" if prev is None else "修改"
                        details.append((kind, a["id"], a.get("title", "")))
                        indexed_mtime[a["id"]] = loader.file_mtime(a["id"])

                    rag.upsert_articles(changed)
                    logger.info("KB 已自动更新 %d 篇文章：", len(details))
                    for kind, aid, title in details:
                        logger.info("  · [%s] %s（%s）", kind, title or aid, aid)
            except Exception as e:  # noqa: BLE001 —— 看护线程不允许崩溃退出
                logger.warning("KB 自动更新失败: %s", e)

    indexed_before = -1
    if hasattr(rag, "indexed_ids"):
        try:
            indexed_before = len(rag.indexed_ids())
        except Exception:
            indexed_before = -1
    logger.info(
        "KB watcher 已启动：当前知识库 %d 篇文章索引；每 %d 秒监听，文件写稳 %d 秒后自动入向量库（新增 add / 修改 upsert）",
        indexed_before,
        CHECK_INTERVAL,
        SETTLE_SECONDS,
    )

    threading.Thread(target=watch, daemon=True, name="kb-watcher").start()
