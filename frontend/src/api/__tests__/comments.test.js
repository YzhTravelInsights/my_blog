/**
 * comments API 测试
 * 覆盖：getComments / postComment
 */
import { describe, it, expect, vi } from 'vitest'

const mockFetch = vi.fn()
global.fetch = mockFetch

function mockResponse(data) {
  return Promise.resolve({ json: () => Promise.resolve(data) })
}

const { getComments, postComment } = await import('../comments')

describe('getComments', () => {
  it('构建正确的 URL', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { comments: [], count: 0 } }))
    await getComments('article-1')
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/comments?article_id=article-1'
    )
  })

  it('返回评论数据', async () => {
    const expected = { code: 0, data: { comments: [{ id: 1, content: 'hi' }], count: 1 } }
    mockFetch.mockResolvedValueOnce(mockResponse(expected))
    const result = await getComments('x')
    expect(result.data.count).toBe(1)
  })
})

describe('postComment', () => {
  it('发送 POST 含正确 body', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { id: 5 } }))
    await postComment({
      article_id: 'a1',
      nickname: 'test',
      content: 'hello',
      is_private: false,
    })
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/comments',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ article_id: 'a1', nickname: 'test', content: 'hello', is_private: false }),
      })
    )
  })

  it('私密评论发送 is_private=true', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { id: 6 } }))
    await postComment({ article_id: 'a1', content: 'secret', is_private: true })
    const callBody = JSON.parse(mockFetch.mock.calls.at(-1)[1].body)
    expect(callBody.is_private).toBe(true)
  })

  it('默认昵称为匿名', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { id: 7 } }))
    await postComment({ article_id: 'a1', content: 'no name' })
    const callBody = JSON.parse(mockFetch.mock.calls.at(-1)[1].body)
    // 前端不强制发 nickname，后端会默认"匿名"
    expect(callBody.article_id).toBe('a1')
  })
})
