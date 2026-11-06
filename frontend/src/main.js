/**
 * 前端应用入口。
 *
 * 初始化顺序：
 * 1. Pinia 全局状态（API 健康状态等）。
 * 2. Vue Router（页面与布局）。
 * 3. Element Plus（中文语言包）。
 * 4. 自定义全局样式（在 Element 样式之后导入，确保可以覆盖主题变量）。
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import 'element-plus/dist/index.css'
import '@/styles/index.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
