/**
 * ArticleCard 组件测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ArticleCard from '../ArticleCard.vue'
import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/article/:id', name: 'Article', component: { template: '<div/>' }, props: true },
  ],
})

const mockArticle = {
  id: '2025-01-01-test',
  title: '测试文章标题',
  summary: '这是摘要内容',
  category: 'Python',
  tags: ['Python', 'Conda'],
  date: '2025-01-01',
}

describe('ArticleCard', () => {
  it('渲染文章标题', () => {
    const wrapper = mount(ArticleCard, {
      props: { article: mockArticle },
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('测试文章标题')
  })

  it('渲染摘要', () => {
    const wrapper = mount(ArticleCard, {
      props: { article: mockArticle },
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('这是摘要内容')
  })

  it('渲染分类标签', () => {
    const wrapper = mount(ArticleCard, {
      props: { article: mockArticle },
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('Python')
  })

  it('渲染 Tag 列表', () => {
    const wrapper = mount(ArticleCard, {
      props: { article: mockArticle },
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('Conda')
  })

  it('包含文章链接', () => {
    const wrapper = mount(ArticleCard, {
      props: { article: mockArticle },
      global: { plugins: [router] },
    })
    const link = wrapper.find('a')
    expect(link.attributes('href')).toContain('2025-01-01-test')
  })
})
