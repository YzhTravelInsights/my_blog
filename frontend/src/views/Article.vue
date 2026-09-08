<!--
  文章页：玻璃头部 ＋ 目录锚点（marked 自定义 heading 收集写入 toc store）＋ 正文 ＋ 上下篇 ＋ 评论区。
-->
<template>
  <div v-if="loading" class="text-center text-sub py-16">
    <span class="animate-spin inline-block">✦</span>
    <p class="mt-2 text-sm">正在加载文章…</p>
  </div>

  <div v-else-if="!article" class="text-center text-sub py-16">
    <p class="text-3xl mb-2">🫥</p>
    <p class="text-sm">文章不存在或已被移除</p>
  </div>

  <div v-else class="max-w-3xl mx-auto">
    <!-- 头部卡片 -->
    <div class="glass-card p-6 mb-6">
      <div class="flex items-center gap-2 text-xs text-sub mb-3">
        <span class="chip">{{ article.category }}</span>
        <span>{{ article.date }}</span>
      </div>
      <h1 class="text-2xl md:text-3xl font-bold text-ink leading-snug">{{ article.title }}</h1>
      <div v-if="article.tags?.length" class="flex flex-wrap gap-1.5 mt-3">
        <span v-for="t in article.tags" :key="t" class="chip">#{{ t }}</span>
      </div>
    </div>

    <!-- 正文 -->
    <div class="prose max-w-none" v-html="renderedContent"></div>

    <!-- 上下篇 -->
    <div class="flex justify-between mt-10 pt-6 border-t border-border-soft text-sm">
      <router-link
        v-if="article.prev"
        :to="`/article/${article.prev.id}`"
        class="text-primary-deep hover:underline max-w-[45%] truncate"
      >&larr; {{ article.prev.title }}</router-link>
      <span v-else class="text-sub/50">&larr; 没有了</span>
      <router-link
        v-if="article.next"
        :to="`/article/${article.next.id}`"
        class="text-primary-deep hover:underline max-w-[45%] truncate"
      >{{ article.next.title }} &rarr;</router-link>
      <span v-else class="text-sub/50">没有了 &rarr;</span>
    </div>

    <!-- 评论区 -->
    <CommentSection :articleId="article.id" class="mt-10" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getArticle } from '../api/articles'
import { marked } from 'marked'
import hljs from 'highlight.js'
import CommentSection from '../components/CommentSection.vue'
import { setToc, clearToc } from '../store/toc'
import { recordArticleView } from '../store/visit'

const props = defineProps({ id: String })
const route = useRoute()
const articleId = computed(() => props.id || route.params.id)

const article = ref(null)
const loading = ref(true)

// ---------------------------------------------------------------------------
// marked 渲染：代码高亮 ＋ 标题锚点 id ＋ TOC 收集
// render() 中临时打开 tocCollect，parse 结束后写回 toc store，避免重复收集。
// ---------------------------------------------------------------------------
let tocCollect = null
let slugCounts = {} // 锚点 id 去重计数；每篇文章渲染前重置

function slugify(text) {
  const base = text
    .toLowerCase()
    .trim()
    .replace(/[`~!@#$%^&*()+=|{}\[\];:'",.<>/?]+/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
  slugCounts[base] = (slugCounts[base] || 0) + 1
  return slugCounts[base] === 1 ? base : `${base}-${slugCounts[base]}`
}

marked.use({
  renderer: {
    heading({ tokens, depth }) {
      const text = this.parser.parseInline(tokens)
      const id = slugify(text)
      if (tocCollect) tocCollect.push({ id, text, level: depth })
      return `<h${depth} id="${id}">${text}</h${depth}>`
    },
  },
})

marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
})

function render(content) {
  tocCollect = []
  slugCounts = {} // 组件复用（上下篇切换）后重新计号，避免标题锚点 id 错乱
  const html = marked.parse(content)
  setToc(tocCollect)
  tocCollect = null
  return html
}

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return render(article.value.content)
})

// 竞态保护：快速连点上下篇时，旧请求结果不得覆盖新文章
let loadSeq = 0

async function loadArticle(id) {
  const seq = ++loadSeq
  loading.value = true
  article.value = null
  clearToc()
  const res = await getArticle(id)
  if (seq !== loadSeq) return // 已被更新的导航取代
  if (res.code === 0) {
    article.value = res.data
    recordArticleView(article.value.id, article.value.title)
  }
  loading.value = false
}

onMounted(() => loadArticle(articleId.value))

// 上下篇切换复用同一组件实例，onMounted 不会重跑——监听路由参数重新加载
watch(articleId, (id) => {
  if (id) window.scrollTo?.(0, 0)
  loadArticle(id)
})

onUnmounted(() => {
  clearToc()
})
</script>
