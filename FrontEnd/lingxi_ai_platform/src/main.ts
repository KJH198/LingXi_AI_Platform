import { createApp } from "vue";    // 引入 createApp用于创建应用
import App from "./App.vue";        // 引入 App 根组件
import ElementPlus from 'element-plus'  // 引入 Element Plus
import 'element-plus/dist/index.css'    // 引入 Element Plus 样式
import * as ElementPlusIconsVue from '@element-plus/icons-vue'  // 引入所有图标
import type { Component } from 'vue'  // 引入 Component 类型
import router from './router'  // 引入路由配置

// 引入 Vue Flow 样式
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const app = createApp(App)  // 创建应用实例

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component as Component)
}

app.use(ElementPlus)  // 使用 Element Plus
app.use(router)      // 使用路由
app.mount("#app")     // 挂载应用