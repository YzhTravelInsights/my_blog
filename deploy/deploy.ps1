<#
.SYNOPSIS
    把 myblog 部署到阿里云 ECS（本机 Windows -> Ubuntu 服务器）

.DESCRIPTION
    一键完成：构建前端 -> 打包代码 -> 上传 -> 服务器初始化（首次）-> 装依赖 -> 重建索引 -> 重启服务

.EXAMPLE
    # 完整部署（首次会自动先做服务器初始化）
    pwsh deploy/deploy.ps1

.EXAMPLE
    # 只更新前端 + 代码，跳过前端构建
    pwsh deploy/deploy.ps1 -SkipBuild

.EXAMPLE
    # 强制重新打包模型缓存上传
    pwsh deploy/deploy.ps1 -Force
#>
[CmdletBinding()]
param(
    [string]$Server   = '47.94.91.5',
    [string]$SshUser  = 'root',
    [switch]$SkipBuild,
    [switch]$SkipModels,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$Root       = Split-Path -Parent $PSScriptRoot
$DeployDir  = Join-Path $Root '.deploy'
$KeyFile    = Join-Path $DeployDir 'id_ed25519'
$KnownHosts = Join-Path $DeployDir 'known_hosts'
$Stage      = Join-Path $DeployDir 'stage'
$CodeTar    = Join-Path $DeployDir 'myblog-code.tar.gz'
$ModelTar   = Join-Path $DeployDir 'myblog-models.tar.gz'
$EnvFile    = Join-Path $DeployDir 'server.env'
$Target     = "$SshUser@$Server"

$SshArgs = @(
    '-i', $KeyFile
    '-o', 'IdentitiesOnly=yes'
    '-o', "UserKnownHostsFile=$KnownHosts"
    '-o', 'StrictHostKeyChecking=accept-new'
    '-o', 'ServerAliveInterval=30'
    '-o', 'BatchMode=yes'
    '-o', 'PreferredAuthentications=publickey'
)

function Write-Step([string]$Text) { Write-Host "`n==> $Text" -ForegroundColor Green }
function Write-Warn2([string]$Text) { Write-Host "!! $Text" -ForegroundColor Yellow }

# PowerShell 5.1 会把原生程序的 stderr 包装成 ErrorRecord；在
# $ErrorActionPreference='Stop' 下这会直接变成终止错误（nginx 的 "syntax is ok"
# 就是写 stderr 的），导致脚本在完全正常的步骤上假失败。
# 所以调用原生程序时临时切到 Continue，靠 $LASTEXITCODE 判成败。
function Invoke-Native {
    param([scriptblock]$Block)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Block } finally { $ErrorActionPreference = $prev }
}

function Invoke-Remote([string]$Command) {
    $output = Invoke-Native { & ssh @SshArgs $Target $Command 2>&1 }
    $code = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }
    if ($code -ne 0) { throw "远程命令失败（exit $code）：$Command" }
}

# scp 在本机环境下偶发「返回 0 但文件没传过去」，所以每次上传都校验 MD5 并重试。
function Send-File {
    param([string]$Local, [string]$Remote)
    if (-not (Test-Path $Local)) { throw "本地文件不存在：$Local" }
    $localMd5 = (Get-FileHash -Algorithm MD5 -Path $Local).Hash.ToLower()
    $name = Split-Path -Leaf $Local
    for ($i = 1; $i -le 4; $i++) {
        Invoke-Native { & scp @SshArgs $Local "${Target}:$Remote" 2>&1 } | Out-Null
        $remoteMd5 = Invoke-Native { & ssh @SshArgs $Target "md5sum $Remote 2>/dev/null" }
        $remoteMd5 = if ($remoteMd5) { ($remoteMd5 -split '\s+')[0].Trim().ToLower() } else { '' }
        if ($remoteMd5 -eq $localMd5) {
            Write-Host ("  [ok] {0}  ({1})" -f $name, $localMd5.Substring(0, 8)) -ForegroundColor DarkGray
            return
        }
        Write-Host ("  [retry {0}/4] {1} 校验不一致（远端 '{2}'）" -f $i, $name, $remoteMd5) -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
    throw "上传失败（重试 4 次仍不一致）：$Local -> $Remote"
}

# ---------------------------------------------------------------------------
Write-Step "检查前置条件"
foreach ($f in @($KeyFile, (Join-Path $PSScriptRoot 'server_setup.sh'),
                 (Join-Path $PSScriptRoot 'server_install_app.sh'),
                 (Join-Path $PSScriptRoot 'nginx-blog.conf'),
                 (Join-Path $PSScriptRoot 'blog.service'))) {
    if (-not (Test-Path $f)) { throw "缺少文件：$f" }
}
if (-not (Test-Path $EnvFile)) {
    throw @"
缺少 $EnvFile（服务器环境变量，含 DeepSeek Key / OWNER_SECRET）。
先按 deploy/env.production.example 生成该文件，例如：

  OWNER_SECRET=`$(python -c "import secrets;print(secrets.token_hex(32))")
  ADMIN_KEY=`$(python -c "import secrets;print(secrets.token_hex(32))")

该文件已被 .gitignore 忽略，不会进 Git。
"@
}
Write-Host "SSH 目标：$Target"

# ---------------------------------------------------------------------------
if (-not $SkipBuild) {
    Write-Step "构建前端（vite build）"
    Push-Location (Join-Path $Root 'frontend')
    try {
        & npm run build
        if ($LASTEXITCODE -ne 0) { throw "前端构建失败（exit $LASTEXITCODE）" }
    } finally { Pop-Location }
} else {
    Write-Warn2 "已跳过前端构建（-SkipBuild）"
}
if (-not (Test-Path (Join-Path $Root 'frontend\dist\index.html'))) {
    throw "frontend/dist/index.html 不存在，请先执行 npm run build"
}

# ---------------------------------------------------------------------------
Write-Step "打包代码（排除 .git / node_modules / 模型 / 数据库 / 日志）"
if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
$null = New-Item -ItemType Directory -Force -Path $Stage

$excludeDirs = @('.git', 'node_modules', '__pycache__', '.pytest_cache', '.deploy',
                 '.continue', '.claude', '.claude-dev-helper', '.vscode',
                 'models', 'chroma', 'logs', 'venv', '.venv', 'dist-info')
robocopy $Root $Stage /E /XD @excludeDirs /XF '.env' '*.pyc' /NFL /NDL /NJH /NJS /NP /R:1 /W:1 | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy 打包失败（exit $LASTEXITCODE）" }

if (Test-Path $CodeTar) { Remove-Item $CodeTar -Force }
& tar -czf $CodeTar -C $Stage .
if ($LASTEXITCODE -ne 0) { throw 'tar 打包失败' }
$codeMb = [math]::Round((Get-Item $CodeTar).Length / 1MB, 2)
Write-Host "代码包：$codeMb MB"

# 自检：确认排除生效，避免把 node_modules（上万个文件）传上去
$listing = & tar -tzf $CodeTar
$bad = $listing | Where-Object { $_ -match 'node_modules|__pycache__|\.pytest_cache|/\.env$' }
if ($bad) {
    throw "打包内容包含应排除的路径，例如：`n" + (($bad | Select-Object -First 5) -join "`n")
}
Write-Host ("打包内容自检通过：{0} 个条目" -f $listing.Count)

# ---------------------------------------------------------------------------
if (-not $SkipModels) {
    $modelSrc = Join-Path $Root 'backend\models'
    if (-not (Test-Path $modelSrc)) {
        Write-Warn2 "本机没有 backend/models，跳过模型上传（服务器 RAG 会降级）"
    } elseif ((Test-Path $ModelTar) -and -not $Force) {
        Write-Host ("复用已有模型包：{0} MB（加 -Force 可重新打包）" -f [math]::Round((Get-Item $ModelTar).Length / 1MB, 2))
    } else {
        Write-Step "打包 embedding 模型缓存（约 87 MB，rag.py 强制离线必须预置）"
        if (Test-Path $ModelTar) { Remove-Item $ModelTar -Force }
        & tar -czf $ModelTar -C $modelSrc .
        if ($LASTEXITCODE -ne 0) { throw 'tar 打包模型失败' }
        Write-Host ("模型包：{0} MB" -f [math]::Round((Get-Item $ModelTar).Length / 1MB, 2))
    }
}

# ---------------------------------------------------------------------------
Write-Step "上传到服务器"
Send-File -Local $CodeTar -Remote '/tmp/myblog-code.tar.gz'
Send-File -Local (Join-Path $PSScriptRoot 'server_setup.sh')       -Remote '/tmp/myblog-server_setup.sh'
Send-File -Local (Join-Path $PSScriptRoot 'server_install_app.sh') -Remote '/tmp/myblog-server_install_app.sh'
Send-File -Local (Join-Path $PSScriptRoot 'nginx-blog.conf')       -Remote '/tmp/myblog-nginx.conf'
Send-File -Local (Join-Path $PSScriptRoot 'blog.service')          -Remote '/tmp/myblog-blog.service'

if ((Test-Path $ModelTar) -and -not $SkipModels) {
    $hasModel = (& ssh @SshArgs $Target 'test -d /home/blog/my_blog/backend/models/models--sentence-transformers--all-MiniLM-L6-v2 && echo yes || echo no').Trim()
    if ($hasModel -eq 'yes' -and -not $Force) {
        Write-Host "服务器已有 embedding 模型缓存，跳过上传（-Force 可强制重传）"
    } else {
        Write-Host "上传模型包（约 80 MB，视上行带宽 1~10 分钟）..."
        Send-File -Local $ModelTar -Remote '/tmp/myblog-models.tar.gz'
    }
}

Send-File -Local $EnvFile -Remote '/tmp/myblog-server.env'

# ---------------------------------------------------------------------------
Write-Step "远程脚本语法自检"
Invoke-Remote 'bash -n /tmp/myblog-server_setup.sh && bash -n /tmp/myblog-server_install_app.sh && echo "  语法检查通过"'

# ---------------------------------------------------------------------------
Write-Step "检查服务器是否已初始化"
$marker = (& ssh @SshArgs $Target 'test -f /var/lib/myblog-setup.done && echo yes || echo no').Trim()
if ($marker -ne 'yes') {
    Write-Step "首次部署：安装 nginx / python / swap / systemd（约 2~3 分钟）"
    Invoke-Remote 'bash /tmp/myblog-server_setup.sh'
} else {
    Write-Host "服务器已初始化，跳过"
    # 配置有更新时热更新
    Invoke-Remote 'install -m 644 /tmp/myblog-nginx.conf /etc/nginx/sites-available/myblog && nginx -t && systemctl reload nginx'
    Invoke-Remote 'install -m 644 /tmp/myblog-blog.service /etc/systemd/system/blog.service && systemctl daemon-reload'
}

# ---------------------------------------------------------------------------
Write-Step "部署应用（解包 / 装依赖 / 建索引 / 重启）"
Invoke-Remote 'bash /tmp/myblog-server_install_app.sh'

# ---------------------------------------------------------------------------
Write-Step "部署完成"
Write-Host @"
访问地址：  http://$Server/
主人入口：  http://$Server/#/chat?owner_token=<你 .env 里的 OWNER_SECRET>
健康检查：  http://$Server/api/articles

查看日志：
  ssh $Target 'journalctl -u blog -f'
  ssh $Target 'tail -f /home/blog/my_blog/backend/logs/gunicorn-error.log'
"@ -ForegroundColor Cyan
