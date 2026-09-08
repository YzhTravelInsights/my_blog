/**
 * ThemeToggle 明暗切换测试
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ThemeToggle from '../ThemeToggle.vue'

beforeEach(() => {
  document.documentElement.classList.remove('dark')
  localStorage.clear()
})

describe('ThemeToggle', () => {
  it('初始状态从 DOM 读取（默认浅色 → 显示月亮图标）', () => {
    const wrapper = mount(ThemeToggle)
    expect(wrapper.text()).toContain('🌙')
  })

  it('点击切换深色：写入 localStorage 并给 html 加 .dark', async () => {
    const wrapper = mount(ThemeToggle)
    await wrapper.find('button').trigger('click')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('theme')).toBe('dark')
    expect(wrapper.text()).toContain('☀️')
  })

  it('再点切回浅色', async () => {
    const wrapper = mount(ThemeToggle)
    const btn = wrapper.find('button')
    await btn.trigger('click')
    await btn.trigger('click')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(localStorage.getItem('theme')).toBe('light')
  })

  it('DOM 已是 dark 时初始显示太阳图标', async () => {
    document.documentElement.classList.add('dark')
    const wrapper = mount(ThemeToggle)
    await wrapper.vm.$nextTick() // onMounted 同步 isDark 后等待 DOM 刷新
    expect(wrapper.text()).toContain('☀️')
  })
})
