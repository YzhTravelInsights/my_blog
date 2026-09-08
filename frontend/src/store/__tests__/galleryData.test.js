/**
 * galleryData 真实扫描测试：验证 import.meta.glob 确实扫到了 src/assets/gallery/ 下的图片。
 * （回归：之前 glob 相对路径写错导致匹配 0 张、图库空白）
 */
import { describe, it, expect } from 'vitest'
import { loadGalleryRaw } from '../galleryData'

describe('galleryData · 真实文件扫描', () => {
  it('扫描到至少 1 张图，且按专辑/标题正确解析', () => {
    const list = loadGalleryRaw()
    expect(list.length).toBeGreaterThan(0)

    const albums = new Set(list.map((i) => i.album))
    expect(albums.has('流萤同人')).toBe(true)

    const first = list.find((i) => i.album === '流萤同人')
    expect(first).toBeTruthy()
    expect(first.title).toMatch(/^流萤-\d+$/) // 文件名解析出的标题
    expect(first.url).toContain('/assets/gallery/')
    expect(first.id).toContain('assets/gallery')
  })
})
