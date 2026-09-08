<!--
  首页：搜索框 ＋ 文章列表 ＋ 分页。
  状态统一来自 store/blog.js（分类/标签筛选在右侧栏操作）。
-->
<template>
  <div>
    <!-- 搜索 -->
    <div class="mb-5">
      <div class="relative">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sub/60 text-sm pointer-events-none">🔍</span>
        <input
          v-model="blog.searchText"
          @keyup.enter="doSearch"
          placeholder="搜索文章…"
          class="glass-input pl-9"
        />
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="blog.loading" class="text-center text-sub py-16">
      <span class="animate-spin inline-block">✦</span>
      <p class="mt-2 text-sm">萤火正在收集文章…</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="blog.articles.length === 0" class="text-center text-sub/70 py-16">
      <p class="text-3xl mb-2">🌫️</p>
      <p class="text-sm">这里还很安静，换个筛选试试？</p>
    </div>

    <!-- 列表 -->
    <div v-else class="space-y-4">
      <ArticleCard v-for="a in blog.articles" :key="a.id" :article="a" />
    </div>

    <!-- 分页 -->
    <div v-if="blog.pagination.total_pages > 1" class="flex justify-center items-center gap-3 mt-8">
      <button
        @click="goPage(blog.pagination.page - 1)"
        :disabled="blog.pagination.page <= 1"
        class="btn-ghost px-4 py-1.5"
      >上一页</button>
      <span class="text-sm text-sub">{{ blog.pagination.page }} / {{ blog.pagination.total_pages }}</span>
      <button
        @click="goPage(blog.pagination.page + 1)"
        :disabled="blog.pagination.page >= blog.pagination.total_pages"
        class="btn-ghost px-4 py-1.5"
      >下一页</button>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { blog, fetchArticles, doSearch, goPage } from '../store/blog'
import ArticleCard from '../components/ArticleCard.vue'

onMounted(() => {
  fetchArticles()
})
</script>
