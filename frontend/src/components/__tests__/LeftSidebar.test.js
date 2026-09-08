/**
 * LeftSidebar 左侧栏测试：个人卡片 / 统计 / 社交链接 / 公告
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHashHistory } from 'vue-router'
import LeftSidebar from '../LeftSidebar.vue'
import { site } from '../../config/site'
import { blog } from '../../store/blog'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'Home', component: { template: '<div/>' } },
    { path: '/about', name: 'About', component: { template: '<div/>' } },
  ],
})

beforeEach(() => {
  // 跳过网络统计：直接给定统计值
  blog.statsLoaded = true
  Object.assign(blog.stats, { articles: 12, archives: 8, categories: 3, tags: 5 })
})

describe('LeftSidebar', () => {
  it('渲染站名、昵称、学校', () => {
    const wrapper = mount(LeftSidebar, { global: { plugins: [router] } })
    expect(wrapper.text()).toContain(site.name)
    expect(wrapper.text()).toContain(site.owner.nickname)
    expect(wrapper.text()).toContain(site.owner.school)
  })

  it('渲染站点统计数字', () => {
    const wrapper = mount(LeftSidebar, { global: { plugins: [router] } })
    expect(wrapper.text()).toContain('12')
    expect(wrapper.text()).toContain('8')
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('5')
  })

  it('渲染社交链接：href 正确（有链接跳转，无链接为空）', () => {
    const wrapper = mount(LeftSidebar, { global: { plugins: [router] } })
    for (const s of site.socials) {
      const el = wrapper.find(`a[aria-label="${s.title}"]`)
      expect(el.exists()).toBe(true)
      if (s.url) {
        expect(el.attributes('href')).toBe(s.url)
      } else {
        expect(el.attributes('href')).toBeUndefined() // 空 url 不跳转，靠复制 + 悬浮提示
      }
    }
  })

  it('悬浮图标：在图标下方显示账号提示，移开消失', async () => {
    const wrapper = mount(LeftSidebar, { global: { plugins: [router] } })
    const wechat = site.socials.find((s) => s.name === '微信')
    const el = wrapper.find(`a[aria-label="${wechat.title}"]`)
    await el.trigger('mouseenter')
    const tip = wrapper.find('.social-tip')
    expect(tip.exists()).toBe(true)
    expect(tip.text()).toContain(wechat.title)
    await el.trigger('mouseleave')
    expect(wrapper.find('.social-tip').exists()).toBe(false)
  })

  it('点击联系方式类社交：在图标下方显示复制成功提示', async () => {
    const wrapper = mount(LeftSidebar, { global: { plugins: [router] } })
    const wechat = site.socials.find((s) => s.name === '微信')
    const el = wrapper.find(`a[aria-label="${wechat.title}"]`)
    await el.trigger('click')
    const tip = wrapper.find('.social-tip')
    expect(tip.exists()).toBe(true)
    expect(tip.text()).toContain(wechat.toast)
  })

  it('渲染公告内容', () => {
    const wrapper = mount(LeftSidebar, { global: { plugins: [router] } })
    expect(wrapper.text()).toContain(site.announcement)
  })

  it('包含「关于本站」按钮', () => {
    const wrapper = mount(LeftSidebar, { global: { plugins: [router] } })
    expect(wrapper.text()).toContain('关于本站')
  })
})
