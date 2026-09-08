/**
 * Article 视图测试：文章加载 + 上下篇路由切换后重新拉取内容
 * （回归：组件实例被复用，onMounted 不会重跑，需靠 watch(articleId) 重载）
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHashHistory } from 'vue-router'

// 路径从测试文件（src/views/__tests__/）解析
vi.mock('../../api/articles', () => ({
  getArticle: vi.fn(async (id) => {
    const map = {
      '1': {
        code: 0,
        data: {
          id: '1', title: '第一篇文章', content: '# 介绍\n正文一', category: 'Python',
          date: '2026-01-01', tags: ['A'], prev: null, next: { id: '2', title: '第二篇' },
        },
      },
      '2': {
        code: 0,
        data: {
          id: '2', title: '第二篇文章', content: '# 介绍\n正文二', category: 'Vue',
          date: '2026-02-01', tags: ['B'], prev: { id: '1', title: '第一篇' }, next: null,
        },
      },
    }
    return map[id] || { code: 1, msg: 'not found' }
  }),
}))

// 评论区独立测试，这里用桩避免真实请求
vi.mock('../../components/CommentSection.vue', () => ({
  default: { name: 'CommentSectionStub', template: '<div />' },
}))

import Article from '../Article.vue'
import { getArticle } from '../../api/articles'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'Home', component: { template: '<div/>' } },
    { path: '/article/:id', name: 'Article', component: Article },
  ],
})

let wrapper = null

async function mountAt(path) {
  await router.push(path)
  await router.isReady()
  wrapper = mount(Article, { global: { plugins: [router] } })
  return wrapper
}

describe('Article 视图', () => {
  beforeEach(async () => {
    getArticle.mockClear()
    await router.push('/')
    await router.isReady()
  })

  afterEach(() => {
    // 卸载旧 wrapper，避免其 watch(articleId) 在后续用例的路由变化时继续触发 getArticle
    wrapper?.unmount()
    wrapper = null
  })

  it('加载并渲染文章', async () => {
    const wrapper = await mountAt('/article/1')
    await vi.waitFor(() => expect(wrapper.text()).toContain('第一篇文章'))
    expect(getArticle).toHaveBeenCalledWith('1')
  })

  it('文章不存在时显示占位', async () => {
    const wrapper = await mountAt('/article/999')
    await vi.waitFor(() => expect(wrapper.text()).toContain('文章不存在'))
  })

  it('上下篇路由切换后重新拉取新文章内容', async () => {
    const wrapper = await mountAt('/article/1')
    await vi.waitFor(() => expect(wrapper.text()).toContain('第一篇文章'))

    await router.push('/article/2')
    // 旧内容应被清空，新内容加载出来
    await vi.waitFor(() => expect(wrapper.text()).toContain('第二篇文章'))
    expect(wrapper.text()).not.toContain('第一篇文章')
    expect(getArticle).toHaveBeenCalledTimes(2)
    expect(getArticle).toHaveBeenLastCalledWith('2')
  })

  it('切换回上一篇文章也能正确刷新', async () => {
    const wrapper = await mountAt('/article/2')
    await vi.waitFor(() => expect(wrapper.text()).toContain('第二篇文章'))

    await router.push('/article/1')
    await vi.waitFor(() => expect(wrapper.text()).toContain('第一篇文章'))
    expect(getArticle).toHaveBeenLastCalledWith('1')
  })
})
