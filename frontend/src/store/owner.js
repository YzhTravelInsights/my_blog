/**
 * 主人身份状态（跨组件共享）
 *
 * 令牌只存浏览器 localStorage（key: blog_owner_token），不进前端代码 / git。
 * 访问方式：
 *   1. 携带 URL 令牌访问任意页面：/…?owner_token=OWNER_SECRET
 *      （App.vue 全局读取 → 存入 localStorage → 自动清除 URL 参数）
 *   2. 在 /chat /admin /write 手动输入 OWNER_SECRET 登录
 *
 * 访客无令牌：isOwner=false，不显示任何登录入口（私聊/管理/写文章入口隐藏）。
 */
import { ref, computed } from 'vue'

export const TOKEN_KEY = 'blog_owner_token'

function readToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

// 模块级共享 ref 保证各组件响应式同步；useOwner() 每次 setup 时从
// localStorage 重读一次，覆盖「跨挂载直接被改」的场景（如测试、多标签页）。
const token = ref(readToken())

const isOwner = computed(() => !!token.value)

function setToken(t) {
  token.value = (t || '').trim()
  try {
    if (token.value) localStorage.setItem(TOKEN_KEY, token.value)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    /* 隐私模式等场景忽略 */
  }
}

function logout() {
  setToken('')
}

export function useOwner() {
  token.value = readToken()
  return { token, isOwner, setToken, logout, TOKEN_KEY }
}
