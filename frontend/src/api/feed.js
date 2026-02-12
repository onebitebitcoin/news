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

  // 소스 목록
  getSources: async () => {
    const { data } = await client.get('/feed/sources')
    return data
  },

  // 스케줄러 상태 조회
  getSchedulerStatus: async () => {
    const { data } = await client.get('/admin/scheduler-status')
    return data
  },

  // 수집 진행 상황 조회
  getFetchProgress: async () => {
    const { data } = await client.get('/admin/fetch-progress')
    return data
  },

  // 수동 수집 실행
  runFetch: async (hours) => {
    const { data } = await client.post('/admin/fetch/run', null, {
      params: hours ? { hours } : undefined,
    })
    return data
  },

  // URL 미리보기
  previewUrl: async (url) => {
    const { data } = await client.post('/feed/preview', { url })
    return data
  },

  // 수동 기사 추가
  createManual: async ({ url, title, summary, image_url }) => {
    const { data } = await client.post('/feed/manual', { url, title, summary, image_url })
    return data
  },

  // 키워드 기사 검색
  searchArticles: async (query, maxResults = 20) => {
    const { data } = await client.post('/feed/search', { query, max_results: maxResults })
    return data
  },

  // 기사 일괄 추가
  createManualBatch: async (articles) => {
    const { data } = await client.post('/feed/manual/batch', { articles })
    return data
  },
}

export const adminApi = {
  // API 키 목록 조회
  getApiKeys: async () => {
    const { data } = await client.get('/admin/api-keys')
    return data
  },

  // API 키 생성
  createApiKey: async (name) => {
    const { data } = await client.post('/admin/api-keys', { name })
    return data
  },

  // API 키 삭제
  deleteApiKey: async (keyId) => {
    const { data } = await client.delete(`/admin/api-keys/${keyId}`)
    return data
  },
}

export const marketApi = {
  // 시장 데이터 조회
  getData: async () => {
    const { data } = await client.get('/market/data')
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
