/**
 * 股票池 API。
 */
import apiClient from './client'

/**
 * 分页查询股票。
 * @param {{ page?: number, page_size?: number, keyword?: string, exchange?: string }} params
 */
export function getStocks(params = {}) {
  return apiClient.get('/stocks', { params })
}

/**
 * 获取交易所与行业筛选项。
 */
export function getStockFilters() {
  return apiClient.get('/stocks/filters')
}

/**
 * 查询单只股票详情。
 * @param {string} symbol 6 位证券代码
 */
export function getStockDetail(symbol) {
  return apiClient.get(`/stocks/${symbol}`)
}
