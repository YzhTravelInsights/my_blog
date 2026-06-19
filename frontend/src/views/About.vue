<template>
  <div class="max-w-2xl mx-auto">
    <div v-if="loading" class="text-center text-gray-400 py-10">加载中...</div>
    <div v-else class="prose max-w-none" v-html="renderedContent"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAbout } from '../api/articles'
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
