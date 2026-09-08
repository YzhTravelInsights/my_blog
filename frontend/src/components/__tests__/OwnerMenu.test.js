/**
 * OwnerMenu 测试：导航栏「👑 主人」入口
 * 覆盖：未登录显示密钥输入 → 输入密钥存入 localStorage 并显示三个入口 →
 * 已登录直接显示入口 → 退出回密钥输入框。
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHashHistory } from 'vue-router'
import OwnerMenu from '../OwnerMenu.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/chat', component: { template: '<div/>' } },
    { path: '/admin', component: { template: '<div/>' } },
    { path: '/write', component: { template: '<div/>' } },
  ],
})

const TOKEN_KEY = 'blog_owner_token'

function make() {
  return mount(OwnerMenu, { global: { plugins: [router] } })
}

describe('OwnerMenu', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('渲染「主人」入口按钮，默认不展开', () => {
    const w = make()
    expect(w.find('.owner-btn').exists()).toBe(true)
    expect(w.find('input[type="password"]').exists()).toBe(false)
  })

  it('未登录点击展开：显示密钥输入框，不含入口链接', async () => {
    const w = make()
    await w.find('.owner-btn').trigger('click')
    expect(w.find('input[type="password"]').exists()).toBe(true)
    expect(w.text()).not.toContain('管理后台')
  })

  it('输入密钥：存入 localStorage 并显示三个入口链接', async () => {
    const w = make()
    await w.find('.owner-btn').trigger('click')
    await w.find('input[type="password"]').setValue('my-secret')
    await w.find('.btn-primary').trigger('click')

    expect(localStorage.getItem(TOKEN_KEY)).toBe('my-secret')
    expect(w.text()).toContain('私聊')
    expect(w.text()).toContain('管理后台')
    expect(w.text()).toContain('发布文章')
  })

  it('已登录：按钮显示绿点 + 「已登录」字样，登录态一眼可辨', () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = make()
    expect(w.find('.owner-dot').exists()).toBe(true)
    expect(w.find('.owner-btn').classes()).toContain('owner-btn-logged')
    expect(w.text()).toContain('已登录')
  })

  it('未登录：按钮无绿点、无「已登录」字样', () => {
    const w = make()
    expect(w.find('.owner-dot').exists()).toBe(false)
    expect(w.text()).not.toContain('已登录')
  })

  it('已登录：点击主人直接显示三个入口，无密钥输入框', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = make()
    await w.find('.owner-btn').trigger('click')
    expect(w.text()).toContain('私聊')
    expect(w.text()).toContain('管理后台')
    expect(w.text()).toContain('发布文章')
    expect(w.find('input[type="password"]').exists()).toBe(false)
  })

  it('退出登录：清 token 并回到密钥输入框', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = make()
    await w.find('.owner-btn').trigger('click')
    const logoutBtn = w.findAll('button').find((b) => b.text().includes('退出'))
    await logoutBtn.trigger('click')
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull()
    expect(w.find('input[type="password"]').exists()).toBe(true)
  })
})
