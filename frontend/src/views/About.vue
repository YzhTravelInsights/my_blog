<!--
  关于页：顶部本地横幅图 ＋ 磨砂玻璃卡片内的 markdown 正文。
-->
<template>
  <div class="max-w-3xl mx-auto">
    <!-- 横幅装饰图（本地资源） -->
    <div class="glass-card overflow-hidden mb-6">
      <img src="/firefly-banner-1.jpg" alt="流萤" class="w-full h-44 md:h-56 object-cover" />
      <div class="px-6 py-4 border-t border-border-soft flex items-center gap-2 text-xs text-sub">
        <span>✨</span>
        <span>{{ site.slogan }}</span>
      </div>
    </div>

    <div class="glass-card p-6 md:p-8">
      <div v-if="loading" class="text-center text-sub py-14">
        <span class="animate-spin inline-block">✦</span>
        <p class="mt-2 text-sm">正在加载…</p>
      </div>
      <div v-else class="prose max-w-none" v-html="renderedContent"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAbout } from '../api/articles'
import { site } from '../config/site'
import { marked } from 'marked'

const about = ref(null)
const loading = ref(true)

const renderedContent = computed(() => {
  if (!about.value?.content) return ''
  return marked.parse(about.value.content)
})

onMounted(async () => {
  const res = await getAbout()
  if (res.code === 0) about.value = res.data
  loading.value = false
})
</script>
