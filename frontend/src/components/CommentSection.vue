<!--
  评论区：玻璃表单 + 主题配色。逻辑不变。
-->
<template>
  <div class="glass-card p-6">
    <h3 class="text-lg font-semibold text-ink mb-4">评论 ({{ totalCount }})</h3>

    <!-- 发表评论 -->
    <div class="mb-6 p-4 rounded-xl border border-border-soft bg-surface">
      <input
        v-model="nickname"
        placeholder="昵称（选填）"
        class="glass-input mb-2"
      />
      <textarea
        v-model="newComment"
        placeholder="写评论..."
        rows="3"
        class="glass-input resize-none"
      ></textarea>
      <div class="flex items-center justify-between mt-2">
        <label class="flex items-center gap-1 text-xs text-sub cursor-pointer">
          <input type="checkbox" v-model="isPrivate" class="rounded accent-[var(--c-primary)]" /> 仅博主可见
        </label>
        <button
          @click="submitComment(null)"
          :disabled="!newComment.trim() || submitting"
          class="btn-primary"
        >
          {{ submitting ? '发送中...' : '发表' }}
        </button>
      </div>
      <p v-if="errorMsg" class="text-red-400 text-xs mt-1">{{ errorMsg }}</p>
    </div>

    <!-- 评论列表 -->
    <div v-if="loading" class="text-sub text-sm">加载中...</div>
    <div v-else-if="comments.length === 0" class="text-sub/60 text-sm">暂无评论</div>
    <div v-else class="space-y-3">
      <div v-for="c in comments" :key="c.id">
        <CommentNode :comment="c" :articleId="articleId" @refresh="fetchComments" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getComments, postComment } from '../api/comments'
import CommentNode from './CommentNode.vue'

const props = defineProps({ articleId: String })

const comments = ref([])
const totalCount = ref(0)
const loading = ref(true)
const nickname = ref('')
const newComment = ref('')
const isPrivate = ref(false)
const submitting = ref(false)
const errorMsg = ref('')

async function fetchComments() {
  const res = await getComments(props.articleId)
  if (res.code === 0) {
    comments.value = res.data.comments
    totalCount.value = res.data.count
  }
  loading.value = false
}

async function submitComment(parentId) {
  if (!newComment.value.trim()) return
  submitting.value = true
  errorMsg.value = ''
  const res = await postComment({
    article_id: props.articleId,
    parent_id: parentId,
    nickname: nickname.value.trim() || '匿名',
    content: newComment.value.trim(),
    is_private: isPrivate.value,
  })
  if (res.code === 0) {
    newComment.value = ''
    isPrivate.value = false
    await fetchComments()
  } else {
    errorMsg.value = res.msg || '发送失败'
  }
  submitting.value = false
}

onMounted(fetchComments)

// 上下篇切换文章后，重新拉取该文章的评论并清空表单
watch(
  () => props.articleId,
  () => {
    comments.value = []
    totalCount.value = 0
    loading.value = true
    nickname.value = ''
    newComment.value = ''
    errorMsg.value = ''
    fetchComments()
  },
)
</script>
