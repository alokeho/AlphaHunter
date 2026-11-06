/**
 * Axios 客户端。
 *
 * 约定：
 * - 所有请求基础路径为 /api/v1，由 Vite 开发代理或 Nginx 转发到 FastAPI；
 * - 响应拦截器直接返回 response.data，业务代码无需重复解包；
 * - 错误信息优先读取后端统一错误结构 { code, message, details }。
 */
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    Accept: 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error),
)

/**
 * 把 Axios 异常转换成适合直接展示给用户的中文提示。
 * @param {unknown} error
 * @returns {string}
 */
export function getApiErrorMessage(error) {
  if (axios.isAxiosError(error)) {
    const responseData = error.response?.data
    if (responseData && typeof responseData === 'object' && responseData.message) {
      return String(responseData.message)
    }
    if (error.code === 'ECONNABORTED') {
      return '请求超时，请确认后端服务与网络状态。'
    }
    if (!error.response) {
      return '无法连接后端服务，请确认 FastAPI 已启动在 8000 端口。'
    }
    return `请求失败（HTTP ${error.response.status}），请稍后重试。`
  }

  if (error instanceof Error) {
    return error.message
  }
  return '发生未知错误，请稍后重试。'
}

export default apiClient
