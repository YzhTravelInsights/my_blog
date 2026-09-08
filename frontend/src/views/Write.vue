<!--
  主人发布文章页（/write）— 仅博主可用
  携 ?owner_token= 访问自动登录，或输入 OWNER_SECRET 后编辑并发布 markdown 文章。
  发布走 /api/admin/article：写 md 文件 → 立即入知识库，访客端即可看到。
  访客无入口（侧栏按钮已隐藏），评论等原有功能不受影响。
-->
<template>
  <div class="flex justify-center px-2">
    <!-- 未登录 -->
    <div v-if="!token" class="w-full max-w-md mt-10 glass-card p-6">
      <h2 class="text-lg font-bold text-ink flex items-center gap-2">
        <span class="nav-logo">✍️</span> 发布文章
      </h2>
      <p class="text-xs text-sub mt-1.5 leading-relaxed">
        输入 <code class="text-primary-deep">OWNER_SECRET</code> 验证身份（仅博主可用），
        或访问时携带 <code class="text-primary-deep">?owner_token=OWNER_SECRET</code> 自动登录。
      </p>
      <input
        v-model="secretInput"
        type="password"
        class="glass-input w-full mt-4 py-2"
        placeholder="OWNER_SECRET"
        @keyup.enter="login"
      />
      <button class="btn-primary w-full mt-3 py-2" :disabled="!secretInput.trim()" @click="login">
        进入编辑器
      </button>
    </div>

    <!-- 已登录：编辑器 -->
    <div v-else class="w-full max-w-2xl mt-4 space-y-4">
      <div class="glass-card p-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="nav-logo">✍️</span>
          <span class="font-bold text-ink">发布文章</span>
        </div>
        <button class="btn-ghost px-3 py-1 text-xs" @click="handleLogout">退出</button>
      </div>

      <div class="glass-card p-4 space-y-3">
        <div>
          <label class="text-xs text-sub block mb-1">标题 *</label>
          <input
            v-model="form.title"
            class="glass-input w-full py-2"
            placeholder="文章标题"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-sub block mb-1">分类</label>
            <input
              v-model="form.category"
              class="glass-input w-full py-2"
              list="write-categories"
              placeholder="未分类"
            />
            <datalist id="write-categories">
              <option v-for="c in categories" :key="c" :value="c" />
            </datalist>
          </div>
          <div>
            <label class="text-xs text-sub block mb-1">标签（英文逗号分隔）</label>
            <input
              v-model="form.tagsText"
              class="glass-input w-full py-2"
              placeholder="vue, 随笔"
            />
          </div>
        </div>

        <div>
          <label class="text-xs text-sub block mb-1">正文 Markdown *</label>
          <textarea
            v-model="form.content"
            rows="14"
            class="glass-input w-full py-2 font-mono text-xs leading-relaxed"
            placeholder="支持 Markdown…&#10;&#10;## 小标题&#10;正文内容"
          />
        </div>

        <button
          class="btn-primary w-full py-2"
          :disabled="!form.title.trim() || !form.content.trim() || publishing"
          @click="publish"
        >
          {{ publishing ? '发布中…' : '发布文章' }}
        </button>

        <p
          v-if="msg"
          class="text-xs text-center break-all"
          :style="{ color: msgError ? '#e06666' : 'var(--c-primary-deep)' }"
        >
          {{ msg }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { publishArticle } from '../api/admin'
import { getArticles } from '../api/articles'
import { useOwner } from '../store/owner'

const { token, setToken, logout } = useOwner()
const secretInput = ref('')
const publishing = ref(false)
const msg = ref('')
const msgError = ref(false)
const categories = ref([])

const form = ref({
  title: '',
  category: '',
  tagsText: '',
  content: '',
})

onMounted(async () => {
  // 拉一次现有分类做联想提示（仅主人编辑器用，失败静默）
  try {
    const res = await getArticles({ page: 1 })
    const filters = res.data?.filters
    if (filters?.categories) categories.value = filters.categories
  } catch {
    /* 后端未启动等场景静默 */
  }
})

async function login() {
  const s = secretInput.value.trim()
  if (!s) return
  setToken(s)
  secretInput.value = ''
}

function handleLogout() {
  logout()
  form.value = { title: '', category: '', tagsText: '', content: '' }
  msg.value = ''
}

async function publish() {
  const title = form.value.title.trim()
  const content = form.value.content.trim()
  if (!title || !content || publishing.value) return

  publishing.value = true
  msg.value = ''
  msgError.value = false
  try {
    const tags = form.value.tagsText
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)

    const res = await publishArticle({
      title,
      category: form.value.category.trim(),
      tags,
      content,
      token: token.value,
    })

    if (res.code === 2) {
      // OWNER_SECRET 无效：清 token 回登录框
      handleLogout()
      window.alert('OWNER_SECRET 无效，请重新输入')
      return
    }

    if (res.code === 0) {
      const id = res.data.id
      msgError.value = false
      msg.value = `✅ 发布成功：${res.data.title} → 查看 #/article/${id}`
      form.value = { title: '', category: '', tagsText: '', content: '' }
    } else {
      msgError.value = true
      msg.value = res.msg || '发布失败'
    }
  } catch {
    msgError.value = true
    msg.value = '无法连接后端，请确认后端已启动'
  } finally {
    publishing.value = false
  }
}
</script>

<style scoped>
@reference "../style.css";

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
</style>
