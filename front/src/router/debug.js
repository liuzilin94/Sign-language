// 调试路由守卫问题
console.log('路由文件加载')

import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

console.log('useUserStore在模块顶层调用:', typeof useUserStore)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home/index.vue'),
    meta: { title: '首页', requiresAuth: false }
  },
  // ... 其他路由
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  console.log('路由守卫触发:', to.path, 'from:', from.path)
  
  // 延迟一点让store初始化
  setTimeout(() => {
    const userStore = useUserStore()
    console.log('userStore状态:', {
      token: userStore.token ? userStore.token.substring(0, 20) + '...' : 'empty',
      userInfo: userStore.userInfo,
      isLoggedIn: userStore.isLoggedIn
    })

    // 如果需要认证
    if (to.meta.requiresAuth) {
      if (!userStore.isLoggedIn) {
        console.log('需要认证，但未登录，跳转到登录页')
        ElMessage.warning('请先登录')
        next('/login')
        return
      }

      // 如果已登录但用户信息未加载，尝试加载
      if (!userStore.userInfo.id) {
        console.log('已登录但用户信息为空，尝试获取用户信息')
        userStore.fetchUserInfo().catch(() => {
          console.log('获取用户信息失败')
        })
      }
    }

    // 如果是仅游客页面（登录/注册），且已登录，则重定向到首页
    if (to.meta.guestOnly && userStore.isLoggedIn) {
      console.log('游客页面但已登录，跳转到首页')
      next('/')
      return
    }

    console.log('路由放行')
    next()
  }, 100)
})

export default router
