/**
 * ChatBubble 组件测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChatBubble from '../ChatBubble.vue'

describe('ChatBubble', () => {
  it('渲染用户消息右对齐', () => {
    const wrapper = mount(ChatBubble, {
      props: { role: 'user', content: '你好' },
    })
    expect(wrapper.text()).toContain('你好')
    expect(wrapper.html()).toContain('justify-end')
  })

  it('渲染助手消息左对齐', () => {
    const wrapper = mount(ChatBubble, {
      props: { role: 'assistant', content: '开拓者好～', emotion: 'happy' },
    })
    expect(wrapper.text()).toContain('开拓者好～')
    expect(wrapper.html()).toContain('justify-start')
  })

  it('显示 sources 引用', () => {
    const wrapper = mount(ChatBubble, {
      props: {
        role: 'assistant',
        content: '根据文章...',
        sources: [{ title: 'Conda教程', relevance: 0.9 }],
      },
    })
    expect(wrapper.text()).toContain('Conda教程')
  })
})
