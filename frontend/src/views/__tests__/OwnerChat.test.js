/**
 * OwnerChat 视图测试：主人专属私聊页
 * 覆盖：未登录显示密钥输入 → 登录存 token → 发送消息渲染回复与好感度 →
 * 401 清 token 回登录框 → 退出登录。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import OwnerChat from '../OwnerChat.vue'

vi.mock('../../api/chat', () => ({
  sendOwnerMessage: vi.fn(),
}))

import { sendOwnerMessage } from '../../api/chat'

const TOKEN_KEY = 'blog_owner_token'

function makeWrapper() {
  return mount(OwnerChat)
}

const OK_REPLY = {
  code: 0,
  data: {
    reply: '记得那次毕业答辩吗？我们并肩走到最后。',
    emotion: 'caring',
    sources: [{ title: '毕业设计' }],
    affinity: { level: 'soul_bond', level_name: '羁绊', interaction_count: 100 },
  },
}

describe('OwnerChat', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.mocked(sendOwnerMessage).mockReset()
    vi.mocked(sendOwnerMessage).mockResolvedValue(OK_REPLY)
  })

  it('未登录时显示密钥输入框，不显示聊天界面', () => {
    const w = makeWrapper()
    expect(w.text()).toContain('主人私聊')
    expect(w.find('input[type="password"]').exists()).toBe(true)
    expect(w.text()).not.toContain('和萤宝聊天')
  })

  it('已登录（localStorage 有 token）时直接显示聊天界面', () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = makeWrapper()
    expect(w.find('input[type="password"]').exists()).toBe(false)
    // 显示聊天输入框（placeholder「和萤宝聊天...」）与占位提示
    expect(w.find('input[placeholder="和萤宝聊天..."]').exists()).toBe(true)
    expect(w.text()).toContain('在这里和萤宝私聊吧')
  })

  it('输入密钥登录：token 存入 localStorage 并显示聊天界面', async () => {
    const w = makeWrapper()
    await w.find('input[type="password"]').setValue('my-secret')
    await w.find('button').trigger('click')
    expect(localStorage.getItem(TOKEN_KEY)).toBe('my-secret')
    expect(w.find('input[type="password"]').exists()).toBe(false)
    expect(w.find('input[placeholder="和萤宝聊天..."]').exists()).toBe(true)
  })

  it('发送消息：调用 owner 接口并渲染回复与好感度徽章', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = makeWrapper()
    await w.find('input[placeholder="和萤宝聊天..."]').setValue('还记得那次吗')
    // header 有「退出」按钮，发送按钮文本是「发送」，需精确选择
    const sendBtn = w.findAll('button').find((b) => b.text() === '发送')
    await sendBtn.trigger('click')

    expect(sendOwnerMessage).toHaveBeenCalledTimes(1)
    const arg = vi.mocked(sendOwnerMessage).mock.calls[0][0]
    expect(arg.session_id).toBe('owner')
    expect(arg.token).toBe('secret-123')
    expect(arg.history).toEqual([])

    await new Promise((r) => setTimeout(r, 20))
    expect(w.text()).toContain('记得那次毕业答辩吗')
    expect(w.text()).toContain('羁绊')
  })

  it('owner 接口返回 401 时清 token 并回到登录框', async () => {
    vi.mocked(sendOwnerMessage).mockResolvedValue({ code: 2, msg: 'unauthorized', data: null })
    window.alert = vi.fn()
    localStorage.setItem(TOKEN_KEY, 'wrong-secret')
    const w = makeWrapper()
    await w.find('input[placeholder="和萤宝聊天..."]').setValue('hi')
    const sendBtn = w.findAll('button').find((b) => b.text() === '发送')
    await sendBtn.trigger('click')
    await new Promise((r) => setTimeout(r, 20))
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull()
    expect(w.find('input[type="password"]').exists()).toBe(true)
    expect(window.alert).toHaveBeenCalled()
  })

  it('退出登录：清 token 并回到登录框', async () => {
    localStorage.setItem(TOKEN_KEY, 'secret-123')
    const w = makeWrapper()
    await w.find('button[title="退出登录"]').trigger('click')
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull()
    expect(w.find('input[type="password"]').exists()).toBe(true)
  })
})
