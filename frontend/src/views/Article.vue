<template>
  <div v-if="loading" class="text-center text-gray-400 py-10">加载中...</div>
  <div v-else-if="!article" class="text-center text-gray-400 py-10">文章不存在</div>
  <div v-else class="max-w-3xl mx-auto">
    <!-- 头部 -->
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm text-gray-400 mb-2">
        <span class="bg-blue-100 text-blue-700 px-2 py-0.5 rounded">{{ article.category }}</span>
        <span>{{ article.date }}</span>
      </div>
      <h1 class="text-2xl font-bold text-gray-900">{{ article.title }}</h1>
      <div class="flex gap-1 mt-2" v-if="article.tags?.length">
        <span v-for="t in article.tags" :key="t" class="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{{ t }}</span>
      </div>
    </div>

    <!-- 正文 -->
    <div class="prose max-w-none" v-html="renderedContent"></div>

    <!-- 上下篇 -->
    <div class="flex justify-between mt-10 pt-6 border-t border-gray-200 text-sm">
      <router-link v-if="article.prev" :to="`/article/${article.prev.id}`" class="text-blue-600 hover:underline">
        &larr; {{ article.prev.title }}
      </router-link>
      <span v-else class="text-gray-300">&larr; 没有了</span>
      <router-link v-if="article.next" :to="`/article/${article.next.id}`" class="text-blue-600 hover:underline">
        {{ article.next.title }} &rarr;
      </router-link>
      <span v-else class="text-gray-300">没有了 &rarr;</span>
    </div>

    <!-- 评论区 -->
    <CommentSection :articleId="article.id" class="mt-10" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getArticle } from '../api/articles'
import { marked } from 'marked'
import hljs from 'highlight.js'
import CommentSection from '../components/CommentSection.vue'

const props = defineProps({ id: String })
const route = useRoute()
const articleId = computed(() => props.id || route.params.id)

const article = ref(null)
const loading = ref(true)

marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
})

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return marked.parse(article.value.content)
})

onMounted(async () => {
  const res = await getArticle(articleId.value)
  if (res.code === 0) article.value = res.data
  loading.value = false
})
</script>
