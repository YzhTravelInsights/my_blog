<template>
  <div class="text-sm">
    <div class="flex items-center gap-2">
      <span class="font-medium text-gray-700">{{ comment.nickname }}</span>
      <span v-if="comment.is_private" class="text-xs text-orange-400">[私密]</span>
      <span class="text-xs text-gray-300">{{ comment.created_at }}</span>
    </div>
    <p class="text-gray-600 mt-0.5">{{ comment.content }}</p>
    <button @click="showReply = !showReply" class="text-xs text-gray-400 hover:text-blue-500 mt-1">回复</button>

    <!-- 回复框 -->
    <div v-if="showReply" class="mt-2 ml-4 p-3 bg-gray-50 rounded border-l-2 border-blue-200">
      <input v-model="replyNick" placeholder="昵称" class="w-full mb-1 px-2 py-1 border rounded text-xs focus:outline-none" />
      <textarea v-model="replyContent" placeholder="写回复..." rows="2" class="w-full px-2 py-1 border rounded text-xs resize-none focus:outline-none"></textarea>
      <div class="flex items-center justify-between mt-1">
        <label class="flex items-center gap-1 text-xs text-gray-400 cursor-pointer">
          <input type="checkbox" v-model="replyPrivate" class="rounded" /> 私密
        </label>
        <button @click="doReply" :disabled="!replyContent.trim() || replying"
          class="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 disabled:opacity-40">
          {{ replying ? '...' : '回复' }}
        </button>
      </div>
      <p v-if="replyError" class="text-red-400 text-xs mt-1">{{ replyError }}</p>
    </div>

    <!-- 子回复 -->
    <div v-if="comment.replies?.length" class="ml-4 mt-2 space-y-2 border-l-2 border-gray-100 pl-3">
      <CommentNode v-for="r in comment.replies" :key="r.id" :comment="r" :articleId="articleId" @refresh="$emit('refresh')" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { postComment } from '../api/comments'

const props = defineProps({ comment: Object, articleId: String })
const emit = defineEmits(['refresh'])

const showReply = ref(false)
const replyNick = ref('')
const replyContent = ref('')
const replyPrivate = ref(false)
const replying = ref(false)
const replyError = ref('')

async function doReply() {
  if (!replyContent.value.trim()) return
  replying.value = true
  replyError.value = ''
  const res = await postComment({
    article_id: props.articleId,
    parent_id: props.comment.id,
    nickname: replyNick.value.trim() || '匿名',
    content: replyContent.value.trim(),
    is_private: replyPrivate.value,
  })
  if (res.code === 0) {
    replyContent.value = ''
    showReply.value = false
    emit('refresh')
  } else {
    replyError.value = res.msg || '发送失败'
  }
  replying.value = false
}
</script>
