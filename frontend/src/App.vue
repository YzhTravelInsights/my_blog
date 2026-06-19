<template>
  <div class="max-w-6xl mx-auto px-4 min-h-screen flex flex-col">
    <NavBar />
    <main class="flex-1 py-6">
      <router-view />
    </main>
    <footer class="text-center text-gray-400 text-sm py-4 border-t border-gray-200">
      &copy; {{ year }} My Blog · Powered by Vue + Flask
    </footer>
    <ChatWidget />
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
import ChatWidget from './components/ChatWidget.vue'
const year = new Date().getFullYear()
</script>
