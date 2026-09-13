<!--
  顶栏：品牌 Logo「萤窗小记」＋ 导航链接 ＋ 明暗切换 ＋ 移动端抽屉按钮。
  抽屉按钮在 <1280px 时显示（左侧栏此时隐藏，需要抽屉承载侧栏内容）。
-->
<template>
  <nav
    class="sticky top-0 z-50 border-b border-border-soft"
    :style="{ background: 'color-mix(in srgb, var(--bg-base) 88%, transparent)' }"
  >
    <div class="backdrop-blur-md h-14 max-w-[1400px] mx-auto px-4 lg:px-6 flex items-center justify-between">
      <router-link to="/" class="flex items-center gap-2 shrink-0">
        <span class="nav-logo">✨</span>
        <span class="text-lg font-bold text-ink tracking-wide">{{ site.name }}</span>
      </router-link>

      <div class="flex items-center gap-2">
        <div class="hidden sm:flex items-center gap-1 text-sm text-sub mr-1">
          <router-link to="/" class="nav-link" :class="{ 'nav-link-active': route.path === '/' }">首页</router-link>
          <router-link to="/gallery" class="nav-link" :class="{ 'nav-link-active': route.path === '/gallery' }">图库</router-link>
          <router-link to="/about" class="nav-link" :class="{ 'nav-link-active': route.path === '/about' }">关于</router-link>
        </div>

        <!-- 主人专属直达：登录后内联显示（与首页/关于同款），随时直达 -->
        <div
          v-if="isOwner"
          class="hidden sm:flex items-center gap-1 text-sm mr-1 pl-1 border-l border-border-soft"
        >
          <router-link to="/chat" class="nav-link" :class="{ 'nav-link-active': route.path === '/chat' }">💬 私聊</router-link>
          <router-link to="/admin" class="nav-link" :class="{ 'nav-link-active': route.path === '/admin' }">⚙️ 管理</router-link>
          <router-link to="/write" class="nav-link" :class="{ 'nav-link-active': route.path === '/write' }">✍️ 发布</router-link>
        </div>

        <!-- 主人入口：始终可见，未登录输一次密钥即存入浏览器；已登录变绿点状态 + 退出 -->
        <OwnerMenu />

        <ThemeToggle />

        <button
          class="xl:hidden hamburger"
          aria-label="打开侧边栏"
          @click="$emit('toggle-drawer')"
        >
          <span class="hamburger-line" />
          <span class="hamburger-line" />
          <span class="hamburger-line" />
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { site } from '../config/site'
import { useOwner } from '../store/owner'
import ThemeToggle from './ThemeToggle.vue'
import OwnerMenu from './OwnerMenu.vue'

defineEmits(['toggle-drawer'])
const route = useRoute()
const { isOwner } = useOwner()
</script>

<style scoped>
.nav-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.9rem;
  height: 1.9rem;
  border-radius: 999px;
  font-size: 1rem;
  background: linear-gradient(135deg, color-mix(in srgb, var(--c-primary) 30%, transparent), color-mix(in srgb, var(--c-star) 20%, transparent));
  border: 1px solid var(--c-border);
  box-shadow: 0 0 12px var(--c-glow);
}

.nav-link {
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  color: var(--c-sub);
  transition: all 0.25s ease;
}
.nav-link:hover {
  color: var(--c-primary-deep);
  background: color-mix(in srgb, var(--c-primary) 12%, transparent);
}
.nav-link-active {
  color: var(--c-primary-deep);
  background: color-mix(in srgb, var(--c-primary) 15%, transparent);
}

.hamburger {
  display: inline-flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 2.25rem;
  height: 2.25rem;
  padding: 0 7px;
  border-radius: 999px;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  cursor: pointer;
  transition: border-color 0.25s ease;
}
.hamburger:hover {
  border-color: color-mix(in srgb, var(--c-primary) 50%, transparent);
}
.hamburger-line {
  display: block;
  height: 2px;
  border-radius: 999px;
  background: var(--c-sub);
}
</style>
