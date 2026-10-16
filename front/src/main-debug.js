// 测试登录并打印详细步骤
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 调试用户store
const userStore = pinia.state.value.user

console.log('初始userStore:', userStore)

app.mount('#app')
