<!--
  全局布局：粒子背景 ＋ 萤火加载动画 ＋ 三栏骨架 ＋ 页脚（ICP 备案）＋ 抽屉 ＋ 聊天组件。
  响应式：
    ≥1280px   三栏常驻（左 / 主 / 右）
    1024-1279 右栏可收起（右侧悬浮按钮开关），左栏进抽屉
    <1024px   左右栏都进移动端抽屉（汉堡开合）
-->
<template>
  <div class="min-h-screen flex flex-col">
    <ParticleBackground />
    <LoadingFirefly />

    <NavBar @toggle-drawer="drawerOpen = !drawerOpen" />

    <div class="max-w-[1400px] w-full mx-auto flex-1 px-4 lg:px-6 py-6 flex items-start gap-6">
      <!-- 左栏：≥1280 常驻 -->
      <div class="hidden xl:block w-64 shrink-0 sticky top-20">
        <LeftSidebar />
      </div>

      <!-- 主内容 -->
      <main class="flex-1 min-w-0">
        <router-view />
      </main>

      <!-- 右栏：≥1280 常驻；1024-1279 由 rightOpen 控制 -->
      <div
        v-if="viewport.xl || (viewport.lg && rightOpen)"
        class="hidden lg:block w-60 shrink-0 sticky top-20"
      >
        <RightSidebar :mode="rightMode" />
      </div>
    </div>

    <!-- 1024-1279 右栏收起开关 -->
    <button
      v-if="viewport.lg && !viewport.xl"
      class="fixed right-0 top-1/2 -translate-y-1/2 z-40 flex items-center justify-center w-6 h-14 rounded-l-xl border border-r-0 border-border-soft text-sub hover:text-primary-deep transition-colors"
      :style="{ background: 'color-mix(in srgb, var(--bg-base) 92%, transparent)' }"
      :title="rightOpen ? '收起右栏' : '展开右栏'"
      @click="rightOpen = !rightOpen"
    >
      {{ rightOpen ? '›' : '‹' }}
    </button>

    <!-- 页脚 -->
    <footer class="mt-10 pb-8 px-4">
      <div class="star-divider" />
      <div class="text-center text-xs text-sub/70 mt-4 space-y-1">
        <p>&copy; {{ year }} {{ site.name }} · Powered by Vue + Flask</p>
        <p class="flex items-center justify-center gap-1.5">
          <span>🌿 总访问 {{ visit.count }} 次</span>
          <span class="text-sub/40">·</span>
          <span>📖 已读记录 {{ visit.readingCount }} 篇</span>
        </p>
        <p>
          <a
            v-if="site.icp.number"
            :href="site.icp.url"
            target="_blank"
            rel="noopener noreferrer"
            class="hover:text-primary-deep transition-colors"
          >{{ site.icp.number }}</a>
          <span v-else>ICP 备案号待补充</span>
        </p>
      </div>
    </footer>

    <!-- 移动端抽屉（<1280 时经 NavBar 汉堡打开） -->
    <Transition name="drawer">
      <div v-if="drawerOpen" class="fixed inset-0 z-[60]">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="drawerOpen = false" />
        <aside
          class="absolute left-0 top-0 bottom-0 w-80 max-w-[85vw] overflow-y-auto p-4 shadow-2xl"
          :style="{ background: 'var(--bg-base)' }"
        >
          <LeftSidebar />
          <div class="mt-4">
            <RightSidebar :mode="rightMode" />
          </div>
        </aside>
      </div>
    </Transition>

    <ChatWidget />
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { site } from './config/site'
import { visit, initVisit, addVisit } from './store/visit'
import { useOwner } from './store/owner'
import NavBar from './components/NavBar.vue'
import LeftSidebar from './components/LeftSidebar.vue'
import RightSidebar from './components/RightSidebar.vue'
import ParticleBackground from './components/ParticleBackground.vue'
import LoadingFirefly from './components/LoadingFirefly.vue'
import ChatWidget from './components/ChatWidget.vue'

const year = new Date().getFullYear()
const route = useRoute()
const router = useRouter()
const { setToken } = useOwner()

const viewport = reactive({ lg: false, xl: false })
const rightOpen = ref(false)
const drawerOpen = ref(false)

// 文章页右栏显示目录，其余显示筛选/最新
const rightMode = computed(() => (route.name === 'Article' ? 'toc' : 'home'))

function updateViewport() {
  viewport.lg = window.innerWidth >= 1024
  viewport.xl = window.innerWidth >= 1280
  if (viewport.xl) rightOpen.value = false
}

// 路由切换时关闭抽屉
watch(
  () => route.path,
  () => {
    drawerOpen.value = false
  },
)

onMounted(() => {
  updateViewport()
  window.addEventListener('resize', updateViewport)
  // 访问统计：恢复历史 + 本会话记一次
  initVisit()
  addVisit()

  // 主人 URL 令牌自动登录：/…?owner_token=SECRET → 存 localStorage 后清除 URL 参数
  // （hash 路由，令牌在 # 片段内，不会出现在服务器访问日志 / Referer）
  const q = route.query.owner_token
  if (typeof q === 'string' && q.trim()) {
    setToken(q.trim())
    router.replace({ query: {} })
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateViewport)
})
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.25s ease;
}
.drawer-enter-active aside,
.drawer-leave-active aside {
  transition: transform 0.28s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-from aside,
.drawer-leave-to aside {
  transform: translateX(-100%);
}
</style>
