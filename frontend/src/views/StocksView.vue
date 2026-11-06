<script setup>
/**
 * 股票池页面。
 *
 * 功能：
 * - 分页查询股票静态资料；
 * - 按代码/名称/行业关键词与交易所筛选；
 * - 点击行或“详情”按钮打开侧边详情抽屉；
 * - 所有数据来自 FastAPI，不包含本地硬编码股票。
 */
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'

import { getApiErrorMessage } from '@/api/client'
import { getStockDetail, getStockFilters, getStocks } from '@/api/stocks'
import { exchangeLabel, EXCHANGE_FULL_LABELS, formatDate } from '@/utils/format'

const stocks = ref([])
const total = ref(0)
const pages = ref(0)
const loading = ref(false)
const error = ref('')

const filters = reactive({
  exchanges: [],
  industries: [],
})

const query = reactive({
  page: 1,
  page_size: 10,
  keyword: '',
  exchange: '',
})

const drawerVisible = ref(false)
const detailLoading = ref(false)
const selectedStock = ref(null)

const industryCount = computed(() => filters.industries.length)
const exchangeCount = computed(() => filters.exchanges.length)

async function loadStocks() {
  loading.value = true
  error.value = ''
  try {
    const data = await getStocks({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword.trim() || undefined,
      exchange: query.exchange || undefined,
    })
    stocks.value = data.items
    total.value = data.total
    pages.value = data.pages
  } catch (requestError) {
    error.value = getApiErrorMessage(requestError)
    stocks.value = []
    total.value = 0
    pages.value = 0
  } finally {
    loading.value = false
  }
}

async function loadFilters() {
  try {
    const data = await getStockFilters()
    filters.exchanges = data.exchanges
    filters.industries = data.industries
  } catch (requestError) {
    ElMessage.error(getApiErrorMessage(requestError))
  }
}

function applyFilters() {
  query.page = 1
  loadStocks()
}

function resetFilters() {
  query.keyword = ''
  query.exchange = ''
  query.page = 1
  loadStocks()
}

function handlePageChange(page) {
  query.page = page
  loadStocks()
}

function handleSizeChange(size) {
  query.page_size = size
  query.page = 1
  loadStocks()
}

/**
 * 打开详情抽屉。列表已有基础信息，先用列表数据即时渲染，
 * 再请求详情接口补全字段，避免抽屉空白。
 */
async function openDetail(row) {
  selectedStock.value = row
  drawerVisible.value = true
  detailLoading.value = true
  try {
    selectedStock.value = await getStockDetail(row.symbol)
  } catch (requestError) {
    ElMessage.error(getApiErrorMessage(requestError))
  } finally {
    detailLoading.value = false
  }
}

function marketTagType(market) {
  if (market === '科创板') return 'primary'
  if (market === '创业板') return 'success'
  if (market === '北交所') return 'warning'
  return 'info'
}

function dataSourceTagType(source) {
  return source === 'demo' ? 'warning' : 'success'
}

function dataSourceLabel(source) {
  if (source === 'demo') return '演示数据'
  if (source === 'akshare') return 'AKShare'
  return source || '未知'
}

onMounted(async () => {
  await Promise.all([loadStocks(), loadFilters()])
})
</script>

<template>
  <div class="page-stack stocks-page">
    <!-- 股票池摘要 -->
    <section class="surface-card pool-hero">
      <div class="pool-hero__copy">
        <div class="eyebrow">
          <span class="pool-dot" />
          A-SHARE UNIVERSE
        </div>
        <h2>核心股票池</h2>
        <p>
          第一阶段收录跨市场代表性标的，用于验证筛选、分页与详情链路。
          真实全市场股票将在接入 AKShare 同步任务后写入。
        </p>
      </div>

      <div class="pool-metrics">
        <div class="pool-metric">
          <span>股票总数</span>
          <strong class="mono">{{ total }}</strong>
          <small>只</small>
        </div>
        <div class="pool-metric">
          <span>交易所</span>
          <strong class="mono">{{ exchangeCount }}</strong>
          <small>个</small>
        </div>
        <div class="pool-metric">
          <span>行业覆盖</span>
          <strong class="mono">{{ industryCount }}</strong>
          <small>类</small>
        </div>
      </div>
    </section>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="page-alert"
    />

    <!-- 筛选栏 -->
    <section class="surface-card filter-bar">
      <div class="filter-controls">
        <el-input
          v-model="query.keyword"
          class="keyword-input"
          placeholder="搜索代码、名称或行业，如 600519 / 茅台"
          :prefix-icon="Search"
          clearable
          @keyup.enter="applyFilters"
          @clear="applyFilters"
        />

        <el-select
          v-model="query.exchange"
          class="exchange-select"
          placeholder="全部交易所"
          clearable
          @change="applyFilters"
        >
          <el-option
            v-for="item in filters.exchanges"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>

        <el-button type="primary" @click="applyFilters">筛选</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>

      <div class="filter-note">
        <span class="filter-note__dot" />
        静态资料 · 只读查询
      </div>
    </section>

    <!-- 股票表格 -->
    <section v-loading="loading" class="surface-card table-card">
      <div class="section-heading table-heading">
        <div>
          <h2>股票清单</h2>
          <p>
            当前筛选命中 <strong>{{ total }}</strong> 条记录，共 {{ pages }} 页。
          </p>
        </div>
        <el-button text :loading="loading" @click="loadStocks">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-table
        :data="stocks"
        size="default"
        class="stock-table"
        row-key="symbol"
        @row-click="openDetail"
      >
        <el-table-column prop="symbol" label="证券代码" width="112">
          <template #default="{ row }">
            <span class="code-chip">{{ row.symbol }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="证券简称" min-width="120">
          <template #default="{ row }">
            <div class="name-cell">
              <span class="name-avatar">{{ row.name?.slice(0, 1) }}</span>
              <strong>{{ row.name }}</strong>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="exchange" label="交易所" width="110">
          <template #default="{ row }">
            {{ exchangeLabel(row.exchange) }}
          </template>
        </el-table-column>

        <el-table-column prop="market" label="板块" width="100">
          <template #default="{ row }">
            <el-tag :type="marketTagType(row.market)" size="small" effect="plain">
              {{ row.market }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="industry" label="行业" min-width="110">
          <template #default="{ row }">{{ row.industry || '—' }}</template>
        </el-table-column>

        <el-table-column prop="list_date" label="上市日期" width="120">
          <template #default="{ row }">
            <span class="mono">{{ formatDate(row.list_date) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="data_source" label="数据来源" width="108">
          <template #default="{ row }">
            <el-tag :type="dataSourceTagType(row.data_source)" size="small">
              {{ dataSourceLabel(row.data_source) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="86" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click.stop="openDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <strong>没有匹配的股票</strong>
            <p>尝试更换关键词或清空交易所筛选条件。</p>
            <el-button size="small" @click="resetFilters">重置筛选</el-button>
          </div>
        </template>
      </el-table>

      <div class="pagination-row">
        <span>第 {{ query.page }} / {{ pages || 1 }} 页</span>
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="sizes, prev, pager, next"
          background
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </section>

    <!-- 详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="股票详情" size="420px">
      <div v-loading="detailLoading" class="detail-panel">
        <div class="detail-head">
          <div class="detail-symbol mono">{{ selectedStock?.symbol }}</div>
          <div>
            <h2>{{ selectedStock?.name }}</h2>
            <p>
              {{ EXCHANGE_FULL_LABELS[selectedStock?.exchange] || selectedStock?.exchange }}
              · {{ selectedStock?.market }}
            </p>
          </div>
        </div>

        <div class="detail-tags">
          <el-tag :type="marketTagType(selectedStock?.market)" effect="plain">
            {{ selectedStock?.market }}
          </el-tag>
          <el-tag :type="dataSourceTagType(selectedStock?.data_source)">
            {{ dataSourceLabel(selectedStock?.data_source) }}
          </el-tag>
          <el-tag :type="selectedStock?.is_active ? 'success' : 'info'" effect="plain">
            {{ selectedStock?.is_active ? '正常上市' : '已停牌/退市' }}
          </el-tag>
        </div>

        <el-descriptions :column="1" border class="detail-descriptions">
          <el-descriptions-item label="证券代码">
            {{ selectedStock?.symbol }}
          </el-descriptions-item>
          <el-descriptions-item label="证券简称">
            {{ selectedStock?.name }}
          </el-descriptions-item>
          <el-descriptions-item label="交易所">
            {{ EXCHANGE_FULL_LABELS[selectedStock?.exchange] || selectedStock?.exchange }}
          </el-descriptions-item>
          <el-descriptions-item label="板块">
            {{ selectedStock?.market }}
          </el-descriptions-item>
          <el-descriptions-item label="所属行业">
            {{ selectedStock?.industry || '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="上市日期">
            {{ formatDate(selectedStock?.list_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="数据来源">
            {{ dataSourceLabel(selectedStock?.data_source) }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-note">
          <strong>备注</strong>
          <p>{{ selectedStock?.description || '暂无备注信息。' }}</p>
        </div>

        <el-alert
          type="warning"
          :closable="false"
          show-icon
          title="阶段一不提供实时行情与交易信号"
          description="当前仅展示股票静态资料，请勿据此作出投资决策。"
        />
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
.stocks-page {
  gap: 15px;
}

.page-alert {
  border-radius: var(--ah-radius);
}

/* ---------------- 摘要 ---------------- */
.pool-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 26px;
  padding: 24px 26px;
  background:
    radial-gradient(circle at 96% 0%, rgb(37 99 235 / 7%), transparent 36%),
    #fff;
}

.pool-hero__copy {
  max-width: 630px;
}

.pool-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ah-blue);
  box-shadow: 0 0 0 4px rgb(37 99 235 / 9%);
}

.pool-hero h2 {
  margin: 8px 0 6px;
  font-size: 22px;
  font-weight: 750;
  letter-spacing: -0.035em;
}

.pool-hero p {
  margin: 0;
  color: var(--ah-text-soft);
  font-size: 12px;
  line-height: 1.8;
}

.pool-metrics {
  display: flex;
  flex: 0 0 auto;
  gap: 10px;
}

.pool-metric {
  min-width: 89px;
  padding: 12px 14px;
  border: 1px solid #e9eef5;
  border-radius: 11px;
  background: #f8fafd;
}

.pool-metric span {
  display: block;
  margin-bottom: 5px;
  color: var(--ah-text-faint);
  font-size: 10px;
}

.pool-metric strong {
  color: var(--ah-text);
  font-size: 22px;
  font-weight: 750;
  letter-spacing: -0.04em;
}

.pool-metric small {
  margin-left: 3px;
  color: var(--ah-text-faint);
  font-size: 10px;
}

/* ---------------- 筛选 ---------------- */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 15px 18px;
}

.filter-controls {
  display: flex;
  min-width: 0;
  flex: 1;
  align-items: center;
  gap: 9px;
}

.keyword-input {
  width: min(360px, 100%);
}

.exchange-select {
  width: 160px;
}

.filter-note {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 7px;
  font-size: 10px;
  color: var(--ah-text-faint);
}

.filter-note__dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--ah-mint-dark);
}

/* ---------------- 表格 ---------------- */
.table-card {
  padding: 20px 22px 16px;
  overflow: hidden;
}

.table-heading {
  margin-bottom: 14px;
}

.table-heading p strong {
  color: var(--ah-text);
}

.stock-table {
  width: 100%;
  cursor: pointer;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name-avatar {
  display: grid;
  width: 25px;
  height: 25px;
  flex: 0 0 25px;
  place-items: center;
  border-radius: 7px;
  background: #f0f5ff;
  color: #3868c6;
  font-size: 11px;
  font-weight: 700;
}

.name-cell strong {
  font-size: 12px;
  font-weight: 650;
  color: var(--ah-text);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 34px 0;
}

.empty-state strong {
  margin-bottom: 4px;
  font-size: 13px;
}

.empty-state p {
  margin: 0 0 12px;
  color: var(--ah-text-soft);
  font-size: 11px;
}

.pagination-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding-top: 15px;
  border-top: 1px solid #f1f4f8;
  margin-top: 4px;
  color: var(--ah-text-faint);
  font-size: 10px;
}

/* ---------------- 详情抽屉 ---------------- */
.detail-panel {
  display: flex;
  min-height: 220px;
  flex-direction: column;
  gap: 18px;
}

.detail-head {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-bottom: 17px;
  border-bottom: 1px solid var(--ah-border);
}

.detail-symbol {
  display: grid;
  width: 62px;
  height: 62px;
  flex: 0 0 62px;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(145deg, #10233b, #17416b);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.detail-head h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 750;
  letter-spacing: -0.03em;
}

.detail-head p {
  margin: 4px 0 0;
  color: var(--ah-text-soft);
  font-size: 11px;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.detail-descriptions {
  margin-top: 1px;
}

.detail-note {
  padding: 13px 14px;
  border: 1px solid var(--ah-border);
  border-radius: 9px;
  background: #fafcff;
}

.detail-note strong {
  font-size: 11px;
}

.detail-note p {
  margin: 5px 0 0;
  color: var(--ah-text-soft);
  font-size: 11px;
  line-height: 1.7;
}

/* ---------------- 响应式 ---------------- */
@media (max-width: 1000px) {
  .pool-hero {
    align-items: flex-start;
    flex-direction: column;
    gap: 18px;
  }

  .pool-metrics {
    width: 100%;
  }

  .pool-metric {
    flex: 1;
  }
}

@media (max-width: 760px) {
  .filter-bar {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;
  }

  .filter-controls {
    flex-wrap: wrap;
  }

  .keyword-input {
    width: 100%;
  }

  .filter-note {
    display: none;
  }

  .table-card {
    padding: 17px 14px 14px;
  }

  .pagination-row {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 540px) {
  .pool-hero {
    padding: 20px 18px;
  }

  .pool-metric {
    min-width: 0;
    padding: 10px;
  }

  .pool-metric strong {
    font-size: 18px;
  }

  .exchange-select {
    flex: 1;
    width: auto;
  }
}
</style>
