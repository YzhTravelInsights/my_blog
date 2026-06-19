/**
 * Live2DCharacter 占位组件测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Live2DCharacter from '../Live2DCharacter.vue'

describe('Live2DCharacter', () => {
  it('默认 emotion 为 normal 显示 🌸', () => {
    const wrapper = mount(Live2DCharacter)
    expect(wrapper.text()).toContain('🌸')
    expect(wrapper.classes()).toContain('emotion-normal')
  })

  it('emotion=happy 显示 ✨', () => {
    const wrapper = mount(Live2DCharacter, { props: { emotion: 'happy' } })
    expect(wrapper.text()).toContain('✨')
    expect(wrapper.classes()).toContain('emotion-happy')
  })

  it('emotion=thinking 显示 💭', () => {
    const wrapper = mount(Live2DCharacter, { props: { emotion: 'thinking' } })
    expect(wrapper.text()).toContain('💭')
    expect(wrapper.classes()).toContain('emotion-thinking')
  })

  it('emotion=caring 显示 💛', () => {
    const wrapper = mount(Live2DCharacter, { props: { emotion: 'caring' } })
    expect(wrapper.text()).toContain('💛')
  })

  it('emotion=surprised 显示 💫', () => {
    const wrapper = mount(Live2DCharacter, { props: { emotion: 'surprised' } })
    expect(wrapper.text()).toContain('💫')
  })

  it('未知 emotion 回退 🌸', () => {
    const wrapper = mount(Live2DCharacter, { props: { emotion: 'unknown' } })
    expect(wrapper.text()).toContain('🌸')
  })

  it('传递 modelPath prop', () => {
    const wrapper = mount(Live2DCharacter, {
      props: { modelPath: 'live2d/firefly/firefly.model3.json' },
    })
    expect(wrapper.props('modelPath')).toBe('live2d/firefly/firefly.model3.json')
  })
})
