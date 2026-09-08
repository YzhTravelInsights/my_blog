/**
 * 图库状态：图片列表（来自 galleryData 自动扫描）、专辑筛选、收藏（localStorage）。
 */
import { reactive, computed } from 'vue'
import { loadGalleryRaw } from './galleryData'

const FAV_KEY = 'blog_gallery_favorites'

export const gallery = reactive({
  items: loadGalleryRaw(),
  favorites: [],       // 收藏的图片 id 列表
  currentAlbum: '全部', // '全部' | '❤️ 收藏' | <专辑名>
  loaded: false,        // 收藏是否已从 localStorage 恢复
})

/** 专辑 tab 列表：全部 / 收藏 / 各专辑 */
export const albums = computed(() => {
  const set = new Set(gallery.items.map((i) => i.album))
  return ['全部', '❤️ 收藏', ...set]
})

/** 当前筛选下的可见图片 */
export const visibleItems = computed(() => {
  if (gallery.currentAlbum === '❤️ 收藏') {
    return gallery.items.filter((i) => gallery.favorites.includes(i.id))
  }
  if (gallery.currentAlbum === '全部') return gallery.items
  return gallery.items.filter((i) => i.album === gallery.currentAlbum)
})

export function initGallery() {
  if (gallery.loaded) return
  try {
    const raw = localStorage.getItem(FAV_KEY)
    gallery.favorites = raw ? JSON.parse(raw) : []
  } catch {
    gallery.favorites = []
  }
  gallery.loaded = true
}

export function setAlbum(name) {
  gallery.currentAlbum = name
}

export function toggleFavorite(id) {
  const idx = gallery.favorites.indexOf(id)
  if (idx >= 0) gallery.favorites.splice(idx, 1)
  else gallery.favorites.push(id)
  try {
    localStorage.setItem(FAV_KEY, JSON.stringify(gallery.favorites))
  } catch {
    /* 隐私模式等存储异常忽略 */
  }
}

export function isFavorite(id) {
  return gallery.favorites.includes(id)
}
