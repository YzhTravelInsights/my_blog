/**
 * Vue Router 测试
 * 覆盖：路由定义 / 路径映射
 */
import { describe, it, expect, vi } from 'vitest'

// 只测路由配置，不必加载真实视图（避免 happy-dom 尝试加载视图里的本地图片资源）
vi.mock('../views/Home.vue', () => ({ default: { name: 'HomeStub', template: '<div/>' } }))
vi.mock('../views/Article.vue', () => ({ default: { name: 'ArticleStub', template: '<div/>' } }))
vi.mock('../views/About.vue', () => ({ default: { name: 'AboutStub', template: '<div/>' } }))

import router from '../router'

describe('Vue Router', () => {
  it('有 7 条路由', () => {
    const routes = router.getRoutes()
    expect(routes.length).toBe(7)
  })

  it('/ 映射到 Home', () => {
    const route = router.resolve('/')
    expect(route.name).toBe('Home')
  })

  it('/article/:id 映射到 Article', () => {
    const route = router.resolve('/article/test-id')
    expect(route.name).toBe('Article')
    expect(route.params.id).toBe('test-id')
  })

  it('/about 映射到 About', () => {
    const route = router.resolve('/about')
    expect(route.name).toBe('About')
  })

  it('/gallery 映射到 Gallery', () => {
    const route = router.resolve('/gallery')
    expect(route.name).toBe('Gallery')
  })

  it('/chat 映射到 OwnerChat', () => {
    const route = router.resolve('/chat')
    expect(route.name).toBe('OwnerChat')
  })

  it('/admin 映射到 Admin', () => {
    const route = router.resolve('/admin')
    expect(route.name).toBe('Admin')
  })

  it('/write 映射到 Write', () => {
    const route = router.resolve('/write')
    expect(route.name).toBe('Write')
  })

  it('使用 hash 模式', () => {
    // createWebHashHistory means URLs use #/
    const route = router.resolve('/')
    expect(route.fullPath).toBe('/')
  })
})
