<template>
  <!-- 默认折叠：圆形图标 -->
  <div v-if="!isOpen" @click="open" class="fixed bottom-5 right-5 w-14 h-14 bg-blue-500 hover:bg-blue-600 rounded-full flex items-center justify-center shadow-lg cursor-pointer transition-all hover:scale-110 z-50" title="和萤宝聊天">
    <span class="text-2xl">🔆</span>
  </div>

  <!-- 展开：聊天窗 -->
  <div v-else class="fixed bottom-5 right-5 w-80 sm:w-96 h-[500px] bg-white rounded-xl shadow-2xl flex flex-col z-50 border border-gray-200 overflow-hidden">
    <!-- 头部 -->
    <div class="flex items-center justify-between px-4 py-3 bg-blue-500 text-white">
      <div class="flex items-center gap-2">
        <Live2DCharacter :emotion="lastEmotion" class="scale-50 -my-6" />
        <span class="font-semibold text-sm">萤宝</span>
      </div>
      <div class="flex items-center gap-2">
        <button @click="exportChat" title="导出对话" class="text-white/80 hover:text-white text-xs">⬇</button>
        <button @click="close" class="text-white/80 hover:text-white text-lg leading-none">&times;</button>
      </div>
    </div>

    <!-- 消息区 -->
    <div ref="msgContainer" class="flex-1 overflow-y-auto px-3 py-3 space-y-3 bg-gray-50">
      <div v-if="messages.length === 0" class="text-center text-gray-300 text-sm mt-20">
        萤宝在等你哦～
      </div>
      <ChatBubble v-for="(m, i) in messages" :key="i" :role="m.role" :content="m.content" :emotion="m.emotion" />
      <div v-if="typing" class="text-gray-400 text-xs pl-2">萤宝思考中...</div>
    </div>

    <!-- 提示 -->
    <div class="text-center text-gray-300 text-[10px] py-1 bg-gray-50">
      对话记录保存在本地浏览器中，清除缓存会丢失
    </div>

    <!-- 输入区 -->
    <div class="flex items-center gap-2 px-3 py-2 border-t border-gray-200 bg-white">
      <input v-model="input" @keyup.enter="send" placeholder="和萤宝聊天..."
        class="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300" />
      <button @click="send" :disabled="!input.trim() || typing"
        class="px-3 py-1.5 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 disabled:opacity-40 transition-colors">
        发送
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { sendMessage } from '../api/chat'
import ChatBubble from './ChatBubble.vue'
import Live2DCharacter from './Live2DCharacter.vue'

const isOpen = ref(false)
const input = ref('')
const typing = ref(false)
const messages = ref([])
const msgContainer = ref(null)

const SESSION_KEY = 'blog_chat_session'
const MSG_KEY = 'blog_chat_messages'

const lastEmotion = computed(() => {
  const last = messages.value.filter(m => m.role === 'assistant').at(-1)
  return last?.emotion || 'normal'
})

// 从 localStorage 恢复
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

async function send() {
  const text = input.value.trim()
  if (!text || typing.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  saveHistory()
  typing.value = true
  scrollBottom()

  const res = await sendMessage({
    message: text,
    session_id: getSessionId(),
    history: messages.value.slice(-20).map(m => ({ role: m.role, content: m.content })),
    session_type: 'guest',
  })

  typing.value = false
  if (res.code === 0) {
    const d = res.data
    messages.value.push({ role: 'assistant', content: d.reply, emotion: d.emotion, sources: d.sources })
  } else {
    messages.value.push({ role: 'assistant', content: '唔…萤宝暂时没法回应，稍后再试试吧', emotion: 'normal' })
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

function open() {
  isOpen.value = true
  loadHistory()
  scrollBottom()
}

function close() {
  isOpen.value = false
}
</script>
