<script setup>
/**
 * 主布局。
 *
 * 负责：
 * - 左侧品牌导航与当前阶段说明；
 * - 顶部页面标题、后端健康状态、刷新与 API 文档入口；
 * - 移动端抽屉式导航；
 * - 全局内容区与页脚。
 */
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  Close,
  Connection,
  DataAnalysis,
  Document,
  Menu,
  Monitor,
  Odometer,
  Refresh,
} from '@element-plus/icons-vue'

import { useSystemStore } from '@/stores/system'

const route = useRoute()
const systemStore = useSystemStore()

const mobileOpen = ref(false)
const pageTitle = computed(() => route.meta?.title || 'AlphaHunter')
const pageSubtitle = computed(() => route.meta?.subtitle || '')

const menuItems = [
  { path: '/', label: '平台总览', icon: Odometer },
  { path: '/stocks', label: '股票池', icon: DataAnalysis },
  { path: '/system', label: '系统状态', icon: Monitor },
]

let healthTimer = null

function openDocs() {
  // 开发环境由 Vite 代理、生产环境由 Nginx 代理到 FastAPI Swagger。
  window.open('/docs', '_blank', 'noopener,noreferrer')
}

watch(
  () => route.path,
  () => {
    mobileOpen.value = false
  },
)

onMounted(() => {
  systemStore.checkHealth()
  // 每 60 秒刷新一次在线状态；页面切换到后台时浏览器会自然节流。
  healthTimer = window.setInterval(() => systemStore.checkHealth(), 60000)
})

onUnmounted(() => {
  if (healthTimer) window.clearInterval(healthTimer)
})
</script>

<template>
  <div class="app-shell" :class="{ 'nav-open': mobileOpen }">
    <div class="nav-backdrop" aria-hidden="true" @click="mobileOpen = false" />

    <aside class="app-sidebar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">
          <span>AH</span>
          <i />
        </div>
        <div class="brand-copy">
          <strong>AlphaHunter</strong>
          <span>A 股 AI 量化研究</span>
        </div>
      </div>

      <div class="nav-section-label">RESEARCH CONSOLE</div>

      <el-menu
        class="side-menu"
        :default-active="route.path"
        router
        background-color="transparent"
        text-color="#9fb0c7"
        active-text-color="#ffffff"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-spacer" />

      <div class="phase-card">
        <div class="phase-card__head">
          <span class="phase-dot" />
          <span>PHASE 1</span>
        </div>
        <strong>基础框架</strong>
        <p>数据层、服务层与前端骨架已就绪，量化模型将在后续阶段接入。</p>
        <div class="phase-card__foot">
          <span>API v{{ systemStore.apiVersion }}</span>
          <el-icon><Connection /></el-icon>
        </div>
      </div>

      <div class="sidebar-footer">
        <span>AlphaHunter Lab</span>
        <span>© 2026</span>
      </div>
    </aside>

    <div class="app-main">
      <header class="topbar">
        <button
          class="mobile-menu-button"
          type="button"
          :aria-label="mobileOpen ? '关闭导航' : '打开导航'"
          @click="mobileOpen = !mobileOpen"
        >
          <el-icon :size="20"><Close v-if="mobileOpen" /><Menu v-else /></el-icon>
        </button>

        <div class="page-heading">
          <div class="breadcrumb">AlphaHunter <span>/</span> {{ pageTitle }}</div>
          <h1>{{ pageTitle }}</h1>
          <p v-if="pageSubtitle">{{ pageSubtitle }}</p>
        </div>

        <div class="topbar-actions">
          <div
            class="status-pill"
            :class="systemStore.isOnline ? 'is-online' : 'is-offline'"
            :title="systemStore.error || '后端健康检查正常'"
          >
            <span class="status-pill__dot" />
            <span class="status-pill__text">{{ systemStore.statusLabel }}</span>
            <span v-if="systemStore.lastChecked" class="status-pill__time">
              {{ systemStore.lastChecked }}
            </span>
          </div>

          <el-tooltip content="刷新后端状态" placement="bottom">
            <el-button
              class="icon-button"
              circle
              :loading="systemStore.checking"
              aria-label="刷新后端状态"
              @click="systemStore.checkHealth()"
            >
              <el-icon v-if="!systemStore.checking"><Refresh /></el-icon>
            </el-button>
          </el-tooltip>

          <el-button class="docs-button" @click="openDocs">
            <el-icon><Document /></el-icon>
            <span>API 文档</span>
          </el-button>
        </div>
      </header>

      <main class="page-body">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <footer class="app-footer">
        <span>AlphaHunter · A 股 AI 量化选股平台</span>
        <span>本平台仅用于量化研究与教学，不构成任何投资建议。</span>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--ah-bg);
}

/* ---------------- 侧边栏 ---------------- */
.app-sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 40;
  display: flex;
  width: 254px;
  flex-direction: column;
  padding: 26px 18px 18px;
  overflow-y: auto;
  background:
    radial-gradient(circle at 20% 0%, rgb(41 112 160 / 26%), transparent 36%),
    radial-gradient(circle at 120% 90%, rgb(32 190 148 / 12%), transparent 38%),
    var(--ah-navy);
  color: #fff;
  transition: transform 0.25s ease;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 8px 26px;
}

.brand-mark {
  position: relative;
  display: grid;
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  place-items: center;
  border: 1px solid rgb(255 255 255 / 14%);
  border-radius: 13px;
  background: linear-gradient(145deg, #17375a, #0e2138);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 10%);
  font-size: 15px;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.brand-mark i {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  border: 2px solid var(--ah-navy);
  border-radius: 50%;
  background: var(--ah-mint);
}

.brand-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.brand-copy strong {
  font-size: 17px;
  letter-spacing: -0.02em;
}

.brand-copy span {
  margin-top: 3px;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: #8ba0b9;
}

.nav-section-label {
  padding: 0 12px 10px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: #5e738c;
}

.side-menu {
  border-right: 0;
}

.side-menu :deep(.el-menu-item) {
  height: 46px;
  margin: 3px 0;
  border-radius: 10px;
  font-size: 14px;
  transition:
    background 0.2s ease,
    color 0.2s ease;
}

.side-menu :deep(.el-menu-item .el-icon) {
  margin-right: 11px;
  font-size: 18px;
}

.side-menu :deep(.el-menu-item:hover) {
  background: rgb(255 255 255 / 6%);
}

.side-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgb(37 99 235 / 34%), rgb(32 190 148 / 12%));
  box-shadow: inset 0 0 0 1px rgb(255 255 255 / 7%);
}

.side-menu :deep(.el-menu-item.is-active::before) {
  position: absolute;
  left: 0;
  width: 3px;
  height: 20px;
  border-radius: 0 4px 4px 0;
  background: var(--ah-mint);
  content: '';
}

.sidebar-spacer {
  flex: 1;
  min-height: 24px;
}

.phase-card {
  padding: 15px;
  border: 1px solid rgb(255 255 255 / 9%);
  border-radius: 14px;
  background: rgb(255 255 255 / 4%);
}

.phase-card__head {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 9px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.13em;
  color: #88a3c2;
}

.phase-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ah-mint);
  box-shadow: 0 0 0 4px rgb(49 208 165 / 12%);
}

.phase-card strong {
  font-size: 14px;
}

.phase-card p {
  margin: 7px 0 13px;
  font-size: 11px;
  line-height: 1.7;
  color: #7f95ae;
}

.phase-card__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid rgb(255 255 255 / 7%);
  color: #6d829a;
  font-size: 10px;
}

.sidebar-footer {
  display: flex;
  justify-content: space-between;
  padding: 18px 4px 0;
  font-size: 10px;
  color: #4f6278;
}

/* ---------------- 主区域 ---------------- */
.app-main {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  margin-left: 254px;
}

.topbar {
  position: sticky;
  z-index: 30;
  top: 0;
  display: flex;
  min-height: 88px;
  align-items: center;
  gap: 22px;
  padding: 17px 34px;
  border-bottom: 1px solid rgb(18 32 51 / 7%);
  background: rgb(243 246 251 / 88%);
  backdrop-filter: blur(16px);
}

.page-heading {
  min-width: 0;
  flex: 1;
}

.breadcrumb {
  margin-bottom: 4px;
  font-size: 11px;
  letter-spacing: 0.03em;
  color: var(--ah-text-soft);
}

.breadcrumb span {
  margin: 0 6px;
  color: #b9c4d2;
}

.page-heading h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 750;
  letter-spacing: -0.03em;
  color: var(--ah-text);
}

.page-heading p {
  margin: 4px 0 0;
  overflow: hidden;
  font-size: 12px;
  color: var(--ah-text-soft);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-pill {
  display: flex;
  height: 34px;
  align-items: center;
  gap: 7px;
  padding: 0 12px;
  border: 1px solid rgb(18 32 51 / 8%);
  border-radius: 999px;
  background: #fff;
  font-size: 12px;
  font-weight: 600;
  color: #4c5d72;
  box-shadow: 0 2px 6px rgb(18 32 51 / 4%);
}

.status-pill__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #9aa8b9;
}

.status-pill.is-online .status-pill__dot {
  background: var(--ah-mint-dark);
  box-shadow: 0 0 0 4px rgb(20 170 130 / 10%);
}

.status-pill.is-offline .status-pill__dot {
  background: var(--ah-red);
  box-shadow: 0 0 0 4px rgb(227 77 89 / 10%);
}

.status-pill__time {
  padding-left: 7px;
  border-left: 1px solid #edf0f5;
  font-size: 10px;
  font-weight: 500;
  color: #9aa8b9;
}

.icon-button {
  width: 34px;
  height: 34px;
  border-color: rgb(18 32 51 / 8%);
}

.docs-button {
  height: 34px;
  border-color: rgb(18 32 51 / 10%);
  border-radius: 9px;
  background: #fff;
  font-size: 12px;
}

.docs-button:hover {
  border-color: var(--ah-blue);
  color: var(--ah-blue);
}

.mobile-menu-button {
  display: none;
  width: 38px;
  height: 38px;
  align-items: center;
  justify-content: center;
  border: 1px solid rgb(18 32 51 / 8%);
  border-radius: 10px;
  background: #fff;
  color: var(--ah-text);
}

.page-body {
  width: 100%;
  max-width: 1500px;
  flex: 1;
  align-self: center;
  padding: 26px 34px 40px;
}

.app-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 34px 26px;
  border-top: 1px solid rgb(18 32 51 / 6%);
  font-size: 10px;
  color: #8d9aab;
}

.nav-backdrop {
  display: none;
}

/* ---------------- 页面切换动画 ---------------- */
.page-fade-enter-active,
.page-fade-leave-active {
  transition:
    opacity 0.16s ease,
    transform 0.16s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(5px);
}

/* ---------------- 响应式 ---------------- */
@media (max-width: 1080px) {
  .status-pill__time {
    display: none;
  }
}

@media (max-width: 960px) {
  .app-sidebar {
    transform: translateX(-100%);
  }

  .app-shell.nav-open .app-sidebar {
    transform: translateX(0);
  }

  .app-main {
    margin-left: 0;
  }

  .nav-backdrop {
    position: fixed;
    z-index: 35;
    inset: 0;
    background: rgb(8 17 30 / 48%);
  }

  .app-shell.nav-open .nav-backdrop {
    display: block;
  }

  .mobile-menu-button {
    display: flex;
  }

  .topbar {
    padding: 15px 22px;
  }

  .page-body {
    padding: 22px 22px 32px;
  }

  .app-footer {
    padding: 16px 22px 24px;
  }
}

@media (max-width: 640px) {
  .page-heading p,
  .docs-button span,
  .status-pill__text {
    display: none;
  }

  .status-pill {
    width: 34px;
    justify-content: center;
    padding: 0;
  }

  .docs-button {
    width: 34px;
    padding: 0;
  }

  .page-heading h1 {
    font-size: 19px;
  }

  .app-footer {
    flex-direction: column;
    gap: 5px;
  }
}
</style>
