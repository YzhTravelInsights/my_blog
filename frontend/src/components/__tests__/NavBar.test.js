/**
 * NavBar 组件测试
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import NavBar from '../NavBar.vue'
import { createRouter, createWebHashHistory } from 'vue-router'

const TOKEN_KEY = 'blog_owner_token'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'Home', component: { template: '<div>home</div>' } },
    { path: '/about', name: 'About', component: { template: '<div>about</div>' } },
  ],
})

describe('NavBar', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('渲染品牌名「流萤小筑」', () => {
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('流萤小筑')
  })

  it('包含首页链接', () => {
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('首页')
  })

  it('包含关于链接', () => {
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('关于')
  })

  it('包含图库链接', () => {
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('图库')
  })

  it('访客也能看到「主人」入口按钮（入口常驻，未登录点开才输密钥）', () => {
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('.owner-btn').exists()).toBe(true)
    expect(wrapper.text()).toContain('主人')
  })

  it('主人登录（本地有令牌）时导航栏常驻「主人」入口', () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('.owner-btn').exists()).toBe(true)
  })

  it('主人登录后：私聊/管理/发布内联显示，和首页/关于一样直达', () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })
    const links = wrapper.findAll('.nav-link').map((l) => l.text())
    expect(links.some((l) => l.includes('私聊'))).toBe(true)
    expect(links.some((l) => l.includes('管理'))).toBe(true)
    expect(links.some((l) => l.includes('发布'))).toBe(true)
    expect(links.some((l) => l.includes('首页'))).toBe(true)
    expect(links.some((l) => l.includes('关于'))).toBe(true)
  })

  it('点击汉堡按钮触发 toggle-drawer', async () => {
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })
    await wrapper.find('.hamburger').trigger('click')
    expect(wrapper.emitted('toggle-drawer')).toBeTruthy()
  })
})
