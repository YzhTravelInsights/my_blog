const BASE = '/api'

export async function getArticles({ page = 1, category = '', tag = '', search = '' } = {}) {
  const params = new URLSearchParams({ page, page_size: 10 })
  if (category) params.set('category', category)
  if (tag) params.set('tag', tag)
  if (search) params.set('search', search)
  const res = await fetch(`${BASE}/articles?${params}`)
  return res.json()
}

export async function getArticle(id) {
  const res = await fetch(`${BASE}/articles/${id}`)
  return res.json()
}

export async function getAbout() {
  const res = await fetch(`${BASE}/about`)
  return res.json()
}
