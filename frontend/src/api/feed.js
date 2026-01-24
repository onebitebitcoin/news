import client from './client'

export const feedApi = {
  // 피드 목록 조회
  getList: async ({ page = 1, pageSize = 20, category, source, search } = {}) => {
    const params = new URLSearchParams()
    params.append('page', page)
    params.append('page_size', pageSize)
    if (category) params.append('category', category)
    if (source) params.append('source', source)
    if (search) params.append('search', search)

    const { data } = await client.get(`/feed?${params.toString()}`)
    return data
  },

  // 피드 상세 조회
  getDetail: async (id) => {
    const { data } = await client.get(`/feed/${id}`)
    return data
  },

  // 트렌딩 피드
  getTrending: async (limit = 5) => {
    const { data } = await client.get(`/feed/trending?limit=${limit}`)
    return data
  },

  // 카테고리 목록
  getCategories: async () => {
    const { data } = await client.get('/feed/categories')
    return data
  },
}

export const bookmarkApi = {
  // 북마크 목록
  getList: async () => {
    const { data } = await client.get('/bookmarks')
    return data
  },

  // 북마크 추가
  add: async (itemId) => {
    const { data } = await client.post(`/bookmarks/${itemId}`)
    return data
  },

  // 북마크 삭제
  remove: async (itemId) => {
    const { data } = await client.delete(`/bookmarks/${itemId}`)
    return data
  },
}
