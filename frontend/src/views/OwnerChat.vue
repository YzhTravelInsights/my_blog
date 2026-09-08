<!--
  主人专属独立聊天页（/chat）
  仅博主可用：携 ?owner_token= 访问自动登录，或手动输入 OWNER_SECRET（存浏览器本地）。
  走 owner 模式 API（/api/chat/owner）：好感度 / 长期记忆 / 人格演化全链路，
  与右下角访客聊天窗完全独立，不影响访客体验。
  密钥只存本机浏览器，不进前端代码 / git。
-->
<template>
  <div class="flex justify-center px-2">
    <!-- 未登录：密钥输入 -->
    <div v-if="!token" class="w-full max-w-md mt-10 glass-card p-6">
      <h2 class="text-lg font-bold text-ink flex items-center gap-2">
        <span class="nav-logo">✨</span> 主人私聊
      </h2>
      <p class="text-xs text-sub mt-1.5 leading-relaxed">
        输入 <code class="text-primary-deep">OWNER_SECRET</code> 进入（仅博主可用），
        或访问时携带 <code class="text-primary-deep">?owner_token=OWNER_SECRET</code> 自动登录。
        密钥只保存在你的浏览器本地，访客无法进入。
      </p>
      <input
        v-model="secretInput"
        type="password"
        class="glass-input w-full mt-4 py-2"
        placeholder="OWNER_SECRET"
        @keyup.enter="login"
      />
      <button class="btn-primary w-full mt-3 py-2" :disabled="!secretInput.trim()" @click="login">
        进入
      </button>
    </div>

    <!-- 已登录：聊天界面 -->
    <div v-else class="w-full max-w-xl flex flex-col mt-4 rounded-2xl border border-border-soft overflow-hidden chat-card">
      <!-- 头部 -->
      <div
        class="flex items-center justify-between px-4 py-2.5 shrink-0"
        :style="{ background: 'linear-gradient(135deg, var(--c-primary), var(--c-star))', color: '#0b1f16' }"
      >
        <span class="font-semibold text-sm">✨ 萤宝 · 主人私聊</span>
        <div class="flex items-center gap-3">
          <span v-if="affinity" class="text-xs font-medium opacity-90">
            💞 {{ affinity.level_name }} · {{ affinity.interaction_count }} 次互动
          </span>
          <button class="opacity-75 hover:opacity-100 text-xs transition-opacity" title="退出登录" @click="handleLogout">
            退出
          </button>
        </div>
      </div>

      <!-- 消息区 -->
      <div
        ref="msgContainer"
        class="flex-1 overflow-y-auto px-3 py-3 space-y-3"
        :style="{ minHeight: '52vh', maxHeight: '62vh' }"
      >
        <div v-if="messages.length === 0" class="text-center text-sub/50 text-sm mt-16">
          在这里和萤宝私聊吧～ 记忆 / 好感度 / 人格全开 ✨
        </div>
        <ChatBubble
          v-for="(m, i) in messages"
          :key="i"
          :role="m.role"
          :content="m.content"
          :emotion="m.emotion"
          :sources="m.sources"
        />
        <div v-if="typing" class="text-sub text-xs pl-2">
          <span class="typing-dot" />
          <span class="typing-dot" style="animation-delay:0.15s" />
          <span class="typing-dot" style="animation-delay:0.3s" />
        </div>
      </div>

      <div class="text-center text-sub/50 text-[10px] py-1 shrink-0">对话保存在本地浏览器</div>

      <!-- 输入区 -->
      <div class="flex items-center gap-2 px-3 py-2 border-t border-border-soft shrink-0">
        <input
          v-model="input"
          class="glass-input flex-1 py-1.5"
          placeholder="和萤宝聊天..."
          @keyup.enter="send"
        />
        <button class="btn-primary px-3 py-1.5" :disabled="!input.trim() || typing" @click="send">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { sendOwnerMessage } from '../api/chat'
import ChatBubble from '../components/ChatBubble.vue'
import { useOwner } from '../store/owner'

const MSG_KEY = 'blog_owner_chat_messages'

const { token, setToken, logout } = useOwner()
const secretInput = ref('')
const messages = ref([])
const affinity = ref(null) // 最近一次接口返回的好感度状态 { level_name, interaction_count }
const input = ref('')
const typing = ref(false)
const msgContainer = ref(null)

onMounted(loadHistory)

// ---------- 本地历史 ----------
function loadHistory() {
  try {
    const saved = localStorage.getItem(MSG_KEY)
    if (saved) messages.value = JSON.parse(saved)
  } catch { /* 忽略损坏历史 */ }
}

function saveHistory() {
  try {
    localStorage.setItem(MSG_KEY, JSON.stringify(messages.value))
  } catch { /* 忽略配额 */ }
}

// ---------- 登录 / 退出 ----------
function login() {
  const s = secretInput.value.trim()
  if (!s) return
  setToken(s)
  secretInput.value = ''
  loadHistory()
}

function handleLogout() {
  logout()
  messages.value = []
  localStorage.removeItem(MSG_KEY)
  affinity.value = null
}

// ---------- 发送 ----------
async function send() {
  const text = input.value.trim()
  if (!text || typing.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  saveHistory()
  typing.value = true
  scrollBottom()

  // 传给后端的 history 不含刚 push 的这条（后端会把 message 作为最后一条追加）
  const history = messages.value
    .slice(0, -1)
    .slice(-20)
    .map((m) => ({ role: m.role, content: m.content }))

  try {
    const res = await sendOwnerMessage({
      message: text,
      session_id: 'owner',
      history,
      token: token.value,
    })
    typing.value = false

    if (res.code === 2) {
      // OWNER_SECRET 无效：清 token 回登录框
      handleLogout()
      window.alert('OWNER_SECRET 无效，请重新输入')
      return
    }

    const d = res.data
    if (d?.affinity) affinity.value = d.affinity
    if (res.code === 0) {
      messages.value.push({ role: 'assistant', content: d.reply, emotion: d.emotion, sources: d.sources })
    } else {
      messages.value.push({ role: 'assistant', content: '唔…萤宝暂时没法回应', emotion: 'normal' })
    }
  } catch {
    typing.value = false
    messages.value.push({ role: 'assistant', content: '唔…萤宝暂时没法回应', emotion: 'normal' })
  }
  saveHistory()
  scrollBottom()
}

function scrollBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}
</script>

<style scoped>
@reference "../style.css";

.chat-card {
  background: color-mix(in srgb, var(--bg-base) 96%, transparent);
  box-shadow: 0 12px 40px var(--c-glow);
}
.nav-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.7rem;
  height: 1.7rem;
  border-radius: 999px;
  font-size: 0.9rem;
  background: linear-gradient(135deg, color-mix(in srgb, var(--c-primary) 30%, transparent), color-mix(in srgb, var(--c-star) 20%, transparent));
  border: 1px solid var(--c-border);
}
.typing-dot {
  display: inline-block;
  width: 5px;
  height: 5px;
  margin-right: 3px;
  border-radius: 999px;
  background: var(--c-primary-deep);
  animation: typing-bounce 0.9s ease-in-out infinite;
}
@keyframes typing-bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-4px); opacity: 1; }
}
</style>
