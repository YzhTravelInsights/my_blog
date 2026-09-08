const BASE = '/api'

// 管理后台汇总：后台数据 + 系统运行信息（需 Bearer OWNER_SECRET）
export async function getAdminSummary(token) {
  const res = await fetch(`${BASE}/admin/summary`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.json()
}

// 主人发布文章：{title, category, tags, content} → 写 md 并立即入知识库（需 Bearer OWNER_SECRET）
export async function publishArticle({ title, category, tags, content, token }) {
  const res = await fetch(`${BASE}/admin/article`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ title, category, tags, content }),
  })
  return res.json()
}

// 主人删除文章：删 md 文件 + 清 RAG 索引 + 删该文章评论（需 Bearer OWNER_SECRET）
export async function deleteArticle(id, token) {
  const res = await fetch(`${BASE}/admin/article/${encodeURIComponent(id)}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.json()
}

// 主人删除单条评论（含回复，需 Bearer OWNER_SECRET）
export async function deleteComment(id, token) {
  const res = await fetch(`${BASE}/admin/comment/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.json()
}
