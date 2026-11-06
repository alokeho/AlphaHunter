<script setup>
/**
 * 平台总览页。
 *
 * 数据全部来自后端真实接口：
 * - /dashboard/summary：股票数、行情数、数据状态、依赖就绪度；
 * - /stocks：股票池预览。
 *
 * 页面不会伪造收益曲线或模型准确率；阶段未实现的能力明确标记为“待开发”。
 */
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowRight,
  CircleCheck,
  Cpu,
  DataAnalysis,
  Refresh,
  TrendCharts,
  Warning,
} from '@element-plus/icons-vue'

import { getDashboardSummary } from '@/api/system'
import { getStocks } from '@/api/stocks'
import { getApiErrorMessage } from '@/api/client'
import StatCard from '@/components/StatCard.vue'
import { useSystemStore } from '@/stores/system'
import {
  DATA_STATUS_MAP,
  exchangeLabel,
  formatDate,
  formatNumber,
} from '@/utils/format'

const router = useRouter()
const systemStore = useSystemStore()

const summary = ref(null)
const previewStocks = ref([])
const previewTotal = ref(0)
const loading = ref(true)
const error = ref('')

const dataStatus = computed(
  () => DATA_STATUS_MAP[summary.value?.data_status] || DATA_STATUS_MAP.empty,
)

const capabilityPercent = computed(() => {
  const ready = Number(summary.value?.capability_ready || 0)
  const total = Number(summary.value?.capability_total || 0)
  if (!total) return 0
  return Math.round((ready / total) * 100)
})

const healthLabel = computed(() => {
  if (systemStore.checking) return '检测中'
  return systemStore.isOnline ? '在线' : '离线'
})

const pipeline = [
  {
    no: '01',
    title: '工程底座',
    description: 'FastAPI、Vue3、SQLAlchemy 与配置体系',
    state: 'done',
    tag: '已完成',
  },
  {
    no: '02',
    title: '数据接入',
    description: 'AKShare 适配器与行情同步任务',
    state: 'active',
    tag: '适配器就绪',
  },
  {
    no: '03',
    title: '因子研究',
    description: '技术指标、因子清洗与 IC 分析',
    state: 'planned',
    tag: '待开发',
  },
  {
    no: '04',
    title: 'AI 选股',
    description: 'LightGBM / XGBoost 与 Optuna 调参',
    state: 'planned',
    tag: '待开发',
  },
  {
    no: '05',
    title: '策略回测',
    description: 'Backtrader 回测、绩效归因与风控',
    state: 'planned',
    tag: '待开发',
  },
]

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const [summaryData, stocksData] = await Promise.all([
      getDashboardSummary(),
      getStocks({ page: 1, page_size: 5 }),
    ])
    summary.value = summaryData
    previewStocks.value = stocksData.items
    previewTotal.value = stocksData.total
  } catch (requestError) {
    error.value = getApiErrorMessage(requestError)
  } finally {
    loading.value = false
  }
}

function goStocks() {
  router.push('/stocks')
}

function openDocs() {
  window.open('/docs', '_blank', 'noopener,noreferrer')
}

onMounted(loadDashboard)
</script>

<template>
  <div v-loading="loading" class="page-stack dashboard-page">
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="page-alert"
    />

    <!-- 首屏主视觉：强调平台定位与阶段状态 -->
    <section class="hero">
      <div class="hero__content">
        <div class="eyebrow hero__eyebrow">
          <span class="live-dot" />
          PHASE 1 · FOUNDATION
        </div>

        <h1>
          把 A 股研究，做成一条<span>可复现</span>的流水线。
        </h1>

        <p class="hero__description">
          AlphaHunter 正在搭建数据、因子、模型与回测的统一底座。当前阶段聚焦工程框架，
          让每一次研究都能被版本化、复现与验证。
        </p>

        <div class="hero__actions">
          <el-button type="primary" class="hero__primary" @click="goStocks">
            浏览股票池
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <el-button class="hero__secondary" @click="openDocs">查看 API 文档</el-button>
        </div>

        <div class="hero__meta">
          <span>FastAPI</span>
          <i />
          <span>SQLAlchemy</span>
          <i />
          <span>Vue 3</span>
          <i />
          <span>SQLite</span>
        </div>
      </div>

      <aside class="console">
        <div class="console__head">
          <span>RUNTIME STATUS</span>
          <span class="console__badge" :class="{ offline: !systemStore.isOnline }">
            {{ healthLabel }}
          </span>
        </div>

        <div class="console__list">
          <div class="console__row">
            <span>当前阶段</span>
            <strong>{{ summary?.phase || 'Phase 1 · 基础框架' }}</strong>
          </div>
          <div class="console__row">
            <span>数据状态</span>
            <el-tag
              :type="dataStatus.type"
              size="small"
              effect="dark"
              class="console__status-tag"
            >
              {{ dataStatus.label }}
            </el-tag>
          </div>
          <div class="console__row">
            <span>最新交易日</span>
            <strong class="mono">{{ formatDate(summary?.latest_trade_date) }}</strong>
          </div>
          <div class="console__row">
            <span>数据库</span>
            <strong>SQLite / 可切 PostgreSQL</strong>
          </div>
        </div>

        <div class="console__progress">
          <div class="console__progress-label">
            <span>技术栈就绪度</span>
            <strong>
              {{ summary?.capability_ready ?? 0 }} /
              {{ summary?.capability_total ?? 0 }}
            </strong>
          </div>
          <el-progress
            :percentage="capabilityPercent"
            :stroke-width="6"
            :show-text="false"
            color="#31d0a5"
          />
        </div>

        <p class="console__note">
          <el-icon><CircleCheck /></el-icon>
          基础服务、数据层与前端框架已完成自检，行情同步将在第二阶段接入。
        </p>
      </aside>
    </section>

    <!-- 核心指标 -->
    <section class="stat-grid">
      <StatCard label="股票池" :value="formatNumber(summary?.stock_count)" unit="只" accent="blue">
        <template #icon><el-icon><DataAnalysis /></el-icon></template>
        <template #hint>当前为演示静态资料</template>
      </StatCard>

      <StatCard
        label="日行情记录"
        :value="formatNumber(summary?.daily_bar_count)"
        unit="条"
        accent="mint"
      >
        <template #icon><el-icon><TrendCharts /></el-icon></template>
        <template #hint>接入 AKShare 后写入</template>
      </StatCard>

      <StatCard
        label="AI 选股模型"
        :value="formatNumber(summary?.ai_model_count ?? 0)"
        unit="个"
        accent="violet"
      >
        <template #icon><el-icon><Cpu /></el-icon></template>
        <template #hint>LightGBM / XGBoost 待接入</template>
      </StatCard>

      <StatCard label="API 服务" :value="healthLabel" accent="amber">
        <template #icon><el-icon><CircleCheck /></el-icon></template>
        <template #hint>
          最近检测：{{ systemStore.lastChecked || '等待检测' }}
        </template>
      </StatCard>
    </section>

    <!-- 研究流水线 + 数据状态 -->
    <section class="content-grid">
      <article class="surface-card pipeline-card">
        <div class="section-heading">
          <div>
            <h2>研究流水线</h2>
            <p>从原始行情到选股组合，每一步都保留可追溯的工程边界。</p>
          </div>
          <span class="stage-chip">PHASE 1 / 5</span>
        </div>

        <div class="pipeline">
          <div
            v-for="(step, index) in pipeline"
            :key="step.no"
            class="pipeline__step"
            :class="`is-${step.state}`"
          >
            <div class="pipeline__rail">
              <span class="pipeline__number mono">{{ step.no }}</span>
              <i v-if="index < pipeline.length - 1" class="pipeline__line" />
            </div>
            <div class="pipeline__body">
              <div class="pipeline__title">
                <strong>{{ step.title }}</strong>
                <el-tag
                  :type="step.state === 'done' ? 'success' : step.state === 'active' ? 'warning' : 'info'"
                  size="small"
                  effect="plain"
                >
                  {{ step.tag }}
                </el-tag>
              </div>
              <p>{{ step.description }}</p>
            </div>
          </div>
        </div>
      </article>

      <article class="surface-card data-card">
        <div class="section-heading">
          <div>
            <h2>数据概览</h2>
            <p>当前数据库中的真实统计，不包含模拟收益。</p>
          </div>
          <el-button text circle :loading="loading" aria-label="刷新数据" @click="loadDashboard">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>

        <div class="data-list">
          <div class="data-row">
            <span>股票数量</span>
            <strong class="mono">{{ formatNumber(summary?.stock_count) }} 只</strong>
          </div>
          <div class="data-row">
            <span>行情记录</span>
            <strong class="mono">{{ formatNumber(summary?.daily_bar_count) }} 条</strong>
          </div>
          <div class="data-row">
            <span>最新交易日</span>
            <strong class="mono">{{ formatDate(summary?.latest_trade_date) }}</strong>
          </div>
          <div class="data-row">
            <span>数据状态</span>
            <el-tag :type="dataStatus.type" size="small">{{ dataStatus.label }}</el-tag>
          </div>
        </div>

        <div class="data-callout">
          <el-icon class="data-callout__icon"><Warning /></el-icon>
          <div>
            <strong>等待真实行情接入</strong>
            <p>
              股票池为公开静态演示数据。下一阶段将通过 AKShare 同步日线行情，
              再进行因子构建与模型训练。
            </p>
          </div>
        </div>

        <el-button class="data-action" @click="goStocks">
          查看完整股票池
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </article>
    </section>

    <!-- 股票池预览 -->
    <section class="surface-card preview-card">
      <div class="section-heading">
        <div>
          <h2>股票池预览</h2>
          <p>覆盖沪深主板、创业板与科创板的代表性标的。</p>
        </div>
        <el-button text type="primary" @click="goStocks">
          全部 {{ previewTotal }} 只
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>

      <el-table :data="previewStocks" size="small" class="preview-table" @row-click="goStocks">
        <el-table-column prop="symbol" label="代码" width="100">
          <template #default="{ row }">
            <span class="code-chip">{{ row.symbol }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="110">
          <template #default="{ row }">
            <strong class="stock-name">{{ row.name }}</strong>
          </template>
        </el-table-column>
        <el-table-column prop="exchange" label="交易所" width="100">
          <template #default="{ row }">{{ exchangeLabel(row.exchange) }}</template>
        </el-table-column>
        <el-table-column prop="market" label="板块" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.market }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="industry" label="行业" min-width="110" />
        <el-table-column prop="list_date" label="上市日期" width="120">
          <template #default="{ row }">{{ formatDate(row.list_date) }}</template>
        </el-table-column>
      </el-table>

      <div class="preview-foot">
        <span>展示最近查询的前 5 条记录</span>
        <span class="mono">READ ONLY · DEMO DATA</span>
      </div>
    </section>
  </div>
</template>

<style scoped>
.dashboard-page {
  gap: 18px;
}

.page-alert {
  border-radius: var(--ah-radius);
}

/* ---------------- Hero ---------------- */
.hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(300px, 0.78fr);
  gap: 34px;
  padding: 34px 36px;
  overflow: hidden;
  border: 1px solid rgb(255 255 255 / 7%);
  border-radius: 20px;
  background:
    radial-gradient(circle at 84% 8%, rgb(49 208 165 / 18%), transparent 28%),
    radial-gradient(circle at 8% 100%, rgb(37 99 235 / 28%), transparent 38%),
    linear-gradient(125deg, #0b1424 0%, #10233b 55%, #123448 100%);
  box-shadow: 0 18px 40px rgb(11 20 36 / 16%);
  color: #fff;
}

.hero::after {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgb(255 255 255 / 3%) 1px, transparent 1px),
    linear-gradient(90deg, rgb(255 255 255 / 3%) 1px, transparent 1px);
  background-size: 44px 44px;
  content: "";
  mask-image: linear-gradient(90deg, transparent, #000 45%, transparent);
  pointer-events: none;
}

.hero__content {
  position: relative;
  z-index: 1;
  align-self: center;
}

.hero__eyebrow {
  color: #8db9d5;
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--ah-mint);
  box-shadow: 0 0 0 5px rgb(49 208 165 / 12%);
}

.hero h1 {
  max-width: 660px;
  margin: 16px 0 14px;
  font-size: clamp(26px, 2.6vw, 35px);
  font-weight: 760;
  letter-spacing: -0.045em;
  line-height: 1.28;
  text-wrap: balance;
}

.hero h1 span {
  color: var(--ah-mint);
}

.hero__description {
  max-width: 590px;
  margin: 0;
  color: #a9bdd1;
  font-size: 13px;
  line-height: 1.85;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 24px;
}

.hero__primary {
  height: 40px;
  padding: 0 18px;
  border: 0;
  background: var(--ah-mint);
  color: #062a22;
  box-shadow: 0 8px 18px rgb(49 208 165 / 18%);
}

.hero__primary:hover {
  background: #5fe0bc;
  color: #062a22;
}

.hero__secondary {
  height: 40px;
  border-color: rgb(255 255 255 / 18%);
  background: rgb(255 255 255 / 4%);
  color: #d9e7f2;
}

.hero__secondary:hover {
  border-color: rgb(255 255 255 / 35%);
  background: rgb(255 255 255 / 9%);
  color: #fff;
}

.hero__meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 24px;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 9px;
  letter-spacing: 0.08em;
  color: #66829b;
}

.hero__meta i {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #3d5870;
}

/* ---------------- 控制台面板 ---------------- */
.console {
  position: relative;
  z-index: 1;
  align-self: stretch;
  padding: 18px;
  border: 1px solid rgb(255 255 255 / 9%);
  border-radius: 15px;
  background: rgb(5 14 25 / 38%);
  backdrop-filter: blur(8px);
}

.console__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid rgb(255 255 255 / 7%);
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: #7591aa;
}

.console__badge {
  padding: 2px 7px;
  border: 1px solid rgb(49 208 165 / 30%);
  border-radius: 99px;
  background: rgb(49 208 165 / 10%);
  color: #65e1bd;
  font-family: inherit;
  font-size: 9px;
  letter-spacing: 0.04em;
}

.console__badge.offline {
  border-color: rgb(227 77 89 / 35%);
  background: rgb(227 77 89 / 10%);
  color: #ff8e98;
}

.console__list {
  display: flex;
  flex-direction: column;
}

.console__row {
  display: flex;
  min-height: 38px;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 1px dashed rgb(255 255 255 / 6%);
  font-size: 11px;
}

.console__row span {
  color: #8097ad;
}

.console__row strong {
  max-width: 64%;
  overflow: hidden;
  color: #d8e5ef;
  font-size: 10px;
  font-weight: 600;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 深色控制台中的状态标签使用高对比配色，避免暗色主题下文字不可见。 */
.console__status-tag {
  border-color: transparent !important;
  background: #f6c76c !important;
  color: #352106 !important;
  font-weight: 700 !important;
}

.console__progress {
  margin-top: 15px;
}

.console__progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 7px;
  font-size: 10px;
  color: #8097ad;
}

.console__progress-label strong {
  color: #cfdeea;
}

.console__progress :deep(.el-progress-bar__outer) {
  background: rgb(255 255 255 / 8%);
}

.console__note {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  margin: 14px 0 0;
  color: #6f879e;
  font-size: 9px;
  line-height: 1.7;
}

.console__note .el-icon {
  margin-top: 2px;
  color: var(--ah-mint);
}

/* ---------------- 指标与内容区 ---------------- */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.8fr);
  gap: 14px;
}

.pipeline-card,
.data-card,
.preview-card {
  padding: 21px 22px;
}

.stage-chip {
  padding: 4px 8px;
  border: 1px solid #e5ebf4;
  border-radius: 6px;
  background: #f8fafd;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: #8b9aad;
}

.pipeline {
  display: flex;
  flex-direction: column;
}

.pipeline__step {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 12px;
  min-height: 67px;
}

.pipeline__rail {
  display: flex;
  align-items: center;
  flex-direction: column;
}

.pipeline__number {
  display: grid;
  width: 32px;
  height: 32px;
  flex: 0 0 32px;
  place-items: center;
  border: 1px solid #e3e9f1;
  border-radius: 9px;
  background: #f8fafd;
  color: #94a3b5;
  font-size: 9px;
  font-weight: 700;
}

.pipeline__line {
  width: 1px;
  flex: 1;
  margin: 4px 0;
  background: #edf1f6;
}

.pipeline__body {
  padding: 3px 0 16px;
}

.pipeline__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.pipeline__title strong {
  font-size: 12px;
  color: var(--ah-text);
}

.pipeline__body p {
  margin: 3px 0 0;
  color: var(--ah-text-soft);
  font-size: 11px;
}

.pipeline__step.is-done .pipeline__number {
  border-color: #cfeee4;
  background: #ecfaf5;
  color: #0f9f7a;
}

.pipeline__step.is-active .pipeline__number {
  border-color: #f0dfbd;
  background: #fff9ed;
  color: #b66a08;
}

.pipeline__step.is-planned {
  opacity: 0.72;
}

.data-list {
  display: flex;
  flex-direction: column;
}

.data-row {
  display: flex;
  min-height: 38px;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-bottom: 1px dashed #edf1f6;
  font-size: 11px;
}

.data-row span {
  color: var(--ah-text-soft);
}

.data-row strong {
  font-size: 11px;
  font-weight: 650;
}

.data-callout {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 16px;
  padding: 12px;
  border: 1px solid #f0e4ca;
  border-radius: 9px;
  background: #fffbf2;
}

.data-callout__icon {
  flex: 0 0 auto;
  margin-top: 2px;
  color: #ca7a12;
}

.data-callout strong {
  font-size: 11px;
  color: #845817;
}

.data-callout p {
  margin: 3px 0 0;
  color: #9b7b45;
  font-size: 10px;
  line-height: 1.65;
}

.data-action {
  width: 100%;
  margin-top: 14px;
  border-color: #e4eaf2;
  font-size: 11px;
}

/* ---------------- 股票预览 ---------------- */
.preview-card {
  padding-bottom: 14px;
}

.preview-table {
  width: 100%;
  cursor: pointer;
}

.stock-name {
  font-size: 12px;
  color: var(--ah-text);
}

.preview-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f1f4f8;
  font-size: 9px;
  color: var(--ah-text-faint);
}

/* ---------------- 响应式 ---------------- */
@media (max-width: 1180px) {
  .hero {
    grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
    gap: 24px;
    padding: 28px;
  }

  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .console {
    margin-top: 2px;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .hero {
    padding: 24px 20px;
  }

  .hero__meta {
    flex-wrap: wrap;
    gap: 7px;
  }

  .stat-grid {
    grid-template-columns: 1fr;
  }

  .pipeline-card,
  .data-card,
  .preview-card {
    padding: 18px 16px;
  }

  .preview-foot {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
