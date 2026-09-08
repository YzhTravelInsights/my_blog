/**
 * Live2DCharacter 3D 模型组件测试
 *
 * 测试环境中 Three.js 无法实际渲染（无 WebGL），
 * 仅验证 Vue 组件接口（props / emits / 挂载行为）。
 */

import { describe, it, expect, vi, beforeAll } from 'vitest'
import { mount } from '@vue/test-utils'
import Live2DCharacter from '../Live2DCharacter.vue'

// 模拟 WebGL 上下文
beforeAll(() => {
  HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
    drawingBufferWidth: 200,
    drawingBufferHeight: 200,
    canvas: { width: 200, height: 200 },
  }))
})

describe('Live2DCharacter 组件接口', () => {
  it('组件可挂载，渲染容器 + canvas', () => {
    const wrapper = mount(Live2DCharacter)
    expect(wrapper.find('.three-d-container').exists()).toBe(true)
    expect(wrapper.find('canvas').exists()).toBe(true)
  })

  it('emotion 默认 normal，对应 CSS class', () => {
    const wrapper = mount(Live2DCharacter)
    expect(wrapper.find('.three-d-container').classes()).toContain('emotion-normal')
  })

  it.each(['happy', 'thinking', 'caring', 'surprised'])(
    'emotion=%s 设置正确 CSS class',
    (emo) => {
      const wrapper = mount(Live2DCharacter, { props: { emotion: emo } })
      expect(wrapper.find('.three-d-container').classes()).toContain(`emotion-${emo}`)
    },
  )

  it('modelPath 默认值为 GLB 路径', () => {
    const wrapper = mount(Live2DCharacter)
    expect(wrapper.props('modelPath')).toBe('/live2d/firefly/firefly.glb')
  })

  it('可传递自定义 modelPath', () => {
    const wrapper = mount(Live2DCharacter, { props: { modelPath: '/models/test.glb' } })
    expect(wrapper.props('modelPath')).toBe('/models/test.glb')
  })

  it('size 默认 small', () => {
    const wrapper = mount(Live2DCharacter)
    expect(wrapper.props('size')).toBe('small')
  })

  it('size=large 添加对应 class', () => {
    const wrapper = mount(Live2DCharacter, { props: { size: 'large' } })
    expect(wrapper.find('.three-d-container').classes()).toContain('size-large')
  })

  it('点击容器触发 click 事件', async () => {
    const wrapper = mount(Live2DCharacter)
    await wrapper.find('.three-d-container').trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click').length).toBe(1)
  })

  it('没有问候气泡（greeting 为空时）', () => {
    const wrapper = mount(Live2DCharacter)
    expect(wrapper.find('.speech-bubble').exists()).toBe(false)
  })
})
