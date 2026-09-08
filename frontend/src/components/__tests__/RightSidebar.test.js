/**
 * RightSidebar 右侧栏测试：home 模式（筛选/最新）/ toc 模式（目录）
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHashHistory } from 'vue-router'
import RightSidebar from '../RightSidebar.vue'
import { blog } from '../../store/blog'
import { tocState } from '../../store/toc'
import { visit } from '../../store/visit'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'Home', component: { template: '<div/>' } },
    { path: '/article/:id', name: 'Article', component: { template: '<div/>' } },
  ],
})

beforeEach(() => {
  // 跳过网络统计与列表请求：mock fetch 避免真实网络调用
  blog.statsLoaded = true
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () =>
      Promise.resolve({
        code: 0,
        data: { articles: [], pagination: { page: 1, total: 0, total_pages: 1 }, filters: {} },
      }),
  })
  Object.assign(blog, {
    categories: ['Python', 'Vue'],
    tags: ['Flask', 'RAG'],
    activeCategory: '',
    activeTag: '',
    recentArticles: [
      { id: 'a1', title: '最新文章一', date: '2026-08-01' },
      { id: 'a2', title: '最新文章二', date: '2026-07-01' },
    ],
  })
  tocState.items = []
  visit.history = []
})

describe('RightSidebar · home 模式', () => {
  it('渲染分类 / 标签筛选', () => {
    const wrapper = mount(RightSidebar, {
      props: { mode: 'home' },
      global: { plugins: [router] },
    })
    const text = wrapper.text()
    expect(text).toContain('Python')
    expect(text).toContain('Vue')
    expect(text).toContain('Flask')
    expect(text).toContain('RAG')
  })

  it('渲染最新文章', () => {
    const wrapper = mount(RightSidebar, {
      props: { mode: 'home' },
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('最新文章一')
    expect(wrapper.text()).toContain('最新文章二')
  })

  it('点击分类更新 store.activeCategory', async () => {
    const wrapper = mount(RightSidebar, {
      props: { mode: 'home' },
      global: { plugins: [router] },
    })
    const pythonBtn = wrapper.findAll('button').find((b) => b.text() === 'Python')
    await pythonBtn.trigger('click')
    expect(blog.activeCategory).toBe('Python')
  })

  it('渲染最近阅读记录', () => {
    visit.history = [
      { id: 'h1', title: '刚读过的文章', time: 1780000000000 },
    ]
    const wrapper = mount(RightSidebar, {
      props: { mode: 'home' },
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('最近阅读')
    expect(wrapper.text()).toContain('刚读过的文章')
    const link = wrapper.find('a[href="#/article/h1"]')
    expect(link.exists()).toBe(true)
  })

  it('无阅读记录时显示占位', () => {
    const wrapper = mount(RightSidebar, {
      props: { mode: 'home' },
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('还没有阅读记录')
  })
})

describe('RightSidebar · toc 模式', () => {
  it('渲染目录锚点链接', () => {
    tocState.items = [
      { id: 'sec-1', text: '第一章', level: 2 },
      { id: 'sec-2', text: '第二章', level: 3 },
    ]
    const wrapper = mount(RightSidebar, { props: { mode: 'toc' } })
    const links = wrapper.findAll('a')
    expect(links.length).toBe(2)
    expect(links[0].attributes('href')).toBe('#sec-1')
    expect(wrapper.text()).toContain('第一章')
  })

  it('无目录时显示占位', () => {
    const wrapper = mount(RightSidebar, { props: { mode: 'toc' } })
    expect(wrapper.text()).toContain('本文暂无目录')
  })
})
