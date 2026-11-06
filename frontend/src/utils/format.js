/**
 * 展示层格式化工具。
 * 纯函数便于在多个页面复用与后续单元测试。
 */

export const EXCHANGE_LABELS = {
  SSE: '上交所',
  SZSE: '深交所',
  BSE: '北交所',
}

export const EXCHANGE_FULL_LABELS = {
  SSE: '上海证券交易所',
  SZSE: '深圳证券交易所',
  BSE: '北京证券交易所',
}

export const DATA_STATUS_MAP = {
  empty: { label: '待初始化', type: 'info' },
  demo: { label: '演示数据', type: 'warning' },
  ready: { label: '行情就绪', type: 'success' },
}

/**
 * 格式化日期字符串。
 * 对 YYYY-MM-DD 直接截取，避免时区转换导致日期偏移。
 * @param {string | null | undefined} value
 */
export function formatDate(value) {
  if (!value) return '—'
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date)
}

/**
 * 格式化日期时间。
 * @param {string | null | undefined} value
 */
export function formatDateTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(date)
}

/**
 * 把秒数转为易读的运行时长。
 * @param {number} seconds
 */
export function formatUptime(seconds) {
  const total = Math.max(Number(seconds) || 0, 0)
  const days = Math.floor(total / 86400)
  const hours = Math.floor((total % 86400) / 3600)
  const minutes = Math.floor((total % 3600) / 60)

  if (days > 0) return `${days} 天 ${hours} 小时`
  if (hours > 0) return `${hours} 小时 ${minutes} 分钟`
  if (minutes > 0) return `${minutes} 分钟`
  return `${Math.floor(total)} 秒`
}

/**
 * 千分位数字格式化。
 * @param {number | null | undefined} value
 */
export function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—'
  return new Intl.NumberFormat('zh-CN').format(Number(value))
}

/**
 * 交易所短名称。
 * @param {string} exchange
 */
export function exchangeLabel(exchange) {
  return EXCHANGE_LABELS[exchange] || exchange || '—'
}
