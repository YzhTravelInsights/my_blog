/**
 * 访问统计与阅读记录 —— 纯前端 localStorage 实现（不碰后端）
 *
 *  - count        ：站点总访问次数（同一浏览器会话只 +1，存 sessionStorage 判重）
 *  - readingCount ：已读记录条数
 *  - history      ：最近阅读的文章列表（去重、置顶、上限 20 条）
 *
 * App.vue 挂载时调用 initVisit() + addVisit()；Article.vue 加载成功后调用 recordArticleView()。
 */
import { reactive } from 'vue'

const VISIT_KEY = 'blog_visit_count'
const SESSION_KEY = 'blog_visited_this_session'
const HISTORY_KEY = 'blog_reading_history'
const HISTORY_MAX = 20

export const visit = reactive({
  count: 0,
  readingCount: 0,
  history: [],
})

function readJSON(key, fallback) {
  try {
    const v = localStorage.getItem(key)
    return v === null ? fallback : JSON.parse(v)
  } catch {
    return fallback
  }
}

function writeJSON(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    /* 隐私模式等存储异常忽略 */
  }
}

/** 初始化：从 localStorage 恢复访问次数与阅读记录 */
export function initVisit() {
  visit.count = readJSON(VISIT_KEY, 0)
  visit.history = readJSON(HISTORY_KEY, [])
  visit.readingCount = visit.history.length
}

/** 记一次访问：同一浏览器会话只 +1，返回最新总数 */
export function addVisit() {
  let counted = false
  try {
    counted = sessionStorage.getItem(SESSION_KEY) === '1'
  } catch {}
  if (counted) return visit.count
  visit.count += 1
  writeJSON(VISIT_KEY, visit.count)
  try {
    sessionStorage.setItem(SESSION_KEY, '1')
  } catch {}
  return visit.count
}

/** 记录一次文章阅读：去重、置顶、保留上限 */
export function recordArticleView(id, title) {
  const rest = visit.history.filter((h) => h.id !== id)
  rest.unshift({ id, title, time: Date.now() })
  visit.history = rest.slice(0, HISTORY_MAX)
  visit.readingCount = visit.history.length
  writeJSON(HISTORY_KEY, visit.history)
}
