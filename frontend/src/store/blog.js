/**
 * 博客全局状态 —— 文章列表 / 筛选 / 分页 / 侧边栏统计与最新文章
 *
 * 由 Home.vue（列表）、LeftSidebar.vue（统计）、RightSidebar.vue（筛选/最新）共享。
 * 模块单例：桌面三栏与移动端抽屉里重复挂载的侧边栏组件共享同一份状态，
 * 统计接口通过 statsLoaded 保证只请求一次。
 */
import { reactive } from 'vue'
import { getArticles } from '../api/articles'

export const blog = reactive({
  articles: [],
  pagination: { page: 1, page_size: 10, total: 0, total_pages: 1 },
  categories: [],
  tags: [],
  activeCategory: '',
  activeTag: '',
  searchText: '',
  loading: false,

  // 侧边栏统计
  stats: { articles: 0, archives: 0, categories: 0, tags: 0 },
  recentArticles: [],
  statsLoaded: false,
})

/** 拉取文章列表（应用当前筛选/分页） */
export async function fetchArticles() {
  blog.loading = true
  try {
    const res = await getArticles({
      page: blog.pagination.page,
      category: blog.activeCategory,
      tag: blog.activeTag,
      search: blog.searchText,
    })
    if (res.code === 0) {
      blog.articles = res.data.articles
      Object.assign(blog.pagination, res.data.pagination)
      blog.categories = res.data.filters.categories
      blog.tags = res.data.filters.tags
    }
  } finally {
    blog.loading = false
  }
  // 首次拉取时顺带计算侧边栏统计
  if (!blog.statsLoaded) await loadStats()
}

/** 拉取全量文章（page_size 上限 50，多于 50 篇时翻页补齐） */
async function fetchAllArticles() {
  const all = []
  let total = 0
  const first = await getArticles({ page: 1, page_size: 50 })
  if (first.code === 0) {
    all.push(...first.data.articles)
    total = first.data.pagination.total
  }
  const pagesNeeded = Math.ceil(total / 50)
  for (let p = 2; p <= pagesNeeded; p++) {
    const res = await getArticles({ page: p, page_size: 50 })
    if (res.code === 0) all.push(...res.data.articles)
  }
  return all
}

/** 计算侧边栏统计：文章数 / 归档月数 / 分类数 / 标签数 + 最新文章 */
export async function loadStats() {
  if (blog.statsLoaded) return
  blog.statsLoaded = true
  try {
    const all = await fetchAllArticles()
    const categories = new Set(all.map((a) => a.category))
    const tags = new Set(all.flatMap((a) => a.tags))
    const months = new Set(all.map((a) => String(a.date).slice(0, 7)))
    blog.stats = {
      articles: all.length,
      categories: categories.size,
      tags: tags.size,
      archives: months.size,
    }
    blog.recentArticles = [...all]
      .sort((a, b) => String(b.date).localeCompare(String(a.date)))
      .slice(0, 5)
      .map((a) => ({ id: a.id, title: a.title, date: a.date }))
  } catch {
    blog.statsLoaded = false // 失败允许重试，但不阻塞界面
  }
}

export function setCategory(cat) {
  blog.activeCategory = cat
  blog.pagination.page = 1
  fetchArticles()
}

export function toggleTag(tag) {
  blog.activeTag = blog.activeTag === tag ? '' : tag
  blog.pagination.page = 1
  fetchArticles()
}

export function doSearch() {
  blog.pagination.page = 1
  fetchArticles()
}

export function goPage(p) {
  blog.pagination.page = p
  fetchArticles()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
