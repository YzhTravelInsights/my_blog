const BASE = '/api'

export async function getComments(articleId) {
  const res = await fetch(`${BASE}/comments?article_id=${articleId}`)
  return res.json()
}

export async function postComment({ article_id, parent_id, nickname, content, is_private }) {
  const res = await fetch(`${BASE}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ article_id, parent_id, nickname, content, is_private }),
  })
  return res.json()
}
