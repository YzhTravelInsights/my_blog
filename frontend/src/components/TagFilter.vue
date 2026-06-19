<template>
  <aside class="space-y-5">
    <!-- 分类 -->
    <div>
      <h3 class="text-sm font-semibold text-gray-500 uppercase mb-2">分类</h3>
      <ul class="space-y-1">
        <li>
          <button @click="$emit('select-category', '')"
            :class="['text-sm w-full text-left px-2 py-1 rounded', activeCategory === '' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100']">
            全部
          </button>
        </li>
        <li v-for="cat in categories" :key="cat">
          <button @click="$emit('select-category', cat)"
            :class="['text-sm w-full text-left px-2 py-1 rounded', activeCategory === cat ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100']">
            {{ cat }}
          </button>
        </li>
      </ul>
    </div>
    <!-- 标签 -->
    <div>
      <h3 class="text-sm font-semibold text-gray-500 uppercase mb-2">标签</h3>
      <div class="flex flex-wrap gap-1.5">
        <button v-for="t in tags" :key="t" @click="$emit('select-tag', t)"
          :class="['text-xs px-2 py-1 rounded-full transition-colors', activeTag === t ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']">
          {{ t }}
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({ categories: Array, tags: Array, activeCategory: String, activeTag: String })
defineEmits(['select-category', 'select-tag'])
</script>
