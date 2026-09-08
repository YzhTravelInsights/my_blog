<!--
  页面加载动画：一颗萤火光点从左飞过 → 淡出 → 自动移除。
  纯装饰，prefers-reduced-motion 时样式表会禁用动画，不影响功能。
-->
<template>
  <Transition name="fade">
    <div v-if="visible" class="loading-firefly" aria-hidden="true" />
  </Transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const visible = ref(false)
const DURATION = 1400

onMounted(() => {
  visible.value = true
  setTimeout(() => {
    visible.value = false
  }, DURATION)
})
</script>

<style scoped>
.loading-firefly {
  position: fixed;
  top: 22%;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--c-primary);
  box-shadow:
    0 0 12px var(--c-primary),
    0 0 28px var(--c-primary),
    0 0 52px color-mix(in srgb, var(--c-primary) 70%, transparent);
  animation: fly-across 1.3s ease-in-out forwards;
  z-index: 9999;
  pointer-events: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-leave-to {
  opacity: 0;
}
</style>
