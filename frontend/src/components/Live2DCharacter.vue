<!--
  Live2D 虚拟人物组件 — 占位版本 (P2)

  Props:
    emotion: 'normal' | 'happy' | 'thinking' | 'caring' | 'surprised'
    modelPath: 模型文件路径（暂未使用）

  当前实现：根据 emotion 显示对应 CSS 动画 emoji
  后续接入：替换为 pixi-live2d-display 渲染 .model3.json
-->
<template>
  <div class="live2d-placeholder" :class="emotionClass" :title="emotionLabel">
    <span class="text-4xl select-none">{{ emoji }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  emotion: { type: String, default: 'normal' },
  modelPath: { type: String, default: '' },
})

const emit = defineEmits(['click', 'loaded'])

const emojiMap = {
  normal: '🌸',
  happy: '✨',
  thinking: '💭',
  caring: '💛',
  surprised: '💫',
}

const labelMap = {
  normal: '萤宝待机中',
  happy: '萤宝很开心',
  thinking: '萤宝思考中',
  caring: '萤宝关心你',
  surprised: '萤宝很惊讶',
}

const emoji = computed(() => emojiMap[props.emotion] || '🌸')
const emotionLabel = computed(() => labelMap[props.emotion] || '萤宝')

const emotionClass = computed(() => `emotion-${props.emotion}`)
</script>

<style scoped>
.live2d-placeholder {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #dbeafe, #ede9fe);
  transition: transform 0.3s, background 0.3s;
  cursor: pointer;
  user-select: none;
}
.emotion-normal { animation: breathe 3s ease-in-out infinite; }
.emotion-happy { animation: bounce 0.6s ease-in-out infinite; background: linear-gradient(135deg, #fef3c7, #fce7f3); }
.emotion-thinking { animation: think 1.5s ease-in-out infinite; background: linear-gradient(135deg, #e0e7ff, #ede9fe); }
.emotion-caring { animation: pulse 1s ease-in-out infinite; background: linear-gradient(135deg, #fce7f3, #fef3c7); }
.emotion-surprised { animation: surprise 0.4s ease-in-out 2; background: linear-gradient(135deg, #fef3c7, #dbeafe); }

@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}
@keyframes bounce {
  0%, 100% { transform: translateY(0) scale(1); }
  30% { transform: translateY(-8px) scale(1.05); }
  50% { transform: translateY(0) scale(1); }
  70% { transform: translateY(-4px) scale(1.02); }
}
@keyframes think {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.12); }
}
@keyframes surprise {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.25); }
}
</style>
