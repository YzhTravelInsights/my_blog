/**
 * articles API 测试
 * 覆盖：getArticles / getArticle / getAbout
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

// 需要在 mock 之后动态导入
const { getArticles, getArticle, getAbout } = await import('../articles')

function mockResponse(data) {
  return Promise.resolve({
    json: () => Promise.resolve(data),
  })
}

describe('getArticles', () => {
  it('构建正确的 URL（无参数）', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { articles: [], pagination: {}, filters: {} } }))
    await getArticles()
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/articles?page=1&page_size=10')
    )
  })

  it('构建正确的 URL（含 category）', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { articles: [], pagination: {}, filters: {} } }))
    await getArticles({ category: 'Python' })
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('category=Python')
    )
  })

  it('构建正确的 URL（含 search）', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { articles: [], pagination: {}, filters: {} } }))
    await getArticles({ search: 'Conda' })
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('search=Conda')
    )
  })

  it('构建正确的 URL（含 tag）', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { articles: [], pagination: {}, filters: {} } }))
    await getArticles({ tag: 'Flask' })
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('tag=Flask')
    )
  })

  it('返回解析后的 JSON', async () => {
    const expected = { code: 0, data: { articles: [{ id: '1', title: 'Test' }], pagination: { page: 1, total: 1 }, filters: { categories: [], tags: [] } } }
    mockFetch.mockResolvedValueOnce(mockResponse(expected))
    const result = await getArticles()
    expect(result).toEqual(expected)
  })
})

describe('getArticle', () => {
  it('构建带 ID 的 URL', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { id: 'test-id', title: 'X' } }))
    await getArticle('test-id')
    expect(mockFetch).toHaveBeenCalledWith('/api/articles/test-id')
  })

  it('返回文章详情', async () => {
    const expected = { code: 0, data: { id: '1', title: 'T', content: 'Body', tags: [] } }
    mockFetch.mockResolvedValueOnce(mockResponse(expected))
    const result = await getArticle('1')
    expect(result.data.title).toBe('T')
  })
})

describe('getAbout', () => {
  it('调用 /api/about', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { name: 'Test', content: 'About' } }))
    await getAbout()
    expect(mockFetch).toHaveBeenCalledWith('/api/about')
  })
})
