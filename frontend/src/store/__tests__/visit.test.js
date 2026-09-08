/**
 * visit store 测试：访问计数 + 阅读记录
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { visit, initVisit, addVisit, recordArticleView } from '../visit'

beforeEach(() => {
  localStorage.clear()
  sessionStorage.clear()
  initVisit()
})

describe('visit · 访问计数', () => {
  it('初始为 0', () => {
    expect(visit.count).toBe(0)
  })

  it('addVisit 记一次，写回 localStorage', () => {
    expect(addVisit()).toBe(1)
    expect(JSON.parse(localStorage.getItem('blog_visit_count'))).toBe(1)
  })

  it('同一会话再次 addVisit 不再累加', () => {
    addVisit()
    addVisit()
    addVisit()
    expect(visit.count).toBe(1)
  })

  it('initVisit 从 localStorage 恢复历史计数', () => {
    addVisit()
    visit.count = 42
    localStorage.setItem('blog_visit_count', JSON.stringify(42))
    initVisit()
    expect(visit.count).toBe(42)
  })
})

describe('visit · 阅读记录', () => {
  it('recordArticleView 记录并置顶', () => {
    recordArticleView('a1', '第一篇')
    recordArticleView('a2', '第二篇')
    expect(visit.readingCount).toBe(2)
    expect(visit.history[0].title).toBe('第二篇')
    expect(visit.history[1].title).toBe('第一篇')
  })

  it('重复阅读同一篇只保留最新位置', () => {
    recordArticleView('a1', '第一篇')
    recordArticleView('a2', '第二篇')
    recordArticleView('a1', '第一篇')
    expect(visit.readingCount).toBe(2)
    expect(visit.history[0].id).toBe('a1')
  })

  it('超过上限只保留最近 20 条', () => {
    for (let i = 1; i <= 25; i++) recordArticleView(`id-${i}`, `文章${i}`)
    expect(visit.readingCount).toBe(20)
    expect(visit.history.length).toBe(20)
    expect(visit.history[0].id).toBe('id-25')
    expect(visit.history[19].id).toBe('id-6')
  })

  it('阅读记录持久化到 localStorage，initVisit 可恢复', () => {
    recordArticleView('a1', '第一篇')
    initVisit()
    expect(visit.readingCount).toBe(1)
    expect(visit.history[0].title).toBe('第一篇')
  })
})
