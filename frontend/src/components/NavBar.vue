<template>
  <nav class="flex items-center justify-between py-4 border-b border-gray-200 mb-6">
    <router-link to="/" class="text-xl font-bold text-gray-800 hover:text-blue-600">
      My Blog
    </router-link>
    <div class="flex gap-4 text-sm text-gray-600">
      <router-link to="/" class="hover:text-blue-600">首页</router-link>
      <router-link to="/about" class="hover:text-blue-600">关于</router-link>
    </div>
  </nav>
</template>
