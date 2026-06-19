<!--
  萤宝虚拟人物组件

  当前：静态图片 + CSS 动画（临时版本）
  后续：替换为 pixi-live2d-display 渲染 .model3.json（见 文档/Live2D模型接入指南.md）

  Props:
    emotion - 'normal' | 'happy' | 'thinking' | 'caring' | 'surprised'
    modelPath - 模型文件路径（暂未使用，预留接口）
-->
<template>
  <div class="firefly-avatar" :class="emotionClass" :title="emotionLabel" @click="$emit('click')">
    <img :src="avatarSrc" alt="萤宝" class="avatar-img" />
    <div class="emotion-badge" v-if="emotion !== 'normal'">{{ emotionIcon }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  emotion: { type: String, default: 'normal' },
  modelPath: { type: String, default: 'live2d/firefly/firefly.model3.json' },
})

defineEmits(['click', 'loaded'])

const avatarSrc = computed(() => '/firefly-avatar.png')

const emotionIcon = computed(() => ({
  happy: '✨', thinking: '💭', caring: '💛', surprised: '💫',
}[props.emotion] || ''))

const emotionLabel = computed(() => ({
  normal: '萤宝待机中', happy: '萤宝很开心', thinking: '萤宝思考中',
  caring: '萤宝关心你', surprised: '萤宝很惊讶',
}[props.emotion] || '萤宝'))

const emotionClass = computed(() => `emotion-${props.emotion}`)
</script>

<style scoped>
.firefly-avatar {
  position: relative;
  width: 32px; height: 32px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 0 0 2px #93c5fd;
  user-select: none;
}
.avatar-img {
  width: 100%; height: 100%;
  object-fit: cover;
}
.emotion-badge {
  position: absolute;
  bottom: -2px; right: -2px;
  font-size: 16px;
  line-height: 1;
}
/* 动画 */
.emotion-normal { animation: breathe 3s ease-in-out infinite; }
.emotion-happy { animation: bounce 0.6s ease-in-out infinite; box-shadow: 0 0 8px 3px #fbbf24; }
.emotion-thinking { animation: think 1.5s ease-in-out infinite; box-shadow: 0 0 8px 3px #a78bfa; }
.emotion-caring { animation: pulse 1s ease-in-out infinite; box-shadow: 0 0 8px 3px #f472b6; }
.emotion-surprised { animation: surprise 0.4s ease-in-out 2; box-shadow: 0 0 8px 3px #60a5fa; }
@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}
@keyframes bounce {
  0%, 100% { transform: translateY(0) scale(1); }
  30% { transform: translateY(-6px) scale(1.05); }
  50% { transform: translateY(0) scale(1); }
  70% { transform: translateY(-3px) scale(1.02); }
}
@keyframes think {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-4deg); }
  75% { transform: rotate(4deg); }
}
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
@keyframes surprise {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}
</style>
