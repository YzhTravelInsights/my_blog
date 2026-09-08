<!--
  明暗主题切换按钮。
  - 切换 <html>.dark 类 + 写 localStorage('theme')
  - 默认跟随系统偏好（由 index.html 内联脚本在渲染前打上 .dark）
-->
<template>
  <button
    class="theme-toggle"
    :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
    :aria-label="isDark ? '切换到浅色模式' : '切换到深色模式'"
    @click="toggle"
  >
    <span v-if="isDark" class="text-base leading-none">☀️</span>
    <span v-else class="text-base leading-none">🌙</span>
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const THEME_KEY = 'theme'
const isDark = ref(false)

/** 从 DOM 读取当前主题状态（index.html 已在渲染前按 localStorage/系统偏好打上 .dark） */
function syncFromDom() {
  isDark.value = document.documentElement.classList.contains('dark')
}

function toggle() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  try {
    localStorage.setItem(THEME_KEY, isDark.value ? 'dark' : 'light')
  } catch {
    /* 忽略隐私模式等存储异常 */
  }
}

onMounted(syncFromDom)
</script>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 999px;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  backdrop-filter: blur(12px);
  color: var(--c-sub);
  transition: all 0.25s ease;
  cursor: pointer;
}
.theme-toggle:hover {
  color: var(--c-primary-deep);
  border-color: color-mix(in srgb, var(--c-primary) 50%, transparent);
  box-shadow: 0 0 14px var(--c-glow);
}
</style>
