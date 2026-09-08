<!--
  单条评论节点（含回复）。逻辑不变，配色走主题变量。
-->
<template>
  <div class="text-sm">
    <div class="flex items-center gap-2">
      <span class="font-medium text-ink">{{ comment.nickname }}</span>
      <span v-if="comment.is_private" class="text-xs text-lav">[私密]</span>
      <span class="text-xs text-sub/60">{{ comment.created_at }}</span>
    </div>
    <p class="text-sub mt-0.5">{{ comment.content }}</p>
    <button @click="showReply = !showReply" class="text-xs text-sub/70 hover:text-primary-deep mt-1 transition-colors">回复</button>

    <!-- 回复框 -->
    <div v-if="showReply" class="mt-2 ml-4 p-3 rounded-lg border-l-2 border-primary/50 bg-surface">
      <input
        v-model="replyNick"
        placeholder="昵称"
        class="glass-input mb-1 text-xs py-1"
      />
      <textarea
        v-model="replyContent"
        placeholder="写回复..."
        rows="2"
        class="glass-input text-xs py-1 resize-none"
      ></textarea>
      <div class="flex items-center justify-between mt-1">
        <label class="flex items-center gap-1 text-xs text-sub cursor-pointer">
          <input type="checkbox" v-model="replyPrivate" class="rounded accent-[var(--c-primary)]" /> 私密
        </label>
        <button
          @click="doReply"
          :disabled="!replyContent.trim() || replying"
          class="btn-primary px-3 py-1 text-xs"
        >
          {{ replying ? '...' : '回复' }}
        </button>
      </div>
      <p v-if="replyError" class="text-red-400 text-xs mt-1">{{ replyError }}</p>
    </div>

    <!-- 子回复 -->
    <div v-if="comment.replies?.length" class="ml-4 mt-2 space-y-2 border-l-2 border-border-soft pl-3">
      <CommentNode
        v-for="r in comment.replies"
        :key="r.id"
        :comment="r"
        :articleId="articleId"
        @refresh="$emit('refresh')"
      />
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
