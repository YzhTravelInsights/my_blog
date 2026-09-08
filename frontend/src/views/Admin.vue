<!--
  管理后台（/admin）— 仅博主可用
  携 ?owner_token= 访问自动登录，或输入 OWNER_SECRET（存浏览器本地）后
  拉取 /api/admin/summary：
  后台数据（文章/分类/标签/评论/记忆/印象/RAG 索引/好感度）+ 系统运行信息。
-->
<template>
  <div class="flex justify-center px-2">
    <!-- 未登录 -->
    <div v-if="!token" class="w-full max-w-md mt-10 glass-card p-6">
      <h2 class="text-lg font-bold text-ink flex items-center gap-2">
        <span class="nav-logo">⚙️</span> 管理后台
      </h2>
      <p class="text-xs text-sub mt-1.5 leading-relaxed">
        输入 <code class="text-primary-deep">OWNER_SECRET</code> 验证身份后查看后台数据与系统运行信息，
        或访问时携带 <code class="text-primary-deep">?owner_token=OWNER_SECRET</code> 自动登录。
      </p>
      <input
        v-model="secretInput"
        type="password"
        class="glass-input w-full mt-4 py-2"
        placeholder="OWNER_SECRET"
        @keyup.enter="login"
      />
      <button class="btn-primary w-full mt-3 py-2" :disabled="!secretInput.trim()" @click="login">
        验证身份
      </button>
    </div>

    <!-- 已登录：仪表盘 -->
    <div v-else class="w-full max-w-3xl mt-4 space-y-4">
      <!-- 头部 -->
      <div class="glass-card p-4 flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-2">
          <span class="text-lg">⚙️</span>
          <span class="font-bold text-ink">管理后台</span>
          <span
            v-if="affinity"
            class="text-xs px-2 py-0.5 rounded-full"
            :style="{ background: 'color-mix(in srgb, var(--c-primary) 18%, transparent)', color: 'var(--c-primary-deep)' }"
          >💞 {{ affinity.level_name }} · {{ affinity.interaction_count }} 次互动</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="btn-ghost px-3 py-1 text-xs" :disabled="loading" @click="load">
            {{ loading ? '加载中…' : '🔄 刷新' }}
          </button>
          <button class="btn-ghost px-3 py-1 text-xs" @click="handleLogout">退出</button>
        </div>
      </div>

      <div v-if="error" class="glass-card p-4 text-sm text-center" style="color: #e06666">
        {{ error }}
      </div>

      <template v-if="data">
        <!-- 后台数据 -->
        <div class="glass-card p-4">
          <h3 class="text-sm font-semibold text-sub mb-3">📊 后台数据</h3>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div v-for="c in contentCards" :key="c.label" class="stat-item">
              <span class="stat-num">{{ c.value }}</span>
              <span class="stat-label">{{ c.label }}</span>
            </div>
          </div>
        </div>

        <!-- 文章管理 -->
        <div class="glass-card p-4">
          <h3 class="text-sm font-semibold text-sub mb-3">
            📄 文章管理（{{ (data.content.recent_articles || []).length }}）
          </h3>
          <ul class="space-y-2 text-sm">
            <li v-for="a in data.content.recent_articles || []" :key="a.id" class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2 min-w-0">
                <a :href="`#/article/${a.id}`" class="text-ink hover:text-primary-deep truncate" :title="a.title">{{ a.title }}</a>
                <span class="chip shrink-0">{{ a.category }}</span>
                <span class="text-xs text-sub/60 shrink-0">{{ a.date }}</span>
              </div>
              <button
                class="del-btn text-xs shrink-0"
                :disabled="deleting === a.id"
                :title="`删除《${a.title}》`"
                @click="handleDeleteArticle(a)"
              >{{ deleting === a.id ? '…' : '🗑️ 删除' }}</button>
            </li>
            <li v-if="!data.content.recent_articles?.length" class="text-sub/50 text-xs">暂无文章</li>
          </ul>
        </div>

        <!-- 分类 / 标签 -->
        <div class="glass-card p-4">
          <h3 class="text-sm font-semibold text-sub mb-3">🏷️ 分类与标签</h3>
          <div class="text-xs text-sub mb-1.5">分类</div>
          <div class="flex flex-wrap gap-1.5 mb-3">
            <span v-for="c in data.content.category_counts || []" :key="c.name" class="chip">{{ c.name }} × {{ c.count }}</span>
            <span v-if="!data.content.category_counts?.length" class="text-sub/50 text-xs">无</span>
          </div>
          <div class="text-xs text-sub mb-1.5">标签</div>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="t in data.content.tag_counts || []" :key="t.name" class="chip">#{{ t.name }} × {{ t.count }}</span>
            <span v-if="!data.content.tag_counts?.length" class="text-sub/50 text-xs">无</span>
          </div>
        </div>

        <!-- 评论管理 -->
        <div class="glass-card p-4">
          <h3 class="text-sm font-semibold text-sub mb-3">
            💬 评论管理（{{ (data.content.recent_comments || []).length }}）
          </h3>
          <ul class="space-y-2 text-sm">
            <li v-for="c in data.content.recent_comments || []" :key="c.id" class="border-b border-border-soft/60 pb-2 last:border-0">
              <div class="flex items-center justify-between gap-2">
                <div class="flex items-center gap-2 min-w-0">
                  <span class="font-medium text-ink shrink-0">{{ c.nickname }}</span>
                  <span
                    v-if="c.is_private"
                    class="text-[10px] px-1.5 py-0.5 rounded-full shrink-0"
                    style="background: color-mix(in srgb, var(--c-lav) 20%, transparent); color: var(--c-lav)"
                  >私密</span>
                  <span class="text-xs text-sub/60 shrink-0">{{ c.created_at }}</span>
                </div>
                <button
                  class="del-btn text-xs shrink-0"
                  :disabled="deleting === 'c' + c.id"
                  :title="`删除 ${c.nickname} 的评论`"
                  @click="handleDeleteComment(c)"
                >{{ deleting === 'c' + c.id ? '…' : '🗑️ 删除' }}</button>
              </div>
              <p class="text-sub text-xs mt-0.5 break-all">{{ c.content }}</p>
              <p class="text-[10px] text-sub/50 mt-0.5">→ {{ c.article_title }}</p>
            </li>
            <li v-if="!data.content.recent_comments?.length" class="text-sub/50 text-xs">暂无评论</li>
          </ul>
        </div>

        <!-- 人格印象 -->
        <div class="glass-card p-4">
          <h3 class="text-sm font-semibold text-sub mb-3">🧠 人格印象</h3>
          <ul class="space-y-2 text-sm">
            <li v-for="im in data.content.recent_impressions || []" :key="im.id" class="flex items-start justify-between gap-3">
              <p class="text-sub text-xs break-all">{{ im.content }}</p>
              <span class="text-xs text-sub/60 shrink-0">{{ im.created_at }}</span>
            </li>
            <li v-if="!data.content.recent_impressions?.length" class="text-sub/50 text-xs">暂无印象</li>
          </ul>
        </div>

        <!-- 系统运行信息 -->
        <div class="glass-card p-4">
          <h3 class="text-sm font-semibold text-sub mb-3">⚙️ 系统运行信息</h3>
          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">后端版本</dt><dd class="text-ink">{{ data.system.version }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">启动时间</dt><dd class="text-ink">{{ startedAtText }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">运行时长</dt><dd class="text-ink">{{ data.system.uptime }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">当前时间</dt><dd class="text-ink">{{ data.system.now }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">API 错误次数</dt><dd class="text-ink" :style="{ color: data.system.api_errors > 0 ? '#e06666' : 'inherit' }">{{ data.system.api_errors }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">Python</dt><dd class="text-ink">{{ data.system.python }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">Flask</dt><dd class="text-ink">{{ data.system.flask }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">平台</dt><dd class="text-ink">{{ data.system.platform }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">主机名</dt><dd class="text-ink">{{ data.system.hostname }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">进程 PID</dt><dd class="text-ink">{{ data.system.pid }}</dd></div>
            <div class="flex justify-between gap-3"><dt class="text-sub shrink-0">数据库大小</dt><dd class="text-ink">{{ data.system.db_size_text }}</dd></div>
          </dl>
          <p class="text-[10px] text-sub/60 mt-3 break-all">DB: {{ data.system.db }}（{{ data.system.db_size_text }}）</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAdminSummary, deleteArticle, deleteComment } from '../api/admin'
import { useOwner } from '../store/owner'

const { token, setToken, logout } = useOwner()
const secretInput = ref('')
const data = ref(null)
const loading = ref(false)
const error = ref('')
const deleting = ref('') // 正在删除的项标识：文章 id / 'c'+评论 id

const affinity = computed(() => data.value?.content?.affinity || null)

const contentCards = computed(() => {
  if (!data.value) return []
  const c = data.value.content
  return [
    { label: '文章', value: c.articles },
    { label: '分类', value: c.categories },
    { label: '标签', value: c.tags },
    { label: '评论', value: c.comments },
    { label: '私密评论', value: c.private_comments },
    { label: '长期记忆', value: c.memory },
    { label: '人格印象', value: c.impressions },
    { label: 'RAG 索引', value: c.indexed },
  ]
})

const startedAtText = computed(() => {
  const s = data.value?.system?.started_at
  if (!s) return '未知'
  return new Date(s * 1000).toLocaleString('zh-CN', { hour12: false })
})

onMounted(() => {
  if (token.value) load()
})

async function login() {
  const s = secretInput.value.trim()
  if (!s) return
  setToken(s)
  secretInput.value = ''
  await load()
}

function handleLogout() {
  logout()
  data.value = null
  error.value = ''
}

// 密钥无效：清登录态回登录框
function handleAuthFail() {
  handleLogout()
  secretInput.value = ''
  window.alert('OWNER_SECRET 无效，请重新输入')
}

async function load() {
  if (!token.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await getAdminSummary(token.value)
    if (res.code === 2) {
      handleAuthFail()
      return
    }
    if (res.code === 0) {
      data.value = res.data
    } else {
      error.value = res.msg || '加载失败'
    }
  } catch {
    error.value = '无法连接后端，请确认后端已启动'
  } finally {
    loading.value = false
  }
}

// 删除文章：二次确认 → 调后端 → 刷新
async function handleDeleteArticle(a) {
  if (!window.confirm(`确定删除文章《${a.title}》吗？\n将同时删除文件、知识库索引和该文章的全部评论。`)) return
  deleting.value = a.id
  try {
    const res = await deleteArticle(a.id, token.value)
    if (res.code === 2) { handleAuthFail(); return }
    if (res.code === 0) {
      await load()
      window.alert(res.data?.hint || '已删除')
    } else {
      window.alert(res.msg || '删除失败')
    }
  } catch {
    window.alert('无法连接后端，请确认后端已启动')
  } finally {
    deleting.value = ''
  }
}

// 删除单条评论（含回复）：二次确认 → 调后端 → 刷新
async function handleDeleteComment(c) {
  if (!window.confirm(`确定删除「${c.nickname}」的这条评论吗？\n${c.content.slice(0, 40)}${c.content.length > 40 ? '…' : ''}\n（其回复会一并删除）`)) return
  deleting.value = 'c' + c.id
  try {
    const res = await deleteComment(c.id, token.value)
    if (res.code === 2) { handleAuthFail(); return }
    if (res.code === 0) {
      await load()
      window.alert(res.data?.hint || '已删除')
    } else {
      window.alert(res.msg || '删除失败')
    }
  } catch {
    window.alert('无法连接后端，请确认后端已启动')
  } finally {
    deleting.value = ''
  }
}
</script>

<style scoped>
@reference "../style.css";

.nav-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.7rem;
  height: 1.7rem;
  border-radius: 999px;
  font-size: 0.9rem;
  background: linear-gradient(135deg, color-mix(in srgb, var(--c-primary) 30%, transparent), color-mix(in srgb, var(--c-star) 20%, transparent));
  border: 1px solid var(--c-border);
}
.del-btn {
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  color: var(--c-sub);
  opacity: 0.75;
  cursor: pointer;
  transition: all 0.18s ease;
}
.del-btn:hover {
  color: #e06666;
  opacity: 1;
  background: color-mix(in srgb, #e06666 10%, transparent);
}
.del-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.stat-item {
  @apply flex flex-col items-center justify-center rounded-xl border border-border-soft bg-surface px-2 py-2.5;
}
.stat-num {
  @apply text-lg font-bold text-primary-deep leading-none;
}
.stat-label {
  @apply text-[11px] text-sub/70 mt-1;
}
</style>
