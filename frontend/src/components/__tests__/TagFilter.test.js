/**
 * TagFilter 组件测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TagFilter from '../TagFilter.vue'

const props = {
  categories: ['Python', 'AI', 'Web'],
  tags: ['Flask', 'Conda', 'Vue', 'RAG'],
  activeCategory: '',
  activeTag: '',
}

describe('TagFilter', () => {
  it('渲染所有分类', () => {
    const wrapper = mount(TagFilter, { props })
    const text = wrapper.text()
    expect(text).toContain('Python')
    expect(text).toContain('AI')
    expect(text).toContain('Web')
    expect(text).toContain('全部')
  })

  it('渲染所有标签', () => {
    const wrapper = mount(TagFilter, { props })
    const text = wrapper.text()
    expect(text).toContain('Flask')
    expect(text).toContain('Conda')
    expect(text).toContain('Vue')
    expect(text).toContain('RAG')
  })

  it('点击分类触发事件', async () => {
    const wrapper = mount(TagFilter, { props })
    await wrapper.find('button').trigger('click') // 点击"全部"
    expect(wrapper.emitted('select-category')).toBeTruthy()
  })

  it('activeCategory 高亮', () => {
    const wrapper = mount(TagFilter, {
      props: { ...props, activeCategory: 'Python' },
    })
    const activeBtn = wrapper.findAll('button').find(b => b.text() === 'Python')
    expect(activeBtn.classes()).toContain('bg-blue-100')
  })
})
