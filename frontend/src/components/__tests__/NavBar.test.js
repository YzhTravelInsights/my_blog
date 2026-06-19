/**
 * NavBar 组件测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import NavBar from '../NavBar.vue'
import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'Home', component: { template: '<div>home</div>' } },
    { path: '/about', name: 'About', component: { template: '<div>about</div>' } },
  ],
})

describe('NavBar', () => {
  it('渲染博客标题', () => {
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })
    expect(wrapper.text()).toContain('My Blog')
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
})
