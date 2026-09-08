<!--
  右侧边栏：两种模式。
  - mode="toc"  ：文章页，渲染 toc store 的目录（锚点滚动）
  - mode="home" ：首页/关于，分类标签筛选（复用 TagFilter）＋ 最新文章
-->
<template>
  <aside class="space-y-4">
    <!-- 文章页：目录 -->
    <template v-if="mode === 'toc'">
      <div class="glass-card p-4">
        <h3 class="text-sm font-semibold text-sub mb-3">📑 目录</h3>
        <nav v-if="tocState.items.length" class="space-y-1">
          <a
            v-for="item in tocState.items"
            :key="item.id"
            :href="`#${item.id}`"
            class="toc-link block text-xs leading-relaxed transition-colors"
            :class="`toc-level-${item.level}`"
            @click.prevent="scrollToHeading(item.id)"
          >
            {{ item.text }}
          </a>
        </nav>
        <p v-else class="text-xs text-sub/60">本文暂无目录</p>
      </div>
    </template>

    <!-- 首页 / 关于：分类标签 + 最新文章 -->
    <template v-else>
      <div class="glass-card p-4">
        <h3 class="text-sm font-semibold text-sub mb-3">筛选</h3>
        <TagFilter
          :categories="blog.categories"
          :tags="blog.tags"
          :active-category="blog.activeCategory"
          :active-tag="blog.activeTag"
          @select-category="setCategory"
          @select-tag="toggleTag"
        />
      </div>

      <div class="glass-card p-4">
        <h3 class="text-sm font-semibold text-sub mb-3">✨ 最新文章</h3>
        <ul class="space-y-2">
          <li v-for="a in blog.recentArticles" :key="a.id">
            <router-link :to="`/article/${a.id}`" class="recent-link">
              <span class="truncate">{{ a.title }}</span>
              <span class="text-[10px] text-sub/50 shrink-0">{{ String(a.date).slice(0, 7) }}</span>
            </router-link>
          </li>
        </ul>
        <p v-if="!blog.recentArticles.length" class="text-xs text-sub/60">暂无文章</p>
      </div>

      <div class="glass-card p-4">
        <h3 class="text-sm font-semibold text-sub mb-3">📖 最近阅读</h3>
        <ul v-if="visit.history.length" class="space-y-2">
          <li v-for="h in visit.history" :key="h.id">
            <router-link :to="`/article/${h.id}`" class="recent-link">
              <span class="truncate">{{ h.title }}</span>
              <span class="text-[10px] text-sub/50 shrink-0">{{ formatTime(h.time) }}</span>
            </router-link>
          </li>
        </ul>
        <p v-else class="text-xs text-sub/60">还没有阅读记录</p>
      </div>
    </template>
  </aside>
</template>

<script setup>
import { onMounted } from 'vue'
import { blog, setCategory, toggleTag, loadStats } from '../store/blog'
import { tocState } from '../store/toc'
import { visit } from '../store/visit'
import TagFilter from './TagFilter.vue'

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}/${pad(d.getDate())}`
}

// 目录锚点：页内平滑滚动（hash 路由下普通 <a href="#id"> 会导航走导致路由失效）
function scrollToHeading(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

defineProps({
  mode: { type: String, default: 'home' }, // 'home' | 'toc'
})

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
@reference "../style.css";

.toc-link {
  color: var(--c-sub);
}
.toc-link:hover {
  color: var(--c-primary-deep);
}
.toc-level-2 {
  padding-left: 0.5rem;
}
.toc-level-3 {
  padding-left: 1.25rem;
}
.toc-level-4 {
  padding-left: 2rem;
}

.recent-link {
  @apply flex items-center justify-between gap-2 text-xs text-sub transition-colors;
}
.recent-link:hover {
  color: var(--c-primary-deep);
}
</style>
