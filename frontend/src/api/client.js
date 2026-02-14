import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request 인터셉터 - trailing slash 제거
client.interceptors.request.use((config) => {
  if (config.url && config.url.endsWith('/')) {
    config.url = config.url.slice(0, -1)
  }
  return config
})

// Response 인터셉터 - 에러 로깅
client.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload && typeof payload === 'object' && 'success' in payload) {
      if (payload.success) {
        return { ...response, data: payload.data }
      }

      const apiError = new Error(payload?.error?.message || '요청 처리 중 오류가 발생했습니다')
      apiError.response = { ...response, data: payload }
      throw apiError
    }

    return response
  },
  (error) => {
    console.error('[API Error]', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.message,
    })
    return Promise.reject(error)
  }
)

/**
 * Axios 에러에서 구조화된 에러 정보를 추출한다.
 * @returns {{ message: string, status: number|null, detail: string|null, type: string|null }}
 */
export function extractApiError(err) {
  // 서버 응답이 있는 경우
  if (err.response) {
    const { status, data } = err.response
    const detail = data?.detail

    if (typeof data?.success === 'boolean' && data.success === false) {
      return {
        message: data?.error?.message || `서버 오류 (${status})`,
        status,
        detail: data?.error?.details || null,
        type: data?.error?.code || null,
      }
    }

    // 백엔드가 구조화된 detail 객체를 반환한 경우
    if (detail && typeof detail === 'object') {
      return {
        message: detail.message || `서버 오류 (${status})`,
        status,
        detail: detail.error || null,
        type: detail.type || null,
      }
    }

    // detail이 문자열인 경우
    if (typeof detail === 'string') {
      return {
        message: detail,
        status,
        detail: null,
        type: null,
      }
    }

    return {
      message: `서버 오류 (${status})`,
      status,
      detail: null,
      type: null,
    }
  }

  // 서버 응답 없음 (네트워크 에러)
  if (err.request) {
    return {
      message: '서버에 연결할 수 없습니다',
      status: null,
      detail: err.message || null,
      type: 'NetworkError',
    }
  }

  // 기타 에러
  return {
    message: err.message || '알 수 없는 오류가 발생했습니다',
    status: null,
    detail: null,
    type: null,
  }
}

export default client
