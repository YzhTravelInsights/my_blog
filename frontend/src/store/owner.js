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

/**
 * 从当前地址栏取 owner_token。
 * 优先 hash（/#/admin?owner_token=xxx）——令牌在 # 片段内，不会进服务器访问日志 / Referer；
 * 兼容 search 写法（/?owner_token=xxx），取到后会从地址栏抹掉。
 */
function readUrlToken() {
  if (typeof window === 'undefined') return ''
  const hash = String(window.location.hash || '')
  const search = String(window.location.search || '')
  const m = hash.match(/[?&]owner_token=([^&#]+)/) || search.match(/[?&]owner_token=([^&#]+)/)
  return m ? decodeURIComponent(m[1]) : ''
}

// 关键：在「模块加载时」就把 URL 令牌收进 localStorage，早于任何组件挂载。
// 否则子视图（Admin/OwnerChat/Write）的 onMounted 会先于 App.vue 的 onMounted 执行，
// 那一刻 token 还是空的 → 不发请求 → 自动登录后只看到空仪表盘（要手动刷新才有数据）。
const urlToken = readUrlToken()
if (urlToken) {
  try {
    localStorage.setItem(TOKEN_KEY, urlToken.trim())
  } catch {
    /* 隐私模式等场景忽略 */
  }
  // search 里的明文令牌立刻从地址栏清掉（hash 里的那份由 App.vue 用 router.replace 清）
  try {
    const url = new URL(window.location.href)
    if (url.searchParams.has('owner_token')) {
      url.searchParams.delete('owner_token')
      window.history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`)
    }
  } catch {
    /* 忽略 */
  }
}

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
