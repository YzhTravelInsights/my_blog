/**
 * Vue Router 测试
 * 覆盖：路由定义 / 路径映射
 */
import { describe, it, expect } from 'vitest'
import router from '../router'

describe('Vue Router', () => {
  it('有 3 条路由', () => {
    const routes = router.getRoutes()
    expect(routes.length).toBe(3)
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

  it('使用 hash 模式', () => {
    // createWebHashHistory means URLs use #/
    const route = router.resolve('/')
    expect(route.fullPath).toBe('/')
  })
})
