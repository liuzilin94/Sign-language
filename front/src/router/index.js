import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home/index.vue'),
    meta: { title: '首页', requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login/index.vue'),
    meta: { title: '登录', guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register/index.vue'),
    meta: { title: '注册', guestOnly: true }
  },
  {
    path: '/dictionary',
    name: 'Dictionary',
    component: () => import('@/views/Dictionary/index.vue'),
    meta: { title: '手语词典', requiresAuth: true }
  },
  {
    path: '/dictionary/:id',
    name: 'WordDetail',
    component: () => import('@/views/Dictionary/WordDetail.vue'),
    meta: { title: '词汇详情', requiresAuth: true }
  },
  {
    path: '/learning',
    name: 'Learning',
    component: () => import('@/views/Learning/index.vue'),
    meta: { title: '学习中心', requiresAuth: true }
  },
  {
    path: '/learning/session',
    name: 'LearningSession',
    component: () => import('@/views/Learning/Session.vue'),
    meta: { title: '学习会话', requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('@/views/Upload/index.vue'),
    meta: { title: '上传方言手语', requiresAuth: true }
  },
  {
    path: '/practice',
    name: 'Practice',
    component: () => import('@/views/Practice/index.vue'),
    meta: { title: '背词练习', requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/Tasks/index.vue'),
    meta: { title: '学习任务', requiresAuth: true }
  },
  {
    path: '/assessment',
    name: 'Assessment',
    component: () => import('@/views/Assessment/index.vue'),
    meta: { title: '学习测评', requiresAuth: true }
  },
  {
    path: '/avatar',
    name: 'Avatar',
    component: () => import('@/views/Avatar/index.vue'),
    meta: { title: '数字人手语演示', requiresAuth: false }
  },
  {
    path: '/data',
    name: 'Data',
    component: () => import('@/views/Data/index.vue'),
    meta: { title: '学习数据中心', requiresAuth: true }
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('@/views/Community/index.vue'),
    meta: { title: '社区动态', requiresAuth: true }
  },
  {
    path: '/achievements',
    name: 'Achievements',
    component: () => import('@/views/Achievements/index.vue'),
    meta: { title: '成就勋章', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile/index.vue'),
    meta: { title: '个人主页', requiresAuth: true }
  },
  {
    path: '/science',
    name: 'Science',
    component: () => import('@/views/Science/index.vue'),
    meta: { title: '手语科普', requiresAuth: false }
  },
  {
    path: '/science/:id',
    name: 'ArticleDetail',
    component: () => import('@/views/Science/ArticleDetail.vue'),
    meta: { title: '文章详情', requiresAuth: false }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings/index.vue'),
    meta: { title: '系统设置', requiresAuth: true }
  },
  {
    path: '/audit',
    name: 'Audit',
    component: () => import('@/views/Audit/index.vue'),
    meta: { title: '审核状态', requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('@/views/Messages/index.vue'),
    meta: { title: '消息中心', requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin/index.vue'),
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/arena',
    name: 'Arena',
    component: () => import('@/views/Arena/index.vue'),
    meta: { title: '竞技场', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} — 掌言` : '掌言'

  // 检查登录状态
  const userStore = useUserStore()

  // 如果需要认证
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }

    // 如果需要管理员权限
    if (to.meta.requiresAdmin) {
      if (userStore.userInfo?.role !== 'admin') {
        ElMessage.error('无权限访问，该页面仅限管理员')
        next('/')
        return
      }
    }

    // 如果已登录但用户信息未加载，等待加载完成
    if (!userStore.userInfo.id) {
      userStore.fetchUserInfo()
        .then(() => {
          // 加载成功，继续导航
          // 二次检查管理员权限（用户信息加载完成后）
          if (to.meta.requiresAdmin && userStore.userInfo?.role !== 'admin') {
            ElMessage.error('无权限访问，该页面仅限管理员')
            next('/')
            return
          }
          next()
        })
        .catch((error) => {
          console.error('获取用户信息失败:', error)
          userStore.logout()
          ElMessage.error('登录已过期，请重新登录')
          next('/login')
        })
      return // 等待异步操作完成
    }
  }

  // 如果是仅游客页面（登录/注册），且已登录，则重定向到首页
  if (to.meta.guestOnly && userStore.isLoggedIn) {
    next('/')
    return
  }

  next()
})

export default router
