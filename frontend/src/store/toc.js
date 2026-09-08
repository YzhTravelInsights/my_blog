/**
 * 文章目录（TOC）状态 —— Article.vue 写入，RightSidebar 读取。
 */
import { reactive } from 'vue'

export const tocState = reactive({ items: [] })

export function setToc(items) {
  tocState.items = items || []
}

export function clearToc() {
  tocState.items = []
}
