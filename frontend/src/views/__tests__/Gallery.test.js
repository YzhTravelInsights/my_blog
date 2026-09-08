/**
 * Gallery 视图测试：渲染 / 专辑筛选 / 收藏 / 随机一张 / 空状态
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHashHistory } from 'vue-router'

vi.mock('../../store/galleryData', () => ({
  loadGalleryRaw: () => [
    { id: 'a', album: '流萤同人', title: '流萤-01', desc: '', url: '/g/01.png', file: '01.png' },
    { id: 'b', album: '游戏截图', title: '酷炫截图', desc: '描述', url: '/g/b.jpg', file: 'b.jpg' },
    { id: 'c', album: '流萤同人', title: '流萤-02', desc: '', url: '/g/02.png', file: '02.png' },
  ],
}))

// 灯箱单独测试，这里用桩并暴露 props 以便断言「点击打开」
vi.mock('../../components/GalleryLightbox.vue', () => ({
  default: {
    name: 'LightboxStub',
    props: ['items', 'index'],
    template: '<div class="lb-stub" />',
  },
}))

import Gallery from '../Gallery.vue'
import { gallery, visibleItems } from '../../store/gallery'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'Home', component: { template: '<div/>' } },
    { path: '/gallery', name: 'Gallery', component: Gallery },
  ],
})

function mountGallery() {
  return mount(Gallery, { global: { plugins: [router] } })
}

beforeEach(() => {
  localStorage.clear()
  gallery.loaded = false
  gallery.favorites = []
  gallery.currentAlbum = '全部'
})

describe('Gallery 视图', () => {
  it('渲染全部图片与统计', () => {
    const wrapper = mountGallery()
    expect(wrapper.text()).toContain('图库')
    expect(wrapper.text()).toContain('共 3 张')
    expect(wrapper.text()).toContain('流萤-01')
    expect(wrapper.text()).toContain('酷炫截图')
    expect(wrapper.find('.gallery-item').exists()).toBe(true)
  })

  it('点击专辑筛选图片', async () => {
    const wrapper = mountGallery()
    await wrapper.findAll('.chip').find((b) => b.text() === '游戏截图').trigger('click')
    expect(wrapper.text()).toContain('酷炫截图')
    expect(wrapper.text()).not.toContain('流萤-01')
  })

  it('点击图片打开灯箱（index 传给 Lightbox）', async () => {
    const wrapper = mountGallery()
    await wrapper.findAll('.gallery-item')[0].trigger('click')
    expect(wrapper.findComponent({ name: 'LightboxStub' }).props('index')).toBe(0)
  })

  it('收藏图片后显示收藏专辑', async () => {
    const wrapper = mountGallery()
    await wrapper.findAll('.gallery-fav')[0].trigger('click')
    expect(gallery.favorites).toEqual(['a'])
    // 收藏专辑只显示收藏的
    await wrapper.findAll('.chip').find((b) => b.text() === '❤️ 收藏').trigger('click')
    expect(wrapper.findAll('.gallery-item')).toHaveLength(1)
    expect(wrapper.text()).toContain('流萤-01')
    expect(wrapper.text()).not.toContain('酷炫截图')
  })

  it('收藏为空时显示占位', async () => {
    const wrapper = mountGallery()
    await wrapper.findAll('.chip').find((b) => b.text() === '❤️ 收藏').trigger('click')
    expect(wrapper.text()).toContain('还没有收藏的图片')
  })

  it('随机一张会打开灯箱', async () => {
    const wrapper = mountGallery()
    await wrapper.findAll('button').find((b) => b.text().includes('随机一张')).trigger('click')
    const idx = wrapper.findComponent({ name: 'LightboxStub' }).props('index')
    expect(idx).toBeGreaterThanOrEqual(0)
    expect(idx).toBeLessThan(visibleItems.value.length)
  })
})
