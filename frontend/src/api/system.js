/**
 * 系统监控与仪表盘 API。
 * 所有函数返回 Promise，响应体已经由客户端拦截器解包。
 */
import apiClient from './client'

export function getHealth() {
  return apiClient.get('/health')
}

export function getSystemInfo() {
  return apiClient.get('/system/info')
}

export function getDashboardSummary() {
  return apiClient.get('/dashboard/summary')
}
