const BASE = '/api'

export async function sendMessage({ message, session_id, history = [], session_type = 'guest' }) {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id, history, session_type }),
  })
  return res.json()
}

// 主人模式：带 Bearer OWNER_SECRET，启用好感度 / 记忆 / 人格全链路
export async function sendOwnerMessage({ message, session_id, history = [], token }) {
  const res = await fetch(`${BASE}/chat/owner`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ message, session_id, history }),
  })
  return res.json()
}
