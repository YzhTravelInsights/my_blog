<!--
  图库灯箱：点击图片全屏查看。
  - 左右切换（按钮 + 方向键）、ESC 关闭、点击遮罩关闭
  - 显示标题 / 专辑 / 描述，支持收藏与下载原图
  index 为 null 时不渲染；items 随筛选变化时自动夹紧 index。
-->
<template>
  <Teleport to="body">
    <Transition name="lightbox">
      <div v-if="item" class="lb-mask" @click.self="emit('close')">
        <!-- 顶部：标题 + 关闭 -->
        <div class="lb-head">
          <span class="lb-title">{{ item.title }}</span>
          <button class="lb-btn" aria-label="关闭" @click="emit('close')">✕</button>
        </div>

        <img :src="item.url" :alt="item.title" class="lb-img" />

        <!-- 左右切换 -->
        <button class="lb-nav prev" aria-label="上一张" @click="emit('prev')">‹</button>
        <button class="lb-nav next" aria-label="下一张" @click="emit('next')">›</button>

        <!-- 底部：信息 + 操作 -->
        <div class="lb-foot">
          <div class="lb-meta">
            <span class="lb-album">{{ item.album }}</span>
            <span v-if="item.desc" class="lb-desc">{{ item.desc }}</span>
          </div>
          <div class="lb-actions">
            <span class="lb-count">{{ pos }} / {{ items.length }}</span>
            <button
              class="lb-btn"
              :title="fav ? '取消收藏' : '收藏'"
              @click="emit('toggle-favorite', item.id)"
            >
              {{ fav ? '❤️' : '🤍' }}
            </button>
            <a class="lb-btn lb-link" :href="item.url" :download="item.file" title="下载原图">⬇</a>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  index: { type: Number, default: null }, // null = 关闭
  fav: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'prev', 'next', 'toggle-favorite'])

const item = computed(() => (props.index === null ? null : props.items[props.index]))
const pos = computed(() => (props.index === null ? 0 : props.index + 1))

function onKeydown(e) {
  if (props.index === null) return
  if (e.key === 'ArrowRight') emit('next')
  else if (e.key === 'ArrowLeft') emit('prev')
  else if (e.key === 'Escape') emit('close')
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

// 筛选变化后 items 变短时，自动夹紧 index 防止越界
watch(
  () => props.items.length,
  (len, old) => {
    if (props.index !== null && props.index >= len && len > 0) emit('close')
  },
)
</script>

<style scoped>
.lb-mask {
  position: fixed;
  inset: 0;
  z-index: 90;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(5, 8, 16, 0.88);
  backdrop-filter: blur(6px);
}

.lb-img {
  max-width: min(92vw, 1200px);
  max-height: 76vh;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  object-fit: contain;
}

.lb-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1200px;
  color: #eef6f3;
}
.lb-title { font-size: 0.95rem; font-weight: 600; }

.lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.08);
  color: #eef6f3;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.lb-nav:hover { background: rgba(140, 240, 184, 0.22); border-color: #8cf0b8; }
.lb-nav.prev { left: 1rem; }
.lb-nav.next { right: 1rem; }

.lb-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  max-width: 1200px;
  color: #9aa5b8;
  font-size: 0.8rem;
}
.lb-meta { display: flex; align-items: center; gap: 0.6rem; min-width: 0; }
.lb-album {
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  border: 1px solid rgba(140, 240, 184, 0.4);
  color: #8cf0b8;
  white-space: nowrap;
}
.lb-desc { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lb-actions { display: flex; align-items: center; gap: 0.5rem; }
.lb-count { font-variant-numeric: tabular-nums; }

.lb-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2rem;
  height: 2rem;
  padding: 0 0.6rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.08);
  color: #eef6f3;
  font-size: 0.85rem;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s, border-color 0.2s;
}
.lb-btn:hover { background: rgba(140, 240, 184, 0.22); border-color: #8cf0b8; }
.lb-link { display: inline-flex; align-items: center; }

.lightbox-enter-active, .lightbox-leave-active { transition: opacity 0.22s ease; }
.lightbox-enter-from, .lightbox-leave-to { opacity: 0; }
</style>
