/**
 * 前端路由配置。
 *
 * 采用嵌套路由：
 * - 根路径使用 MainLayout 提供侧边栏与顶栏；
 * - 子页面只关注业务内容；
 * - 使用动态 import 做路由级代码分割。
 */
import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: {
          title: '平台总览',
          subtitle: '数据、因子、模型与回测的统一研究底座',
        },
      },
      {
        path: 'stocks',
        name: 'stocks',
        component: () => import('@/views/StocksView.vue'),
        meta: {
          title: '股票池',
          subtitle: '浏览股票静态资料、交易所与行业分布',
        },
      },
      {
        path: 'system',
        name: 'system',
        component: () => import('@/views/SystemView.vue'),
        meta: {
          title: '系统状态',
          subtitle: '运行环境、依赖就绪度与 API 能力矩阵',
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  const pageTitle = to.meta?.title
  document.title = pageTitle ? `${pageTitle} · AlphaHunter` : 'AlphaHunter'
})

export default router
