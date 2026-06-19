<template>
  <div :class="role === 'user' ? 'flex justify-end' : 'flex justify-start'">
    <div :class="role === 'user' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 border border-gray-200'"
      class="max-w-[80%] px-3 py-2 rounded-2xl text-sm leading-relaxed shadow-sm">
      {{ content }}
      <div v-if="role === 'assistant' && sources?.length" class="mt-1 pt-1 border-t border-gray-200 text-[10px] text-gray-400">
        📎 {{ sources.map(s => s.title).join(' / ') }}
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
