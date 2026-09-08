<!--
  萤宝聊天组件。逻辑零改动，仅视觉换主题：
  悬浮气泡 + 玻璃聊天窗 + 萤火绿主色。
-->
<template>
  <!-- 萤宝 3D 角色（始终可见） -->
  <div
    v-if="!chatVisible"
    class="fixed bottom-5 right-5 z-50 flex flex-col items-end"
  >
    <div
      class="w-24 h-24 rounded-full overflow-hidden shadow-glow cursor-pointer
             ring-2 ring-primary/50 ring-offset-2 ring-offset-[var(--bg-base)]
             transition-transform hover:scale-110 active:scale-95"
      @click="openChat"
    >
      <Live2DCharacter :emotion="lastEmotion" size="large" ref="charRef" />
    </div>
  </div>

  <!-- 展开：聊天窗 -->
  <div
    v-else
    class="fixed bottom-5 right-5 w-80 sm:w-96 h-[520px] rounded-2xl shadow-glow-lg flex flex-col z-50 border border-border-soft overflow-hidden"
    :style="{ background: 'color-mix(in srgb, var(--bg-base) 97%, transparent)' }"
  >
    <!-- 3D 模型展示区 -->
    <div
      class="model-viewer w-full h-36 flex items-center justify-center overflow-hidden shrink-0"
      :style="{ background: 'linear-gradient(180deg, color-mix(in srgb, var(--c-primary) 18%, transparent), transparent)' }"
    >
      <Live2DCharacter :emotion="lastEmotion" />
    </div>

    <!-- 头部 -->
    <div
      class="flex items-center justify-between px-4 py-2 shrink-0"
      :style="{ background: 'linear-gradient(135deg, var(--c-primary), var(--c-star))', color: '#0b1f16' }"
    >
      <span class="font-semibold text-sm">✨ 萤宝</span>
      <div class="flex items-center gap-2">
        <button @click="exportChat" title="导出对话" class="opacity-70 hover:opacity-100 text-sm transition-opacity">⬇</button>
        <button @click="close" class="opacity-70 hover:opacity-100 text-lg leading-none transition-opacity">&times;</button>
      </div>
    </div>

    <!-- 消息区 -->
    <div ref="msgContainer" class="flex-1 overflow-y-auto px-3 py-3 space-y-3">
      <div v-if="messages.length === 0" class="text-center text-sub/50 text-sm mt-20">
        萤宝在等你哦～
      </div>
      <ChatBubble
        v-for="(m, i) in messages"
        :key="i"
        :role="m.role"
        :content="m.content"
        :emotion="m.emotion"
      />
      <div v-if="typing" class="text-sub text-xs pl-2">
        <span class="typing-dot" /> <span class="typing-dot" style="animation-delay:0.15s" /> <span class="typing-dot" style="animation-delay:0.3s" />
      </div>
    </div>

    <div class="text-center text-sub/50 text-[10px] py-1 shrink-0">
      对话保存在本地浏览器
    </div>

    <!-- 输入区 -->
    <div class="flex items-center gap-2 px-3 py-2 border-t border-border-soft shrink-0">
      <input
        v-model="input"
        @keyup.enter="send"
        placeholder="和萤宝聊天..."
        ref="inputRef"
        class="glass-input flex-1 py-1.5"
      />
      <button
        @click="send"
        :disabled="!input.trim() || typing"
        class="btn-primary px-3 py-1.5"
      >
        发送
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { sendMessage } from '../api/chat'
import ChatBubble from './ChatBubble.vue'
import Live2DCharacter from './Live2DCharacter.vue'

const chatVisible = ref(false)
const input = ref('')
const typing = ref(false)
const messages = ref([])
const msgContainer = ref(null)
const inputRef = ref(null)
const charRef = ref(null)

const SESSION_KEY = 'blog_chat_session'
const MSG_KEY = 'blog_chat_messages'

const lastEmotion = computed(() => {
  const last = messages.value.filter((m) => m.role === 'assistant').at(-1)
  return last?.emotion || 'normal'
})

// ---------- 问候语 ----------
const GREETINGS = [
  '你好呀，开拓者～',
  '嘿！萤宝在这里哦！',
  '嘿嘿，你来啦～',
  '开拓者今天过得怎么样？',
  '萤宝等你很久了呢～',
  '哇，是开拓者！',
]

function randomGreeting() {
  return GREETINGS[Math.floor(Math.random() * GREETINGS.length)]
}

// ---------- 本地存储 ----------
function loadHistory() {
  try {
    const saved = localStorage.getItem(MSG_KEY)
    if (saved) messages.value = JSON.parse(saved)
  } catch {}
}

function saveHistory() {
  try {
    localStorage.setItem(MSG_KEY, JSON.stringify(messages.value))
  } catch {}
}

function getSessionId() {
  let sid = localStorage.getItem(SESSION_KEY)
  if (!sid) {
    sid = 'session_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8)
    localStorage.setItem(SESSION_KEY, sid)
  }
  return sid
}

// ---------- 打开聊天 ----------
async function openChat() {
  chatVisible.value = true
  loadHistory()

  // 首次打开：自动发问候
  if (messages.value.length === 0) {
    await autoGreet()
  }

  await nextTick()
  scrollBottom()
  inputRef.value?.focus()
}

async function autoGreet() {
  typing.value = true
  try {
    const res = await sendMessage({
      message: '萤宝你好',
      session_id: getSessionId(),
      history: [],
      session_type: 'guest',
    })
    if (res.code === 0) {
      const d = res.data
      messages.value.push({ role: 'assistant', content: d.reply, emotion: d.emotion, sources: d.sources })
    } else {
      messages.value.push({ role: 'assistant', content: randomGreeting(), emotion: 'happy' })
    }
  } catch {
    messages.value.push({ role: 'assistant', content: randomGreeting(), emotion: 'happy' })
  }
  typing.value = false
  saveHistory()
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

  try {
    const res = await sendMessage({
      message: text,
      session_id: getSessionId(),
      history: messages.value.slice(-20).map((m) => ({ role: m.role, content: m.content })),
      session_type: 'guest',
    })
    typing.value = false
    if (res.code === 0) {
      const d = res.data
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

function exportChat() {
  const blob = new Blob([JSON.stringify(messages.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'chat_history.json'; a.click()
  URL.revokeObjectURL(url)
}

function scrollBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}

function close() {
  chatVisible.value = false
}
</script>

<style scoped>
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
