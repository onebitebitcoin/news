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
  (response) => response,
  (error) => {
    console.error('[API Error]', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.message,
    })
    return Promise.reject(error)
  }
)

export default client
