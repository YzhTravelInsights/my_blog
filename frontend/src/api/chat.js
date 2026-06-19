const BASE = '/api'

export async function sendMessage({ message, session_id, history = [], session_type = 'guest' }) {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id, history, session_type }),
  })
  return res.json()
}
