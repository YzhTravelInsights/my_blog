<!--
  文章卡片：磨砂玻璃 + hover 上浮萤光。
-->
<template>
  <article class="glass-card glass-card-hover p-5">
    <div class="flex items-center gap-2 text-xs text-sub mb-2">
      <span class="chip">{{ article.category }}</span>
      <span>{{ article.date }}</span>
    </div>
    <router-link
      :to="`/article/${article.id}`"
      class="block text-lg font-semibold text-ink hover:text-primary-deep transition-colors no-underline"
    >
      {{ article.title }}
    </router-link>
    <p class="text-sm text-sub mt-2 leading-relaxed">{{ article.summary }}</p>
    <div v-if="article.tags.length" class="flex flex-wrap gap-1.5 mt-3">
      <span v-for="t in article.tags" :key="t" class="chip">#{{ t }}</span>
    </div>
  </article>
</template>

<script setup>
defineProps({ article: Object })
</script>
