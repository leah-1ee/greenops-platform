import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config) => {
    // 개발 환경에서 요청 로깅
    if (import.meta.env.DEV) {
      console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    }
    return config
  },
  (error) => Promise.reject(error),
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status
      const message = error.response?.data?.detail ?? error.message

      if (!error.response) {
        return Promise.reject(new Error('백엔드 서버에 연결할 수 없습니다.'))
      }

      if (status === 404) return Promise.reject(new Error(`리소스를 찾을 수 없습니다: ${message}`))
      if (status === 422) return Promise.reject(new Error(`요청 형식 오류: ${message}`))
      if (status && status >= 500) return Promise.reject(new Error(`서버 오류 (${status}): ${message}`))
    }
    return Promise.reject(error)
  },
)
