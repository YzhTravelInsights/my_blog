#!/usr/bin/env bash
# ============================================================================
# myblog 服务器初始化脚本（Ubuntu 24.04，阿里云 ECS 2 核 2 GiB）
#
# 只需在服务器上跑一次（幂等，重复跑也不会坏事）：
#     sudo bash /tmp/myblog-server_setup.sh
#
# 做的事：
#   1. 装系统依赖（python3 venv / nginx / git / 编译工具）
#   2. 建 2 GiB swap —— 2 GiB 内存跑 torch + MiniLM 模型，不加 swap 极易被 OOM 杀掉
#   3. 建 blog 用户 + /home/blog/my_blog 目录
#   4. 装 nginx 站点配置、关掉默认站点
#   5. 装 systemd 服务单元（此时还不启动，等代码上传）
# ============================================================================
set -euo pipefail

APP_USER=blog
APP_DIR=/home/blog/my_blog

log() { echo -e "\n\033[1;32m==> $*\033[0m"; }
warn() { echo -e "\033[1;33m!! $*\033[0m"; }

if [ "$(id -u)" -ne 0 ]; then
    echo "请用 root 运行：sudo bash $0" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
log "1/5 安装系统依赖"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y --no-install-recommends \
    python3 python3-venv python3-dev python3-pip \
    nginx git curl ca-certificates build-essential

python3 --version

# ---------------------------------------------------------------------------
log "2/5 配置 swap"
if swapon --show | grep -q '/swapfile'; then
    echo "swap 已存在，跳过"
else
    fallocate -l 2G /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1M count=2048 status=none
    chmod 600 /swapfile
    mkswap /swapfile >/dev/null
    swapon /swapfile
    grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
    sysctl -w vm.swappiness=20 >/dev/null
    grep -q '^vm.swappiness' /etc/sysctl.conf || echo 'vm.swappiness=20' >> /etc/sysctl.conf
    echo "已创建 2 GiB swap"
fi
free -h

# ---------------------------------------------------------------------------
log "3/5 创建应用用户与目录"
if id -u "$APP_USER" >/dev/null 2>&1; then
    echo "用户 $APP_USER 已存在"
else
    useradd -m -s /bin/bash "$APP_USER"
    echo "已创建用户 $APP_USER"
fi
# nginx(www-data) 需要能穿过 /home/blog 读静态文件
chmod 755 /home/"$APP_USER"
mkdir -p "$APP_DIR" "$APP_DIR/backend/logs" "$APP_DIR/backend/data/chroma"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# ---------------------------------------------------------------------------
log "4/5 安装 Nginx 站点"
if [ -f /tmp/myblog-nginx.conf ]; then
    install -m 644 /tmp/myblog-nginx.conf /etc/nginx/sites-available/myblog
else
    warn "未找到 /tmp/myblog-nginx.conf，跳过站点配置"
fi
ln -sf /etc/nginx/sites-available/myblog /etc/nginx/sites-enabled/myblog
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable nginx >/dev/null 2>&1 || true
systemctl restart nginx

# ---------------------------------------------------------------------------
log "5/5 安装 systemd 服务"
if [ -f /tmp/myblog-blog.service ]; then
    install -m 644 /tmp/myblog-blog.service /etc/systemd/system/blog.service
    systemctl daemon-reload
else
    warn "未找到 /tmp/myblog-blog.service，跳过服务配置"
fi

touch /var/lib/myblog-setup.done

log "服务器初始化完成"
echo "下一步：回到本机运行 deploy/deploy.ps1 上传代码并启动服务"
