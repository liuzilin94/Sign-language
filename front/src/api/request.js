/**
 * 统一的 Axios 请求实例
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

// 创建axios实例
const isProduction = import.meta.env.PROD
// 生产环境使用相对路径，让Nginx代理到后端
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    try {
      const userStore = useUserStore()
      if (userStore.token) {
        config.headers.Authorization = `Bearer ${userStore.token}`
      }
    } catch (e) {
      // Pinia store 可能在初始化前被调用，忽略错误
    }
    // FormData 不设置 Content-Type，让浏览器自动添加 multipart/form-data + boundary
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json'
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const { response } = error
    if (response) {
      const { data, status } = response
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        try {
          const userStore = useUserStore()
          userStore.logout()
          location.href = '/login'
        } catch (e) {
          // 忽略错误
        }
      } else if (data?.message) {
        ElMessage.error(data.message)
      }
    } else {
      ElMessage.error('网络错误，请检查后端服务')
    }
    return Promise.reject(error)
  }
)

export { api }
