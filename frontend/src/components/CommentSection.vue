<template>
  <div class="border-t border-gray-200 pt-6">
    <h3 class="text-lg font-semibold mb-4">评论 ({{ totalCount }})</h3>

    <!-- 发表评论 -->
    <div class="mb-6 p-4 bg-gray-50 rounded-lg">
      <input v-model="nickname" placeholder="昵称（选填）" class="w-full px-3 py-2 border rounded text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-blue-300" />
      <textarea v-model="newComment" placeholder="写评论..." rows="3"
        class="w-full px-3 py-2 border rounded text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-300"></textarea>
      <div class="flex items-center justify-between mt-2">
        <label class="flex items-center gap-1 text-xs text-gray-400 cursor-pointer">
          <input type="checkbox" v-model="isPrivate" class="rounded" /> 仅博主可见
        </label>
        <button @click="submitComment(null)" :disabled="!newComment.trim() || submitting"
          class="px-4 py-1.5 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-40">
          {{ submitting ? '发送中...' : '发表' }}
        </button>
      </div>
      <p v-if="errorMsg" class="text-red-400 text-xs mt-1">{{ errorMsg }}</p>
    </div>

    <!-- 评论列表 -->
    <div v-if="loading" class="text-gray-400 text-sm">加载中...</div>
    <div v-else-if="comments.length === 0" class="text-gray-300 text-sm">暂无评论</div>
    <div v-else class="space-y-3">
      <div v-for="c in comments" :key="c.id">
        <CommentNode :comment="c" :articleId="articleId" @refresh="fetchComments" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
</script>
