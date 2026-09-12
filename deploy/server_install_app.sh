#!/usr/bin/env bash
# ============================================================================
# myblog 应用部署脚本（在服务器上以 root 运行，由本机 deploy.ps1 调用）
#
#     sudo bash /tmp/myblog-server_install_app.sh
#
# 做的事：
#   1. 解包 /tmp/myblog-code.tar.gz 到 /home/blog/my_blog
#   2. 解包 /tmp/myblog-models.tar.gz 到 backend/models（rag.py 强制离线，必须预置）
#   3. 写入 backend/.env（600 权限，仅 blog 用户可读）
#   4. 建 venv 装依赖（torch 走 CPU 源，避免拉 CUDA 版 2 GB+ 依赖）
#   5. init-db + 重建 Chroma 向量索引
#   6. 重启 blog 服务并打印状态
#
# 幂等：重复执行只做增量（依赖已装则跳过、venv 已存在则复用）
# ============================================================================
set -euo pipefail

APP_USER=blog
APP_DIR=/home/blog/my_blog
VENV="$APP_DIR/backend/venv"
PY="$VENV/bin/python"
PIP="$VENV/bin/pip"

# 国内直连 PyPI 很慢，默认走清华源；要换回官方源传 PIP_INDEX=... 即可
PIP_INDEX="${PIP_INDEX:-https://pypi.tuna.tsinghua.edu.cn/simple}"

log() { echo -e "\n\033[1;32m==> $*\033[0m"; }
warn() { echo -e "\033[1;33m!! $*\033[0m"; }

if [ "$(id -u)" -ne 0 ]; then
    echo "请用 root 运行：sudo bash $0" >&2
    exit 1
fi

as_app() { sudo -u "$APP_USER" --preserve-env=PATH "$@"; }

# ---------------------------------------------------------------------------
log "1/6 解包代码 -> $APP_DIR"
mkdir -p "$APP_DIR"
if [ -f /tmp/myblog-code.tar.gz ]; then
    tar -xzf /tmp/myblog-code.tar.gz -C "$APP_DIR"
else
    echo "缺少 /tmp/myblog-code.tar.gz" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
log "2/6 预置本地 embedding 模型缓存"
if [ -f /tmp/myblog-models.tar.gz ]; then
    mkdir -p "$APP_DIR/backend/models"
    tar -xzf /tmp/myblog-models.tar.gz -C "$APP_DIR/backend/models"
    echo "模型缓存已就位（$(du -sh "$APP_DIR/backend/models" | cut -f1)）"
elif [ -d "$APP_DIR/backend/models/models--sentence-transformers--all-MiniLM-L6-v2" ]; then
    echo "模型缓存已存在，跳过"
else
    warn "没有模型缓存 —— RAG 会自动降级（聊天仍可用，但不引用博客文章）"
fi

# ---------------------------------------------------------------------------
log "3/6 写入 backend/.env"
if [ -f /tmp/myblog-server.env ]; then
    install -m 600 -o "$APP_USER" -g "$APP_USER" /tmp/myblog-server.env "$APP_DIR/backend/.env"
    shred -u /tmp/myblog-server.env 2>/dev/null || rm -f /tmp/myblog-server.env
    echo ".env 已写入（权限 600，属主 $APP_USER）"
elif [ ! -f "$APP_DIR/backend/.env" ]; then
    echo "缺少 $APP_DIR/backend/.env，且没有上传新模板" >&2
    exit 1
else
    echo ".env 已存在，保留不动"
fi

mkdir -p "$APP_DIR/backend/logs" "$APP_DIR/backend/data/chroma" "$APP_DIR/backend/data/articles"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# 关键：切到应用目录再以 blog 身份跑 Python。
# 原因：chromadb 初始化时 pydantic-settings 会在「当前工作目录」找 .env，
# 而 sudo 会继承本脚本的 CWD（ssh 登录后是 /root）。blog 用户读不了 /root，
# 于是 stat('.env') 抛 PermissionError（不是 FileNotFoundError），把导入直接炸掉。
cd "$APP_DIR"

# ---------------------------------------------------------------------------
log "4/6 准备 Python 虚拟环境"
if [ ! -x "$PY" ]; then
    as_app python3 -m venv "$VENV"
    echo "venv 已创建"
else
    echo "venv 已存在，复用"
fi

as_app "$PIP" install -q --upgrade pip wheel

# 先装 CPU 版 torch：Linux 上 pip 默认拉的是 CUDA 版，还会拖 3~4 GB 的 nvidia-* 依赖，
# 这台 2 核 / 1.6 GiB 内存的机器既用不上也扛不住，必须用 CPU 轮子。
# 官方 CPU 源 download.pytorch.org 国内经常超时，所以优先走国内镜像的扁平 wheel 目录。
install_cpu_torch() {
    local pytag name ver url
    pytag=$(as_app "$PY" -c 'import sys; print("cp%d%d" % (sys.version_info[0], sys.version_info[1]))')

    for M in "https://mirrors.aliyun.com/pytorch-wheels/cpu/" \
             "https://mirror.sjtu.edu.cn/pytorch-wheels/cpu/"; do
        # 目录列表里挑出适配当前 Python 的最新 x86_64 CPU 轮子（+ 在 HTML 里是 &#43;）
        name=$(curl -s -m 40 "$M" \
            | grep -oE "torch-[0-9.]+(&#43;|\+)cpu-${pytag}-${pytag}-manylinux[0-9_]*x86_64\.whl" \
            | sort -Vu | tail -1)
        if [ -n "$name" ]; then
            ver=$(printf '%s' "$name" | sed -E 's/^torch-([0-9.]+).*/\1/')
            url=$(printf '%s%s' "$M" "$name" | sed 's/&#43;/+/g')
            log "从国内镜像安装 torch==${ver}+cpu（约 200 MB）"
            echo "  $url"
            if as_app "$PIP" install --no-cache-dir -i "$PIP_INDEX" "$url"; then
                return 0
            fi
            warn "该镜像安装失败，换下一个源"
        else
            warn "该镜像没有 ${pytag} 的 CPU 轮子：$M"
        fi
    done

    log "国内镜像不可用，改试官方 CPU 源（国内可能超时）"
    if as_app "$PIP" install --no-cache-dir --timeout 120 --retries 3 \
            --index-url https://download.pytorch.org/whl/cpu torch; then
        return 0
    fi

    warn "所有 CPU 轮子源都失败，回退 PyPI（会装 CUDA 版 torch，多占约 3~4 GB 磁盘）"
    as_app "$PIP" install --no-cache-dir -i "$PIP_INDEX" torch
}

if ! as_app "$PY" -c "import torch" >/dev/null 2>&1; then
    install_cpu_torch
fi

log "安装项目依赖（首次 5~10 分钟）"
as_app "$PIP" install -q -i "$PIP_INDEX" -r "$APP_DIR/backend/requirements.txt" gunicorn

as_app "$PY" - <<'PYCHECK'
import torch, sentence_transformers, chromadb, flask
print(f"torch {torch.__version__} / sentence-transformers {sentence_transformers.__version__} / chromadb {chromadb.__version__} / flask {flask.__version__}")
PYCHECK

# ---------------------------------------------------------------------------
log "5/6 初始化数据库与向量索引"
as_app "$PY" "$APP_DIR/backend/manage.py" init-db
if as_app "$PY" "$APP_DIR/backend/manage.py" reindex; then
    echo "向量索引重建完成"
else
    warn "reindex 失败 —— RAG 会降级，聊天等其它功能不受影响"
fi

# ---------------------------------------------------------------------------
log "6/6 重启服务"
systemctl daemon-reload
systemctl enable blog >/dev/null 2>&1 || true
systemctl restart blog
sleep 5
systemctl --no-pager --lines=15 status blog || true
echo
echo "本机自测："
curl -s -m 10 http://127.0.0.1:5000/ && echo
curl -s -o /dev/null -w "nginx / -> HTTP %{http_code}\n" -m 10 http://127.0.0.1/ || true
curl -s -o /dev/null -w "nginx /api/articles -> HTTP %{http_code}\n" -m 10 http://127.0.0.1/api/articles || true
