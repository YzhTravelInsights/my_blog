<template>
  <div class="flex gap-8">
    <!-- 左侧：文章列表 -->
    <div class="flex-1 min-w-0">
      <!-- 搜索 -->
      <div class="mb-4">
        <input v-model="searchText" @keyup.enter="doSearch" placeholder="搜索文章..."
          class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="text-center text-gray-400 py-10">加载中...</div>

      <!-- 空状态 -->
      <div v-else-if="articles.length === 0" class="text-center text-gray-400 py-10">
        暂无文章
      </div>

      <!-- 列表 -->
      <ArticleCard v-for="a in articles" :key="a.id" :article="a" />

      <!-- 分页 -->
      <div v-if="pagination.total_pages > 1" class="flex justify-center gap-2 mt-6">
        <button @click="goPage(pagination.page - 1)" :disabled="pagination.page <= 1"
          class="px-3 py-1 text-sm border rounded disabled:opacity-30 hover:bg-gray-100">上一页</button>
        <span class="px-3 py-1 text-sm text-gray-500">{{ pagination.page }} / {{ pagination.total_pages }}</span>
        <button @click="goPage(pagination.page + 1)" :disabled="pagination.page >= pagination.total_pages"
          class="px-3 py-1 text-sm border rounded disabled:opacity-30 hover:bg-gray-100">下一页</button>
      </div>
    </div>

    <!-- 右侧：筛选 -->
    <div class="w-52 shrink-0 hidden md:block">
      <TagFilter :categories="filters.categories" :tags="filters.tags"
        :activeCategory="activeCategory" :activeTag="activeTag"
        @select-category="selectCategory" @select-tag="selectTag" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getArticles } from '../api/articles'
import ArticleCard from '../components/ArticleCard.vue'
import TagFilter from '../components/TagFilter.vue'

const articles = ref([])
const loading = ref(true)
const pagination = reactive({ page: 1, page_size: 10, total: 0, total_pages: 1 })
const filters = reactive({ categories: [], tags: [] })

const activeCategory = ref('')
const activeTag = ref('')
const searchText = ref('')

async function fetchData() {
  loading.value = true
  const res = await getArticles({
    page: pagination.page,
    category: activeCategory.value,
    tag: activeTag.value,
    search: searchText.value,
  })
  if (res.code === 0) {
    articles.value = res.data.articles
    Object.assign(pagination, res.data.pagination)
    Object.assign(filters, res.data.filters)
  }
  loading.value = false
}

function selectCategory(cat) {
  activeCategory.value = cat
  pagination.page = 1
  fetchData()
}

function selectTag(tag) {
  activeTag.value = activeTag.value === tag ? '' : tag
  pagination.page = 1
  fetchData()
}

function doSearch() {
  pagination.page = 1
  fetchData()
}

function goPage(p) {
  pagination.page = p
  fetchData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(fetchData)
</script>
