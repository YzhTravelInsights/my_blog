/**
 * IconSocial 内联图标测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import IconSocial from '../IconSocial.vue'

describe('IconSocial', () => {
  it.each(['qq', 'wechat', 'github', 'mail'])('渲染 %s 图标（内联 svg）', (name) => {
    const wrapper = mount(IconSocial, { props: { name } })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('未知名称渲染空', () => {
    const wrapper = mount(IconSocial, { props: { name: 'unknown' } })
    expect(wrapper.find('svg').exists()).toBe(false)
  })
})
