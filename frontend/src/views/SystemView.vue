<script setup>
/**
 * 系统状态页。
 *
 * 展示：
 * - FastAPI / Python / 数据库 / 运行时长；
 * - 技术栈依赖安装矩阵（核心、数据、机器学习、量化研究）；
 * - 阶段一 API 清单与模块架构说明。
 */
import { computed, onMounted, ref } from 'vue'
import {
  CircleCheck,
  Connection,
  Cpu,
  DataAnalysis,
  Document,
  Monitor,
  Refresh,
  Warning,
} from '@element-plus/icons-vue'

import { getApiErrorMessage } from '@/api/client'
import { getSystemInfo } from '@/api/system'
import { useSystemStore } from '@/stores/system'
import { formatDateTime, formatUptime } from '@/utils/format'

const systemStore = useSystemStore()

const info = ref(null)
const loading = ref(true)
const error = ref('')

const environmentLabels = {
  development: '开发环境',
  testing: '测试环境',
  production: '生产环境',
}

const groupIcons = {
  core: Monitor,
  data: DataAnalysis,
  ai: Cpu,
  quant: Monitor,
}

const apiEndpoints = [
  { method: 'GET', path: '/api/v1/health', description: '服务与数据库健康检查' },
  { method: 'GET', path: '/api/v1/system/info', description: '运行环境与依赖能力矩阵' },
  { method: 'GET', path: '/api/v1/stocks', description: '股票池分页、搜索与交易所筛选' },
  { method: 'GET', path: '/api/v1/stocks/filters', description: '交易所与行业筛选项' },
  { method: 'GET', path: '/api/v1/stocks/{symbol}', description: '单只股票静态详情' },
  { method: 'GET', path: '/api/v1/dashboard/summary', description: '首页聚合统计' },
]

const capabilityGroups = computed(() => info.value?.capabilities || [])

const installedCount = computed(() =>
  capabilityGroups.value.reduce((sum, group) => sum + Number(group.ready || 0), 0),
)

const capabilityTotal = computed(() =>
  capabilityGroups.value.reduce((sum, group) => sum + Number(group.total || 0), 0),
)

const capabilityPercent = computed(() => {
  if (!capabilityTotal.value) return 0
  return Math.round((installedCount.value / capabilityTotal.value) * 100)
})

const allRequiredReady = computed(() =>
  capabilityGroups.value.every((group) =>
    group.packages.every((item) => !item.required || item.available),
  ),
)

const environmentLabel = computed(
  () => environmentLabels[info.value?.environment] || info.value?.environment || '—',
)

async function loadSystemInfo() {
  loading.value = true
  error.value = ''
  try {
    info.value = await getSystemInfo()
  } catch (requestError) {
    error.value = getApiErrorMessage(requestError)
  } finally {
    loading.value = false
  }
}

async function refreshAll() {
  await Promise.all([loadSystemInfo(), systemStore.checkHealth()])
}

function openDocs() {
  window.open('/docs', '_blank', 'noopener,noreferrer')
}

function packageStatusType(item) {
  if (item.available) return 'success'
  return item.required ? 'danger' : 'info'
}

onMounted(loadSystemInfo)
</script>

<template>
  <div v-loading="loading" class="page-stack system-page">
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="page-alert"
    />

    <!-- 运行总览 -->
    <section class="surface-card system-hero">
      <div class="system-hero__copy">
        <div class="eyebrow">
          <span class="hero-dot" />
          RUNTIME INSPECTION
        </div>
        <h2>AlphaHunter 运行环境</h2>
        <p>
          依赖检测只判断包是否可导入并读取版本号，不会在启动时加载大型模型，
          因此不会拖慢 API 冷启动。
        </p>
        <div class="hero-actions">
          <el-button type="primary" @click="openDocs">
            <el-icon><Document /></el-icon>
            打开 Swagger
          </el-button>
          <el-button :loading="loading" @click="refreshAll">
            <el-icon><Refresh /></el-icon>
            重新检测
          </el-button>
        </div>
      </div>

      <div class="environment-card">
        <div class="environment-card__head">
          <span>ENVIRONMENT</span>
          <span class="env-badge">{{ environmentLabel }}</span>
        </div>
        <div class="environment-row">
          <span>后端版本</span>
          <strong class="mono">v{{ info?.version || '—' }}</strong>
        </div>
        <div class="environment-row">
          <span>当前阶段</span>
          <strong>{{ info?.phase || 'Phase 1 · 基础框架' }}</strong>
        </div>
        <div class="environment-row">
          <span>启动时间</span>
          <strong class="mono">{{ formatDateTime(info?.started_at) }}</strong>
        </div>
        <div class="environment-row">
          <span>已运行</span>
          <strong>{{ formatUptime(info?.uptime_seconds) }}</strong>
        </div>
        <div class="environment-health">
          <span :class="{ online: systemStore.isOnline }" />
          {{ systemStore.isOnline ? 'API 健康检查通过' : 'API 当前不可用' }}
        </div>
      </div>
    </section>

    <!-- 运行指标 -->
    <section class="metric-grid">
      <article class="metric-card">
        <span class="metric-card__label">Python</span>
        <strong class="mono">{{ info?.python_version || '—' }}</strong>
        <small>CPython 运行时</small>
      </article>
      <article class="metric-card">
        <span class="metric-card__label">数据库</span>
        <strong class="mono">{{ info?.database_backend || '—' }}</strong>
        <small>SQLite 可平滑迁移</small>
      </article>
      <article class="metric-card">
        <span class="metric-card__label">依赖就绪</span>
        <strong class="mono">{{ installedCount }} / {{ capabilityTotal }}</strong>
        <small>{{ capabilityPercent }}% 技术栈可用</small>
      </article>
      <article class="metric-card">
        <span class="metric-card__label">API 前缀</span>
        <strong class="mono">{{ info?.api_prefix || '/api/v1' }}</strong>
        <small>OpenAPI 3 契约</small>
      </article>
    </section>

    <!-- 依赖矩阵 -->
    <section class="surface-card capability-section">
      <div class="section-heading capability-heading">
        <div>
          <h2>技术栈能力矩阵</h2>
          <p>绿色代表依赖可导入；未安装的可选依赖不会阻止阶段一服务启动。</p>
        </div>
        <div class="capability-score">
          <span>READY</span>
          <strong class="mono">{{ capabilityPercent }}%</strong>
        </div>
      </div>

      <div class="capability-progress">
        <el-progress
          :percentage="capabilityPercent"
          :stroke-width="7"
          :show-text="false"
          :color="allRequiredReady ? '#14aa82' : '#d97706'"
        />
      </div>

      <div class="capability-grid">
        <article v-for="group in capabilityGroups" :key="group.key" class="capability-card">
          <header class="capability-card__head">
            <div class="capability-icon">
              <el-icon><component :is="groupIcons[group.key] || Monitor" /></el-icon>
            </div>
            <div class="capability-title">
              <strong>{{ group.label }}</strong>
              <span>{{ group.description }}</span>
            </div>
            <span class="capability-count mono">{{ group.ready }}/{{ group.total }}</span>
          </header>

          <div class="package-list">
            <div v-for="item in group.packages" :key="item.key" class="package-row">
              <span class="package-dot" :class="{ ready: item.available }" />
              <span class="package-label">{{ item.label }}</span>
              <el-tag v-if="item.required" size="small" type="info" effect="plain">
                核心
              </el-tag>
              <span class="package-version mono">
                {{ item.available ? item.version : '未安装' }}
              </span>
              <el-tag :type="packageStatusType(item)" size="small" effect="plain">
                {{ item.available ? '就绪' : '缺失' }}
              </el-tag>
            </div>
          </div>
        </article>
      </div>
    </section>

    <!-- API 与架构 -->
    <section class="bottom-grid">
      <article class="surface-card api-card">
        <div class="section-heading">
          <div>
            <h2>阶段一 API 清单</h2>
            <p>所有接口均可在 Swagger 中查看 schema 并直接调试。</p>
          </div>
          <el-button text type="primary" @click="openDocs">
            查看文档
            <el-icon class="el-icon--right"><Connection /></el-icon>
          </el-button>
        </div>

        <div class="endpoint-list">
          <div v-for="endpoint in apiEndpoints" :key="endpoint.path" class="endpoint-row">
            <span class="method-badge">{{ endpoint.method }}</span>
            <code>{{ endpoint.path }}</code>
            <span class="endpoint-description">{{ endpoint.description }}</span>
          </div>
        </div>
      </article>

      <article class="surface-card architecture-card">
        <div class="section-heading">
          <div>
            <h2>分层架构</h2>
            <p>模块边界清晰，便于第二阶段扩展数据同步与模型服务。</p>
          </div>
        </div>

        <div class="architecture-list">
          <div class="architecture-item">
            <span class="architecture-index mono">01</span>
            <div>
              <strong>API 层</strong>
              <p>路由、参数校验、统一错误响应与 OpenAPI 文档。</p>
            </div>
          </div>
          <div class="architecture-item">
            <span class="architecture-index mono">02</span>
            <div>
              <strong>服务层</strong>
              <p>股票查询、仪表盘聚合，以及可替换的 AKShare 数据适配器。</p>
            </div>
          </div>
          <div class="architecture-item">
            <span class="architecture-index mono">03</span>
            <div>
              <strong>数据层</strong>
              <p>SQLAlchemy 2.0 ORM、会话管理、SQLite 初始化与种子数据。</p>
            </div>
          </div>
          <div class="architecture-item">
            <span class="architecture-index mono">04</span>
            <div>
              <strong>展示层</strong>
              <p>Vue 3、Vite、Element Plus 与 Pinia，通过 Axios 消费 API。</p>
            </div>
          </div>
        </div>

        <div class="architecture-note">
          <el-icon><CircleCheck /></el-icon>
          <span>阶段一只建立基础框架，不包含因子计算、模型训练与策略回测。</span>
        </div>
      </article>
    </section>

    <!-- 配置提示 -->
    <section class="config-note">
      <el-icon><Warning /></el-icon>
      <p>
        数据库连接：<code>{{ info?.database_url || '—' }}</code>
        · 生产环境请通过 <code>ALPHAHUNTER_SECRET_KEY</code> 设置随机密钥，
        并将 <code>ALPHAHUNTER_DEBUG</code> 设为 false。
      </p>
    </section>
  </div>
</template>

<style scoped>
.system-page {
  gap: 15px;
}

.page-alert {
  border-radius: var(--ah-radius);
}

/* ---------------- 运行总览 ---------------- */
.system-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(300px, 0.76fr);
  gap: 28px;
  padding: 26px 28px;
  background:
    radial-gradient(circle at 92% 12%, rgb(37 99 235 / 8%), transparent 34%),
    #fff;
}

.system-hero__copy {
  align-self: center;
}

.hero-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ah-mint-dark);
  box-shadow: 0 0 0 4px rgb(20 170 130 / 9%);
}

.system-hero h2 {
  margin: 8px 0 7px;
  font-size: 23px;
  font-weight: 750;
  letter-spacing: -0.035em;
}

.system-hero p {
  max-width: 600px;
  margin: 0;
  color: var(--ah-text-soft);
  font-size: 12px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  margin-top: 18px;
}

.environment-card {
  padding: 16px;
  border: 1px solid #e8edf5;
  border-radius: 13px;
  background: #f9fbfe;
}

.environment-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 10px;
  border-bottom: 1px solid #edf1f6;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #8a99ab;
}

.env-badge {
  padding: 2px 7px;
  border: 1px solid #dce6f4;
  border-radius: 99px;
  background: #fff;
  color: #5d7898;
  font-family: inherit;
  letter-spacing: 0.03em;
}

.environment-row {
  display: flex;
  min-height: 35px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px dashed #edf1f6;
  font-size: 10px;
}

.environment-row span {
  color: var(--ah-text-soft);
}

.environment-row strong {
  max-width: 70%;
  overflow: hidden;
  color: #31445b;
  font-size: 10px;
  font-weight: 600;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.environment-health {
  display: flex;
  align-items: center;
  gap: 7px;
  padding-top: 11px;
  color: var(--ah-text-soft);
  font-size: 10px;
}

.environment-health span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ah-red);
}

.environment-health span.online {
  background: var(--ah-mint-dark);
  box-shadow: 0 0 0 3px rgb(20 170 130 / 9%);
}

/* ---------------- 指标 ---------------- */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.metric-card {
  padding: 15px 16px;
  border: 1px solid var(--ah-border);
  border-radius: var(--ah-radius);
  background: #fff;
  box-shadow: var(--ah-shadow-sm);
}

.metric-card__label {
  display: block;
  margin-bottom: 6px;
  color: var(--ah-text-faint);
  font-size: 10px;
}

.metric-card strong {
  display: block;
  color: var(--ah-text);
  font-size: 19px;
  font-weight: 750;
  letter-spacing: -0.035em;
}

.metric-card small {
  display: block;
  margin-top: 4px;
  color: var(--ah-text-faint);
  font-size: 9px;
}

/* ---------------- 依赖矩阵 ---------------- */
.capability-section {
  padding: 22px;
}

.capability-heading {
  margin-bottom: 12px;
}

.capability-score {
  display: flex;
  align-items: baseline;
  gap: 7px;
}

.capability-score span {
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--ah-text-faint);
}

.capability-score strong {
  color: var(--ah-mint-dark);
  font-size: 18px;
  letter-spacing: -0.03em;
}

.capability-progress {
  margin-bottom: 18px;
}

.capability-progress :deep(.el-progress-bar__outer) {
  background: #eff3f8;
}

.capability-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.capability-card {
  padding: 15px;
  border: 1px solid #e9eef5;
  border-radius: 12px;
  background: #fcfdff;
}

.capability-card__head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eef2f7;
}

.capability-icon {
  display: grid;
  width: 32px;
  height: 32px;
  flex: 0 0 32px;
  place-items: center;
  border: 1px solid #e2e9f3;
  border-radius: 9px;
  background: #fff;
  color: var(--ah-blue);
}

.capability-title {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
}

.capability-title strong {
  font-size: 12px;
  font-weight: 700;
}

.capability-title span {
  overflow: hidden;
  margin-top: 1px;
  color: var(--ah-text-faint);
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.capability-count {
  color: var(--ah-text-soft);
  font-size: 10px;
}

.package-list {
  display: flex;
  flex-direction: column;
}

.package-row {
  display: flex;
  min-height: 33px;
  align-items: center;
  gap: 7px;
  border-bottom: 1px dashed #f0f3f7;
  font-size: 10px;
}

.package-row:last-child {
  border-bottom: 0;
}

.package-dot {
  width: 5px;
  height: 5px;
  flex: 0 0 5px;
  border-radius: 50%;
  background: #c9d2df;
}

.package-dot.ready {
  background: var(--ah-mint-dark);
}

.package-label {
  min-width: 76px;
  color: #41556d;
  font-weight: 600;
}

.package-version {
  flex: 1;
  overflow: hidden;
  color: var(--ah-text-faint);
  font-size: 9px;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---------------- 底部区域 ---------------- */
.bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(300px, 0.8fr);
  gap: 12px;
}

.api-card,
.architecture-card {
  padding: 20px 21px;
}

.endpoint-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.endpoint-row {
  display: grid;
  grid-template-columns: 40px minmax(200px, 1.15fr) minmax(150px, 0.9fr);
  align-items: center;
  gap: 10px;
  min-height: 36px;
  border-bottom: 1px dashed #eff3f8;
}

.endpoint-row:last-child {
  border-bottom: 0;
}

.method-badge {
  display: inline-flex;
  width: 34px;
  height: 19px;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  background: #edf5ff;
  color: #2e63b7;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 8px;
  font-weight: 700;
}

.endpoint-row code {
  overflow: hidden;
  color: #384e66;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.endpoint-description {
  color: var(--ah-text-faint);
  font-size: 9px;
}

.architecture-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.architecture-item {
  display: flex;
  gap: 10px;
  padding: 9px 0;
  border-bottom: 1px dashed #eff3f8;
}

.architecture-item:last-child {
  border-bottom: 0;
}

.architecture-index {
  display: grid;
  width: 27px;
  height: 27px;
  flex: 0 0 27px;
  place-items: center;
  border-radius: 7px;
  background: #f0f5ff;
  color: #4871bb;
  font-size: 8px;
  font-weight: 700;
}

.architecture-item strong {
  font-size: 11px;
}

.architecture-item p {
  margin: 2px 0 0;
  color: var(--ah-text-faint);
  font-size: 9px;
  line-height: 1.6;
}

.architecture-note {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f3f7;
  color: var(--ah-text-faint);
  font-size: 9px;
  line-height: 1.6;
}

.architecture-note .el-icon {
  margin-top: 2px;
  color: var(--ah-mint-dark);
}

/* ---------------- 配置提示 ---------------- */
.config-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 15px;
  border: 1px solid #eee5d5;
  border-radius: 10px;
  background: #fffcf6;
  color: #8c744e;
  font-size: 10px;
}

.config-note .el-icon {
  flex: 0 0 auto;
  margin-top: 2px;
  color: #c88b2a;
}

.config-note p {
  margin: 0;
  line-height: 1.7;
}

.config-note code {
  padding: 1px 4px;
  border-radius: 3px;
  background: #f7f0e3;
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 9px;
}

/* ---------------- 响应式 ---------------- */
@media (max-width: 1100px) {
  .system-hero {
    grid-template-columns: 1fr;
  }

  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .capability-grid {
    grid-template-columns: 1fr;
  }

  .endpoint-row {
    grid-template-columns: 40px minmax(0, 1fr);
  }

  .endpoint-description {
    display: none;
  }
}

@media (max-width: 560px) {
  .system-hero,
  .capability-section,
  .api-card,
  .architecture-card {
    padding: 18px 16px;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }

  .environment-row strong {
    max-width: 62%;
  }
}
</style>
