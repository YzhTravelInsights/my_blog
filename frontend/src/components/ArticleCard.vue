<template>
  <article class="border-b border-gray-100 py-5 hover:bg-gray-50 px-2 -mx-2 rounded transition-colors">
    <div class="flex items-center gap-2 text-xs text-gray-400 mb-1">
      <span class="bg-blue-100 text-blue-700 px-2 py-0.5 rounded">{{ article.category }}</span>
      <span>{{ article.date }}</span>
    </div>
    <router-link :to="`/article/${article.id}`" class="text-lg font-semibold text-gray-800 hover:text-blue-600 no-underline">
      {{ article.title }}
    </router-link>
    <p class="text-sm text-gray-500 mt-2 leading-relaxed">{{ article.summary }}</p>
    <div class="flex gap-1 mt-2" v-if="article.tags.length">
      <span v-for="t in article.tags" :key="t" class="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{{ t }}</span>
    </div>
  </article>
</template>

<script setup>
defineProps({ article: Object })
</script>
