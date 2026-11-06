/**
 * 系统健康状态 Pinia Store。
 *
 * 用途：
 * - 顶栏展示后端在线状态；
 * - 多个页面共享最近一次健康检查结果，避免重复请求；
 * - 统一处理检测失败，不向用户弹出重复错误提示。
 */
import { defineStore } from 'pinia'

import { getHealth } from '@/api/system'
import { getApiErrorMessage } from '@/api/client'

export const useSystemStore = defineStore('system', {
  state: () => ({
    /** @type {null | Record<string, unknown>} 最近一次健康检查响应 */
    health: null,
    /** 是否正在进行健康检查 */
    checking: false,
    /** 最近一次错误文案 */
    error: '',
    /** 最近一次检查时间（本地时间字符串） */
    lastChecked: '',
  }),

  getters: {
    /** 后端是否在线 */
    isOnline: (state) => state.health?.status === 'ok',
    /** 顶栏状态文案 */
    statusLabel: (state) => {
      if (state.checking) return '检测中'
      if (state.isOnline) return '服务在线'
      return '服务离线'
    },
    /** API 版本 */
    apiVersion: (state) => state.health?.version || '—',
  },

  actions: {
    /**
     * 主动检查后端健康状态。
     * 为避免初始加载时反复弹窗，错误只保存在 store 中由页面自行展示。
     */
    async checkHealth() {
      this.checking = true
      this.error = ''
      try {
        this.health = await getHealth()
      } catch (error) {
        this.health = null
        this.error = getApiErrorMessage(error)
      } finally {
        this.checking = false
        this.lastChecked = new Date().toLocaleTimeString('zh-CN', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
        })
      }
    },
  },
})
