/**
 * Vite 构建与开发服务器配置。
 *
 * 核心能力：
 * 1. Vue 单文件组件编译。
 * 2. @ 别名指向 src，避免深层相对路径。
 * 3. 开发环境把 /api、/docs、/openapi.json 代理到 FastAPI，实现前后端同源联调。
 * 4. 构建输出到 dist，供 Nginx 容器托管。
 */
import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  // loadEnv 读取 .env / .env.development 等文件。
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://127.0.0.1:8000'

  const apiProxy = {
    target: proxyTarget,
    changeOrigin: true,
  }

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      strictPort: true,
      watch: {
        // 避免浏览器截图配置、构建临时文件、编辑器原子写入目录触发监听器
        // （Windows 下锁定的临时文件会抛 EBUSY）。
        ignored: [
          '**/.tmp/**',
          '**/.screenshots/**',
          '**/dist/**',
          '**/.*.tmpdir/**',
          '**/*.tmp',
        ],
      },
      proxy: {
        '/api': apiProxy,
        '/docs': apiProxy,
        '/redoc': apiProxy,
        '/openapi.json': apiProxy,
      },
    },
    preview: {
      port: 4173,
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
      chunkSizeWarningLimit: 1200,
      rollupOptions: {
        output: {
          // 把体积较大的依赖拆成独立 chunk，提升浏览器缓存利用率。
          manualChunks: {
            vue: ['vue', 'vue-router', 'pinia'],
            element: ['element-plus', '@element-plus/icons-vue'],
            http: ['axios'],
          },
        },
      },
    },
  }
})
