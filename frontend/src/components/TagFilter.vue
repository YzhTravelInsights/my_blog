<!--
  分类 / 标签筛选。选中态用萤火绿主题色。
-->
<template>
  <div class="space-y-5">
    <!-- 分类 -->
    <div>
      <h3 class="text-sm font-semibold text-sub mb-2">分类</h3>
      <ul class="space-y-1">
        <li>
          <button
            @click="$emit('select-category', '')"
            :class="[
              'text-sm w-full text-left px-2 py-1 rounded transition-colors',
              activeCategory === '' ? 'bg-primary/15 text-primary-deep' : 'text-sub hover:bg-primary/10',
            ]"
          >
            全部
          </button>
        </li>
        <li v-for="cat in categories" :key="cat">
          <button
            @click="$emit('select-category', cat)"
            :class="[
              'text-sm w-full text-left px-2 py-1 rounded transition-colors',
              activeCategory === cat ? 'bg-primary/15 text-primary-deep' : 'text-sub hover:bg-primary/10',
            ]"
          >
            {{ cat }}
          </button>
        </li>
      </ul>
    </div>

    <!-- 标签 -->
    <div>
      <h3 class="text-sm font-semibold text-sub mb-2">标签</h3>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="t in tags"
          :key="t"
          @click="$emit('select-tag', t)"
          :class="[
            'text-xs px-2.5 py-1 rounded-full transition-all duration-200',
            activeTag === t
              ? 'bg-primary text-[#0b1f16] shadow-glow'
              : 'bg-surface border border-border-soft text-sub hover:border-primary/40 hover:text-primary-deep',
          ]"
        >
          {{ t }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  categories: { type: Array, default: () => [] },
  tags: { type: Array, default: () => [] },
  activeCategory: { type: String, default: '' },
  activeTag: { type: String, default: '' },
})
defineEmits(['select-category', 'select-tag'])
</script>
