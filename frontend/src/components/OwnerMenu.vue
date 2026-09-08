<!--
  主人入口（导航栏下拉，始终可见）：
    - 未登录：点开 → 输一次密钥 → 存入浏览器 localStorage → 变成三个入口链接
    - 已登录：点开 → 私聊 / 管理后台 / 发布文章 + 退出
  密钥只存本机浏览器（blog_owner_token），三页通用，之后每次打开都是登录态。
  访客看得到入口，但没有密钥进不去；也可以携 ?owner_token= 访问直接免输。
-->
<template>
  <div class="relative owner-menu shrink-0">
    <button
      class="owner-btn"
      :class="{ 'owner-btn-active': open, 'owner-btn-logged': isOwner }"
      :title="isOwner ? '主人已登录 · 点开进私聊/管理/发布' : '主人登录'"
      aria-label="主人入口"
      @click="open = !open"
    >
      <span class="relative inline-flex">
        <span>👑</span>
        <span v-if="isOwner" class="owner-dot" title="已登录" />
      </span>
      <span class="hidden sm:inline">{{ isOwner ? '主人·已登录' : '主人' }}</span>
    </button>

    <!-- 点击外部关闭 -->
    <div v-if="open" class="fixed inset-0 z-40" @click="open = false" />

    <Transition name="owner-menu">
      <div v-if="open" class="owner-panel">
        <!-- 已登录：三个入口 + 退出 -->
        <template v-if="isOwner">
          <router-link to="/chat" class="owner-item" @click="open = false">
            <span>💬</span> 私聊
          </router-link>
          <router-link to="/admin" class="owner-item" @click="open = false">
            <span>⚙️</span> 管理后台
          </router-link>
          <router-link to="/write" class="owner-item" @click="open = false">
            <span>✍️</span> 发布文章
          </router-link>
          <div class="owner-divider" />
          <button class="owner-item" @click="handleLogout">
            🚪 退出登录
          </button>
        </template>

        <!-- 未登录：密钥输入 -->
        <template v-else>
          <p class="owner-hint">输入密钥进入（只存本机浏览器，一次即可）</p>
          <input
            v-model="secretInput"
            type="password"
            class="glass-input w-full py-1.5 text-sm"
            placeholder="OWNER_SECRET"
            @keyup.enter="handleLogin"
          />
          <button
            class="btn-primary w-full mt-2 py-1.5 text-sm"
            :disabled="!secretInput.trim()"
            @click="handleLogin"
          >
            进入
          </button>
        </template>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useOwner } from '../store/owner'

const { isOwner, setToken, logout } = useOwner()
const open = ref(false)
const secretInput = ref('')

function handleLogin() {
  const s = secretInput.value.trim()
  if (!s) return
  setToken(s)
  secretInput.value = ''
  // 登录后保持下拉打开，直接展示三个入口
}

function handleLogout() {
  logout()
  open.value = true // 停留在下拉，回到密钥输入框
}
</script>

<style scoped>
@reference "../style.css";

.owner-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.85rem;
  color: var(--c-sub);
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  transition: all 0.25s ease;
  cursor: pointer;
}
.owner-btn:hover,
.owner-btn-active {
  color: var(--c-primary-deep);
  border-color: color-mix(in srgb, var(--c-primary) 50%, transparent);
  box-shadow: 0 0 10px var(--c-glow);
}
/* 已登录：按钮带荧光绿描边，一眼可辨登录态 */
.owner-btn-logged {
  border-color: color-mix(in srgb, var(--c-primary) 60%, transparent);
}
.owner-dot {
  position: absolute;
  top: -2px;
  right: -4px;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--c-primary);
  box-shadow: 0 0 6px var(--c-glow);
  animation: owner-dot-pulse 2s ease-in-out infinite;
}
@keyframes owner-dot-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}
.owner-panel {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 230px;
  max-width: calc(100vw - 2rem);
  z-index: 50;
  padding: 0.6rem;
  border-radius: 0.9rem;
  background: color-mix(in srgb, var(--c-surface) 96%, var(--c-ink));
  border: 1px solid var(--c-border);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
}
.owner-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.7rem;
  border-radius: 0.6rem;
  font-size: 0.85rem;
  color: var(--c-ink);
  text-align: left;
  cursor: pointer;
  transition: background 0.18s ease;
}
.owner-item:hover {
  background: color-mix(in srgb, var(--c-primary) 12%, transparent);
  color: var(--c-primary-deep);
}
.owner-divider {
  height: 1px;
  margin: 0.35rem 0;
  background: var(--c-border);
}
.owner-hint {
  font-size: 0.72rem;
  color: var(--c-sub);
  line-height: 1.5;
  padding: 0 0.2rem 0.4rem;
}
.owner-menu-enter-active,
.owner-menu-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.owner-menu-enter-from,
.owner-menu-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
