/**
 * Write 视图测试：主人发布文章页
 * 覆盖：未登录显示密钥输入 → 登录显示编辑器 → 发布调用接口并提示成功 →
 * 401 清 token 回登录框 → 退出登录。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Write from '../Write.vue'

vi.mock('../../api/admin', () => ({
  publishArticle: vi.fn(),
}))
vi.mock('../../api/articles', () => ({
  getArticles: vi.fn(),
}))

import { publishArticle } from '../../api/admin'
import { getArticles } from '../../api/articles'

const TOKEN_KEY = 'blog_owner_token'

const OK_PUBLISH = {
  code: 0,
  data: { id: '2026-08-12-my-first-post', title: '我的第一篇文章', filename: '2026-08-12-my-first-post.md', url: '/article/2026-08-12-my-first-post' },
}

describe('Write', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.mocked(publishArticle).mockReset()
    vi.mocked(publishArticle).mockResolvedValue(OK_PUBLISH)
    vi.mocked(getArticles).mockReset()
    vi.mocked(getArticles).mockResolvedValue({
      data: { filters: { categories: ['生活随笔', '技术'] } },
    })
  })

  it('未登录时显示密钥输入框，不显示编辑器', () => {
    const w = mount(Write)
    expect(w.text()).toContain('发布文章')
    expect(w.find('input[type="password"]').exists()).toBe(true)
    expect(w.find('textarea').exists()).toBe(false)
  })

  it('已登录（localStorage 有 token）时直接显示编辑器', () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Write)
    expect(w.find('input[type="password"]').exists()).toBe(false)
    expect(w.find('input[placeholder="文章标题"]').exists()).toBe(true)
    expect(w.find('textarea').exists()).toBe(true)
  })

  it('输入密钥登录：token 存入 localStorage 并显示编辑器', async () => {
    const w = mount(Write)
    await w.find('input[type="password"]').setValue('my-secret')
    await w.find('button').trigger('click')
    expect(localStorage.getItem(TOKEN_KEY)).toBe('my-secret')
    expect(w.find('input[type="password"]').exists()).toBe(false)
    expect(w.find('textarea').exists()).toBe(true)
  })

  it('发布文章：调用接口并渲染成功提示', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Write)

    await w.find('input[placeholder="文章标题"]').setValue('我的第一篇文章')
    await w.find('input[placeholder="vue, 随笔"]').setValue('vue, 随笔')
    await w.find('textarea').setValue('## 你好\n这是一篇正文')

    const publishBtn = w.findAll('button').find((b) => b.text() === '发布文章')
    await publishBtn.trigger('click')

    expect(publishArticle).toHaveBeenCalledTimes(1)
    const arg = vi.mocked(publishArticle).mock.calls[0][0]
    expect(arg.title).toBe('我的第一篇文章')
    expect(arg.category).toBe('')
    expect(arg.tags).toEqual(['vue', '随笔'])
    expect(arg.token).toBe('secret-123')

    await new Promise((r) => setTimeout(r, 20))
    expect(w.text()).toContain('发布成功')
  })

  it('发布接口返回 401 时清 token 并回到登录框', async () => {
    vi.mocked(publishArticle).mockResolvedValue({ code: 2, msg: 'unauthorized', data: null })
    window.alert = vi.fn()
    localStorage.setItem(TOKEN_KEY, 'wrong-secret')
    const w = mount(Write)

    await w.find('input[placeholder="文章标题"]').setValue('测试')
    await w.find('textarea').setValue('正文')
    const publishBtn = w.findAll('button').find((b) => b.text() === '发布文章')
    await publishBtn.trigger('click')
    await new Promise((r) => setTimeout(r, 20))

    expect(localStorage.getItem(TOKEN_KEY)).toBeNull()
    expect(w.find('input[type="password"]').exists()).toBe(true)
    expect(window.alert).toHaveBeenCalled()
  })

  it('退出登录：清 token 并回到登录框', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Write)
    const logoutBtn = w.findAll('button').find((b) => b.text() === '退出')
    await logoutBtn.trigger('click')
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull()
    expect(w.find('input[type="password"]').exists()).toBe(true)
  })
})
