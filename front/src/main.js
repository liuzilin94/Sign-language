import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/main.scss'
import { useLearnStore } from './store/learn'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 初始化 learnStore：从 localStorage 加载数据
const learnStore = useLearnStore()
learnStore.loadFromStorage()

app.mount('#app')
