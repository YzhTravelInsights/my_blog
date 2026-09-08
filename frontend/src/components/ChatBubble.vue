<!--
  聊天气泡。保留 role 对齐类（justify-start/end），配色走主题变量。
-->
<template>
  <div :class="role === 'user' ? 'flex justify-end' : 'flex justify-start'">
    <div
      :class="
        role === 'user'
          ? 'bg-primary text-[#0b1f16]'
          : 'bg-surface text-ink border border-border-soft'
      "
      class="max-w-[80%] px-3 py-2 rounded-2xl text-sm leading-relaxed shadow-sm"
    >
      {{ content }}
      <div
        v-if="role === 'assistant' && sources?.length"
        class="mt-1 pt-1 border-t border-border-soft text-[10px] text-sub"
      >
        📎 {{ sources.map((s) => s.title).join(' / ') }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  role: String,
  content: String,
  emotion: String,
  sources: Array,
})
</script>
