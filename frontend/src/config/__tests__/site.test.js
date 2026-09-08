/**
 * config/site 站点配置完整性测试
 * 保证以后改配置时字段齐全、类型正确。
 */
import { describe, it, expect } from 'vitest'
import { site } from '../site'

describe('站点配置完整性', () => {
  it('包含站名与副标题', () => {
    expect(site.name).toBeTruthy()
    expect(site.slogan).toBeTruthy()
  })

  it('头像为本地资源路径（不以 http 开头）', () => {
    expect(site.avatar.startsWith('http')).toBe(false)
    expect(site.avatar.startsWith('/')).toBe(true)
  })

  it('owner 包含昵称 / 学校 / 位置 / 座右铭', () => {
    for (const key of ['nickname', 'school', 'location', 'motto']) {
      expect(typeof site.owner[key]).toBe('string')
      expect(site.owner[key].length).toBeGreaterThan(0)
    }
  })

  it('社交数组 ≥4 项，每项含 name/icon/title，url 为字符串', () => {
    expect(site.socials.length).toBeGreaterThanOrEqual(4)
    for (const s of site.socials) {
      expect(typeof s.name).toBe('string')
      expect(typeof s.icon).toBe('string')
      expect(typeof s.url).toBe('string')
      expect(typeof s.title).toBe('string')
    }
  })

  it('社交图标名称均为本地已打包图标（qq/wechat/github/mail）', () => {
    const icons = new Set(['qq', 'wechat', 'github', 'mail'])
    for (const s of site.socials) {
      expect(icons.has(s.icon)).toBe(true)
    }
  })

  it('联系方式类社交（QQ/微信/邮箱）均可复制（copy 字段非空）', () => {
    const contacts = site.socials.filter((s) => ['QQ', '微信', '邮箱'].includes(s.name))
    expect(contacts.length).toBeGreaterThanOrEqual(3)
    for (const s of contacts) {
      expect(typeof s.copy).toBe('string')
      expect(s.copy.length).toBeGreaterThan(0)
    }
  })

  it('含 ICP 备案配置字段', () => {
    expect(site.icp).toBeDefined()
    expect(typeof site.icp.number).toBe('string')
    expect(site.icp.url).toContain('http')
  })

  it('含公告文案', () => {
    expect(site.announcement.length).toBeGreaterThan(0)
  })
})
