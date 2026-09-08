/**
 * GalleryLightbox 灯箱测试：打开/关闭 / 左右切换 / 键盘 / 收藏按钮
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import GalleryLightbox from '../GalleryLightbox.vue'

const ITEMS = [
  { id: 'a', album: '流萤同人', title: '第一张', desc: '', url: '/g/01.png', file: '01.png' },
  { id: 'b', album: '游戏截图', title: '第二张', desc: '酷炫', url: '/g/02.png', file: '02.png' },
]

const stubs = { teleport: true } // 让 Teleport 内容渲染进组件内便于断言

describe('GalleryLightbox', () => {
  let wrapper = null

  beforeEach(() => {
    wrapper = null
  })
  afterEach(() => {
    wrapper?.unmount()
  })

  it('index 为 null 时不渲染', () => {
    wrapper = mount(GalleryLightbox, { props: { items: ITEMS, index: null }, global: { stubs } })
    expect(wrapper.find('.lb-mask').exists()).toBe(false)
  })

  it('index 有值时渲染图片与信息', () => {
    wrapper = mount(GalleryLightbox, { props: { items: ITEMS, index: 0, fav: false }, global: { stubs } })
    expect(wrapper.find('.lb-mask').exists()).toBe(true)
    expect(wrapper.text()).toContain('第一张')
    expect(wrapper.find('img').attributes('src')).toBe('/g/01.png')
    expect(wrapper.text()).toContain('1 / 2')
  })

  it('点击遮罩关闭', async () => {
    wrapper = mount(GalleryLightbox, { props: { items: ITEMS, index: 0 }, global: { stubs } })
    await wrapper.find('.lb-mask').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('左右切换按钮触发事件', async () => {
    wrapper = mount(GalleryLightbox, { props: { items: ITEMS, index: 0 }, global: { stubs } })
    await wrapper.find('.lb-nav.prev').trigger('click')
    await wrapper.find('.lb-nav.next').trigger('click')
    expect(wrapper.emitted('prev')).toBeTruthy()
    expect(wrapper.emitted('next')).toBeTruthy()
  })

  it('方向键切换 / ESC 关闭', async () => {
    wrapper = mount(GalleryLightbox, { props: { items: ITEMS, index: 0 }, global: { stubs } })
    // 组件监听的是 document，事件需派发到 document（派发到 window 不会被捕获）
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }))
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }))
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    expect(wrapper.emitted('next')).toBeTruthy()
    expect(wrapper.emitted('prev')).toBeTruthy()
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('收藏按钮触发 toggle-favorite', async () => {
    wrapper = mount(GalleryLightbox, { props: { items: ITEMS, index: 0 }, global: { stubs } })
    await wrapper.findAll('.lb-btn').find((b) => b.text() === '🤍').trigger('click')
    expect(wrapper.emitted('toggle-favorite')).toBeTruthy()
    expect(wrapper.emitted('toggle-favorite')[0][0]).toBe('a')
  })
})
