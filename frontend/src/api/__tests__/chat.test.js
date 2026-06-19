/**
 * chat API 测试
 */
import { describe, it, expect, vi } from 'vitest'

const mockFetch = vi.fn()
global.fetch = mockFetch

function mockResponse(data) {
  return Promise.resolve({ json: () => Promise.resolve(data) })
}

const { sendMessage } = await import('../chat')

describe('sendMessage', () => {
  it('发送 POST 含正确 body', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { reply: 'hi', emotion: 'happy' } }))
    await sendMessage({ message: 'hello', session_id: 's1', history: [], session_type: 'guest' })
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/chat',
      expect.objectContaining({ method: 'POST' })
    )
    const body = JSON.parse(mockFetch.mock.calls[0][1].body)
    expect(body.message).toBe('hello')
    expect(body.session_id).toBe('s1')
    expect(body.session_type).toBe('guest')
  })

  it('发送含 history 的请求', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ code: 0, data: { reply: 'ok' } }))
    const history = [{ role: 'user', content: 'prev' }, { role: 'assistant', content: 'reply' }]
    await sendMessage({ message: 'new', session_id: 's2', history, session_type: 'owner' })
    const body = JSON.parse(mockFetch.mock.calls.at(-1)[1].body)
    expect(body.history).toEqual(history)
    expect(body.session_type).toBe('owner')
  })

  it('返回解析后的 JSON', async () => {
    const expected = { code: 0, data: { reply: '嘿嘿～', emotion: 'happy', mode: 'public' } }
    mockFetch.mockResolvedValueOnce(mockResponse(expected))
    const result = await sendMessage({ message: 'x', session_id: 's3' })
    expect(result.data.reply).toBe('嘿嘿～')
  })
})
