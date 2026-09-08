<!--
  左侧边栏：个人卡片（头像/站名/简介/学校等）＋ 站点统计 ＋ 社交链接 ＋ 主人按钮 ＋ 公告。
  全部信息读自 config/site.js；统计读自 store/blog.js。
-->
<template>
  <aside class="space-y-4">
    <!-- 个人卡片 -->
    <div class="glass-card glass-card-hover p-5">
      <div class="flex flex-col items-center text-center">
        <img
          :src="site.avatar"
          :alt="site.name"
          class="w-20 h-20 rounded-full object-cover ring-2 ring-primary/60 ring-offset-2 ring-offset-[var(--bg-base)] shadow-glow"
        />
        <h2 class="mt-3 text-lg font-bold text-ink">{{ site.name }}</h2>
        <p class="text-xs text-sub mt-0.5">{{ site.slogan }}</p>
      </div>

      <div class="mt-4 space-y-1 text-center text-xs text-sub">
        <p>{{ site.owner.nickname }}</p>
        <p>{{ site.owner.school }}</p>
        <p>{{ site.owner.location }} · {{ site.owner.motto }}</p>
      </div>

      <p class="mt-3 text-xs text-sub leading-relaxed text-center">{{ site.intro }}</p>
    </div>

    <!-- 站点统计 -->
    <div class="glass-card p-4">
      <h3 class="text-sm font-semibold text-sub mb-3">站点统计</h3>
      <div class="grid grid-cols-2 gap-2">
        <div class="stat-item">
          <span class="stat-num">{{ blog.stats.articles }}</span>
          <span class="stat-label">文章</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ blog.stats.archives }}</span>
          <span class="stat-label">归档</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ blog.stats.categories }}</span>
          <span class="stat-label">分类</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ blog.stats.tags }}</span>
          <span class="stat-label">标签</span>
        </div>
      </div>
    </div>

    <!-- 社交链接：悬浮自绘提示账号，点击复制 / 跳转 -->
    <div class="glass-card p-4">
      <h3 class="text-sm font-semibold text-sub mb-3">找到我</h3>
      <div class="flex justify-center gap-3">
        <a
          v-for="s in site.socials"
          :key="s.name"
          :href="s.url || undefined"
          :aria-label="s.title"
          :target="isExternal(s.url) ? '_blank' : undefined"
          :rel="isExternal(s.url) ? 'noopener noreferrer' : undefined"
          class="social-link group relative"
          :class="{ 'social-link-disabled': !s.url && !s.copy }"
          @mouseenter="hoverSocial(s)"
          @mouseleave="leaveSocial(s)"
          @click.prevent="onSocialClick(s)"
        >
          <IconSocial :name="s.icon" />
          <span class="sr-only">{{ s.name }}</span>
          <span v-if="isTipShown(s)" class="social-tip">{{ tip.text }}</span>
        </a>
      </div>
    </div>

    <!-- 主人按钮：关于本站访客可见；管理 / 写新文章仅主人可见（其余人体验不变） -->
    <div class="space-y-2">
      <router-link to="/about" class="btn-primary w-full">关于本站</router-link>
      <div v-if="isOwner" class="grid grid-cols-2 gap-2">
        <router-link to="/admin" class="btn-ghost">管理</router-link>
        <router-link to="/write" class="btn-ghost">写新文章</router-link>
      </div>
    </div>

    <!-- 公告板 -->
    <div class="glass-card p-4">
      <h3 class="text-sm font-semibold text-sub mb-2">📢 公告</h3>
      <p class="text-xs text-sub leading-relaxed">{{ site.announcement }}</p>
    </div>

  </aside>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { site } from '../config/site'
import { blog, loadStats } from '../store/blog'
import IconSocial from './IconSocial.vue'
import { useOwner } from '../store/owner'

const { isOwner } = useOwner()

onMounted(() => {
  loadStats()
})

function isExternal(url) {
  return !!url && /^https?:/.test(url)
}

// —— 悬浮 / 点击提示：统一显示在对应图标下方 ——
// 用 name 字符串定位提示归属，而非保存对象引用（对象比较依赖 v-for 每次迭代
// 返回同一引用，测试环境不保证；字符串比较两者都稳）
const tip = ref(null) // { name, text }
const tipPinned = ref(false)
let tipTimer = null

function isTipShown(s) {
  return tip.value && tip.value.name === s.name
}

function hoverSocial(s) {
  if (tipPinned.value) return // 点击固定展示期间不覆盖
  tip.value = { name: s.name, text: s.title }
}

function leaveSocial(s) {
  if (tipPinned.value) return
  if (tip.value && tip.value.name === s.name) tip.value = null
}

function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).catch(() => {})
  } else {
    // 非安全上下文（如 http 局域网访问）fallback：临时 textarea + execCommand
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    try {
      document.execCommand('copy')
    } catch (e) {
      /* 复制失败不阻塞其他行为 */
    }
    document.body.removeChild(ta)
  }
}

function onSocialClick(s) {
  if (s.copy) {
    copyText(s.copy)
    // 在图标下方固定展示「已复制」提示 2.2 秒
    tip.value = { name: s.name, text: s.toast || `已复制 ${s.title}` }
    tipPinned.value = true
    clearTimeout(tipTimer)
    tipTimer = setTimeout(() => {
      tipPinned.value = false
      tip.value = null
    }, 2200)
  }
  if (s.url && window.open) {
    window.open(s.url, '_blank', 'noopener,noreferrer')
  }
}
</script>

<style scoped>
@reference "../style.css";

.stat-item {
  @apply flex flex-col items-center justify-center rounded-xl border border-border-soft bg-surface px-2 py-2.5;
}
.stat-num {
  @apply text-lg font-bold text-primary-deep leading-none;
}
.stat-label {
  @apply text-[11px] text-sub/70 mt-1;
}

.social-link {
  @apply flex items-center justify-center w-10 h-10 rounded-full border border-border-soft bg-surface text-sub
         transition-all duration-300;
}
.social-link:hover {
  @apply text-primary-deep border-primary/50 shadow-glow -translate-y-0.5;
}
.social-link-disabled {
  @apply cursor-not-allowed opacity-70;
}
.social-link :deep(.icon-social svg) {
  width: 1.15rem;
  height: 1.15rem;
}

/* 悬浮提示 / 复制反馈：自绘，显示在图标正下方，紧跟对应图标 */
.social-tip {
  @apply absolute top-[calc(100%+7px)] left-1/2 -translate-x-1/2 whitespace-nowrap rounded-lg px-2.5 py-1 text-xs text-ink
         shadow-lg;
  background: color-mix(in srgb, var(--c-surface) 97%, var(--c-ink));
  border: 1px solid var(--c-border);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.16);
  z-index: 40;
  animation: tip-in 0.16s ease;
}
.social-tip::before {
  /* 指向图标的小箭头 */
  content: '';
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 5px solid var(--c-border);
}
.social-tip::after {
  content: '';
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 4px solid var(--c-surface);
}
@keyframes tip-in {
  from {
    opacity: 0;
    transform: translate(-50%, -4px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>
