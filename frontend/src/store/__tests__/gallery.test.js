/**
 * gallery store 测试：专辑筛选 / 收藏 / localStorage 持久化
 * mock 掉 galleryData 的自动扫描，避免加载真实图片
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../galleryData', () => ({
  loadGalleryRaw: () => [
    { id: 'a', album: '流萤同人', title: '流萤-01', desc: '', url: '/g/01.png', file: '流萤-01.png' },
    { id: 'b', album: '游戏截图', title: '截图', desc: '一张截图', url: '/g/b.jpg', file: 'b.jpg' },
    { id: 'c', album: '流萤同人', title: '流萤-02', desc: '', url: '/g/02.png', file: '流萤-02.png' },
  ],
}))

import { gallery, albums, visibleItems, initGallery, setAlbum, toggleFavorite, isFavorite } from '../gallery'

beforeEach(() => {
  localStorage.clear()
  gallery.loaded = false
  gallery.favorites = []
  gallery.currentAlbum = '全部'
})

describe('gallery · 数据与筛选', () => {
  it('加载全部图片', () => {
    expect(gallery.items).toHaveLength(3)
  })

  it('专辑 tab：全部 / 收藏 / 各专辑', () => {
    expect(albums.value).toEqual(['全部', '❤️ 收藏', '流萤同人', '游戏截图'])
  })

  it('默认显示全部图片', () => {
    expect(visibleItems.value).toHaveLength(3)
  })

  it('按专辑筛选', () => {
    setAlbum('流萤同人')
    expect(visibleItems.value.map((i) => i.id)).toEqual(['a', 'c'])
    setAlbum('游戏截图')
    expect(visibleItems.value.map((i) => i.id)).toEqual(['b'])
  })
})

describe('gallery · 收藏', () => {
  it('收藏/取消收藏并写入 localStorage', () => {
    initGallery()
    toggleFavorite('a')
    expect(isFavorite('a')).toBe(true)
    expect(JSON.parse(localStorage.getItem('blog_gallery_favorites'))).toEqual(['a'])

    toggleFavorite('a')
    expect(isFavorite('a')).toBe(false)
    expect(JSON.parse(localStorage.getItem('blog_gallery_favorites'))).toEqual([])
  })

  it('收藏专辑只显示收藏的图片', () => {
    initGallery()
    toggleFavorite('a')
    toggleFavorite('b')
    setAlbum('❤️ 收藏')
    expect(visibleItems.value.map((i) => i.id)).toEqual(['a', 'b'])
  })

  it('initGallery 从 localStorage 恢复收藏', () => {
    localStorage.setItem('blog_gallery_favorites', JSON.stringify(['b', 'c']))
    initGallery()
    expect(gallery.favorites).toEqual(['b', 'c'])
    expect(isFavorite('c')).toBe(true)
  })
})
