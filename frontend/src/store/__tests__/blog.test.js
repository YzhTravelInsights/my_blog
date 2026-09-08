/**
 * store/blog 测试：列表拉取 / 统计聚合 / 筛选动作
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../../api/articles', () => ({
  getArticles: vi.fn(),
}))

import { getArticles } from '../../api/articles'
import {
  blog,
  fetchArticles,
  loadStats,
  setCategory,
  toggleTag,
  doSearch,
  goPage,
} from '../blog'

function res(articles, pagination, filters = { categories: [], tags: [] }) {
  return { code: 0, data: { articles, pagination, filters } }
}

beforeEach(() => {
  Object.assign(blog, {
    articles: [],
    pagination: { page: 1, page_size: 10, total: 0, total_pages: 1 },
    categories: [],
    tags: [],
    activeCategory: '',
    activeTag: '',
    searchText: '',
    loading: false,
    stats: { articles: 0, archives: 0, categories: 0, tags: 0 },
    recentArticles: [],
    statsLoaded: false,
  })
  window.scrollTo = vi.fn()
  vi.clearAllMocks()
})

describe('fetchArticles', () => {
  it('应用当前筛选并更新列表', async () => {
    getArticles.mockResolvedValue(
      res(
        [{ id: '1', title: 'T', category: 'Python', tags: [] }],
        { page: 1, total: 1, total_pages: 1 },
        { categories: ['Python'], tags: [] },
      ),
    )
    blog.activeCategory = 'Python'
    blog.searchText = 'hello'
    await fetchArticles()
    expect(getArticles).toHaveBeenCalledWith({
      page: 1,
      category: 'Python',
      tag: '',
      search: 'hello',
    })
    expect(blog.articles[0].title).toBe('T')
    expect(blog.categories).toEqual(['Python'])
  })

  it('首次拉取后触发 loadStats（statsLoaded 置真）', async () => {
    getArticles.mockResolvedValue(res([], { page: 1, total: 0, total_pages: 1 }))
    await fetchArticles()
    expect(blog.statsLoaded).toBe(true)
  })
})

describe('loadStats', () => {
  it('跨页聚合统计：文章/分类/标签/归档数', async () => {
    const page1 = Array.from({ length: 50 }, (_, i) => ({
      id: `a${i}`,
      title: `t${i}`,
      category: 'A',
      tags: ['x'],
      date: '2026-01-01',
    }))
    const page2 = [
      { id: 'b1', title: 't', category: 'B', tags: ['x', 'y'], date: '2026-02-01' },
      { id: 'b2', title: 't', category: 'C', tags: ['z'], date: '2025-12-01' },
    ]
    getArticles
      .mockResolvedValueOnce(res(page1, { page: 1, total: 52, total_pages: 2 }))
      .mockResolvedValueOnce(res(page2, { page: 2, total: 52, total_pages: 2 }))

    await loadStats()

    expect(blog.stats.articles).toBe(52)
    expect(blog.stats.categories).toBe(3) // A / B / C
    expect(blog.stats.tags).toBe(3) // x / y / z
    expect(blog.stats.archives).toBe(3) // 2026-01 / 2026-02 / 2025-12
    expect(blog.recentArticles.length).toBeLessThanOrEqual(5)
    // 最新文章按日期倒序
    expect(blog.recentArticles[0].title).toBe('t') // 2026-02-01 那条
  })

  it('已加载时不重复请求', async () => {
    blog.statsLoaded = true
    await loadStats()
    expect(getArticles).not.toHaveBeenCalled()
  })
})

describe('筛选动作', () => {
  it('setCategory 重置页码并拉取', () => {
    getArticles.mockResolvedValue(res([], { page: 1, total: 0, total_pages: 1 }))
    blog.pagination.page = 3
    setCategory('Vue')
    expect(blog.activeCategory).toBe('Vue')
    expect(blog.pagination.page).toBe(1)
    expect(getArticles).toHaveBeenCalled()
  })

  it('toggleTag 切换标签', () => {
    getArticles.mockResolvedValue(res([], { page: 1, total: 0, total_pages: 1 }))
    toggleTag('Flask')
    expect(blog.activeTag).toBe('Flask')
    toggleTag('Flask')
    expect(blog.activeTag).toBe('')
  })

  it('doSearch 重置页码', () => {
    getArticles.mockResolvedValue(res([], { page: 1, total: 0, total_pages: 1 }))
    blog.pagination.page = 2
    doSearch()
    expect(blog.pagination.page).toBe(1)
  })

  it('goPage 设置页码并滚动到顶部', () => {
    getArticles.mockResolvedValue(res([], { page: 1, total: 0, total_pages: 1 }))
    goPage(4)
    expect(blog.pagination.page).toBe(4)
    expect(window.scrollTo).toHaveBeenCalled()
  })
})
