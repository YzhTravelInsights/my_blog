/**
 * Admin 视图测试：管理后台（认证后拉取后台数据 + 系统运行信息）
 * 覆盖：未登录显示密钥输入 → 登录拉取并渲染统计/系统信息 → 401 清 token → 退出。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Admin from '../Admin.vue'

vi.mock('../../api/admin', () => ({
  getAdminSummary: vi.fn(),
  deleteArticle: vi.fn(),
  deleteComment: vi.fn(),
}))

import { getAdminSummary, deleteArticle, deleteComment } from '../../api/admin'

const TOKEN_KEY = 'blog_owner_token'

const SUMMARY = {
  code: 0,
  data: {
    content: {
      articles: 17, categories: 5, tags: 12, comments: 8, private_comments: 1,
      memory: 10, impressions: 3, indexed: 17,
      affinity: { level: 'soul_bond', level_name: '羁绊', interaction_count: 100, last_interaction_at: '2026-08-12 04:47:07' },
      category_counts: [
        { name: '技术', count: 10 },
        { name: '生活随笔', count: 7 },
      ],
      tag_counts: [{ name: 'RAG', count: 5 }],
      recent_articles: [
        { id: '2026-08-12-test', title: '测试文章一', date: '2026-08-12', category: '技术', tags: ['RAG'] },
      ],
      recent_comments: [
        { id: 1, article_id: '2026-08-12-test', article_title: '测试文章一', nickname: '访客A', content: '写得很棒！', is_private: 0, created_at: '2026-08-12 05:00:00' },
      ],
      recent_impressions: [
        { id: 1, content: '开拓者喜欢深聊技术', weight: 0.8, created_at: '2026-08-12 05:00:00' },
      ],
    },
    system: {
      version: '1.0',
      started_at: 1754960000,
      uptime_seconds: 3661,
      uptime: '1 小时 1 分 1 秒',
      api_errors: 2,
      now: '2026-08-12 05:00:00',
      python: '3.11',
      flask: '3.0',
      platform: 'Windows',
      hostname: 'myblog-host',
      pid: 1234,
      db: 'D:/backend/data/blog.db',
      db_size: 1258291,
      db_size_text: '1.2 MB',
    },
  },
}

describe('Admin', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.mocked(getAdminSummary).mockReset()
    vi.mocked(getAdminSummary).mockResolvedValue(SUMMARY)
    vi.mocked(deleteArticle).mockReset()
    vi.mocked(deleteComment).mockReset()
  })

  it('未登录时显示密钥输入框', () => {
    const w = mount(Admin)
    expect(w.text()).toContain('管理后台')
    expect(w.find('input[type="password"]').exists()).toBe(true)
  })

  it('登录后拉取数据并渲染统计卡片与系统信息', async () => {
    const w = mount(Admin)
    await w.find('input[type="password"]').setValue('my-secret')
    await w.find('button').trigger('click')

    expect(getAdminSummary).toHaveBeenCalledTimes(1)
    expect(getAdminSummary).toHaveBeenCalledWith('my-secret')
    expect(localStorage.getItem(TOKEN_KEY)).toBe('my-secret')

    await new Promise((r) => setTimeout(r, 20))
    expect(w.text()).toContain('17')            // 文章
    expect(w.text()).toContain('私密评论')
    expect(w.text()).toContain('羁绊')           // 好感度徽章
    expect(w.text()).toContain('1 小时 1 分 1 秒') // 运行时长
    expect(w.text()).toContain('2')             // api_errors
    expect(w.text()).toContain('3.11')          // python
  })

  it('渲染最近文章 / 分类标签 / 最近评论 / 人格印象 / 系统明细', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Admin)
    await new Promise((r) => setTimeout(r, 20))
    expect(w.text()).toContain('测试文章一')      // 最近文章
    expect(w.text()).toContain('技术 × 10')        // 分类计数
    expect(w.text()).toContain('#RAG × 5')         // 标签计数
    expect(w.text()).toContain('写得很棒！')        // 最近评论
    expect(w.text()).toContain('深聊技术')          // 人格印象
    expect(w.text()).toContain('myblog-host')      // 主机名
    expect(w.text()).toContain('1.2 MB')           // 数据库大小
  })

  it('文章管理/评论管理卡片渲染全量列表与删除按钮', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Admin)
    await new Promise((r) => setTimeout(r, 20))
    expect(w.text()).toContain('文章管理')
    expect(w.text()).toContain('评论管理')
    expect(w.text()).toContain('测试文章一')
    expect(w.text()).toContain('写得很棒！')
    expect(w.findAll('.del-btn').length).toBe(2)
  })

  it('删除文章：确认后调用删除接口并刷新', async () => {
    window.confirm = vi.fn(() => true)
    window.alert = vi.fn()
    vi.mocked(deleteArticle).mockResolvedValue({ code: 0, data: { hint: '已删除文章及其 0 条评论' } })
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Admin)
    await new Promise((r) => setTimeout(r, 20))

    const btn = w.findAll('.del-btn').find((b) => (b.attributes('title') || '').includes('《测试文章一》'))
    await btn.trigger('click')

    expect(window.confirm).toHaveBeenCalled()
    expect(deleteArticle).toHaveBeenCalledWith('2026-08-12-test', 'secret-123')
    await new Promise((r) => setTimeout(r, 20))
    expect(getAdminSummary).toHaveBeenCalledTimes(2) // 初始 + 删除后刷新
  })

  it('删除评论：确认后调用删除接口并刷新', async () => {
    window.confirm = vi.fn(() => true)
    window.alert = vi.fn()
    vi.mocked(deleteComment).mockResolvedValue({ code: 0, data: { hint: '已删除评论（含 0 条回复）' } })
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Admin)
    await new Promise((r) => setTimeout(r, 20))

    const btn = w.findAll('.del-btn').find((b) => (b.attributes('title') || '').includes('访客A'))
    await btn.trigger('click')

    expect(window.confirm).toHaveBeenCalled()
    expect(deleteComment).toHaveBeenCalledWith(1, 'secret-123')
    await new Promise((r) => setTimeout(r, 20))
    expect(getAdminSummary).toHaveBeenCalledTimes(2)
  })

  it('删除取消确认时不调用接口', async () => {
    window.confirm = vi.fn(() => false)
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Admin)
    await new Promise((r) => setTimeout(r, 20))
    await w.findAll('.del-btn')[0].trigger('click')
    expect(deleteArticle).not.toHaveBeenCalled()
    expect(deleteComment).not.toHaveBeenCalled()
  })

  it('已登录（token 存在）时自动拉取', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Admin)
    await new Promise((r) => setTimeout(r, 20))
    expect(getAdminSummary).toHaveBeenCalledWith('secret-123')
    expect(w.text()).toContain('管理后台')
  })

  it('接口返回 401 时清 token 并回到登录框', async () => {
    vi.mocked(getAdminSummary).mockResolvedValue({ code: 2, msg: 'unauthorized', data: null })
    window.alert = vi.fn()
    localStorage.setItem(TOKEN_KEY, 'wrong-secret')
    const w = mount(Admin)
    await new Promise((r) => setTimeout(r, 20))
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull()
    expect(w.find('input[type="password"]').exists()).toBe(true)
    expect(window.alert).toHaveBeenCalled()
  })

  it('退出登录：清 token 回到登录框', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = mount(Admin)
    await new Promise((r) => setTimeout(r, 20))
    const logoutBtn = w.findAll('button').find((n) => n.text() === '退出')
    await logoutBtn.trigger('click')
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull()
    expect(w.find('input[type="password"]').exists()).toBe(true)
  })
})
