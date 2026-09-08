/**
 * admin API 测试：发布文章 / 删除文章 / 删除评论（均需 Bearer OWNER_SECRET）
 */
import { describe, it, expect, vi } from 'vitest'

const mockFetch = vi.fn()
global.fetch = mockFetch

function mockResponse(data, status = 200) {
  return Promise.resolve({ status, json: () => Promise.resolve(data) })
}

const { publishArticle, deleteArticle, deleteComment } = await import('../admin')

describe('admin API', () => {
  it('publishArticle：POST 到 /admin/article 并带 Bearer 头', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { id: '2026-08-12-x' } }))
    const res = await publishArticle({ title: 't', category: 'c', tags: ['a'], content: 'body', token: 'my-secret' })
    expect(res.code).toBe(0)
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/admin/article',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ Authorization: 'Bearer my-secret' }),
      })
    )
  })

  it('deleteArticle：DELETE 到 /admin/article/<id>（URL 编码）并带 Bearer 头', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { id: '2026-08-12-x' } }))
    const res = await deleteArticle('2026-08-12-测试-在线发布', 'my-secret')
    expect(res.code).toBe(0)
    const [url, opts] = mockFetch.mock.calls.at(-1)
    expect(url).toBe(`/api/admin/article/${encodeURIComponent('2026-08-12-测试-在线发布')}`)
    expect(opts.method).toBe('DELETE')
    expect(opts.headers.Authorization).toBe('Bearer my-secret')
  })

  it('deleteComment：DELETE 到 /admin/comment/<id> 并带 Bearer 头', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { id: 7 } }))
    const res = await deleteComment(7, 'my-secret')
    expect(res.code).toBe(0)
    const [url, opts] = mockFetch.mock.calls.at(-1)
    expect(url).toBe('/api/admin/comment/7')
    expect(opts.method).toBe('DELETE')
    expect(opts.headers.Authorization).toBe('Bearer my-secret')
  })
})
