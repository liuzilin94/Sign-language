import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home/index.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register/index.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/dictionary',
    name: 'Dictionary',
    component: () => import('@/views/Dictionary/index.vue'),
    meta: { title: '手语词典' }
  },
  {
    path: '/dictionary/:id',
    name: 'WordDetail',
    component: () => import('@/views/Dictionary/WordDetail.vue'),
    meta: { title: '词汇详情' }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('@/views/Upload/index.vue'),
    meta: { title: '上传方言手语' }
  },
  {
    path: '/practice',
    name: 'Practice',
    component: () => import('@/views/Practice/index.vue'),
    meta: { title: '背词练习' }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/Tasks/index.vue'),
    meta: { title: '学习任务' }
  },
  {
    path: '/assessment',
    name: 'Assessment',
    component: () => import('@/views/Assessment/index.vue'),
    meta: { title: '学习测评' }
  },
  {
    path: '/avatar',
    name: 'Avatar',
    component: () => import('@/views/Avatar/index.vue'),
    meta: { title: '数字人手语演示' }
  },
  {
    path: '/data',
    name: 'Data',
    component: () => import('@/views/Data/index.vue'),
    meta: { title: '学习数据中心' }
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('@/views/Community/index.vue'),
    meta: { title: '社区动态' }
  },
  {
    path: '/achievements',
    name: 'Achievements',
    component: () => import('@/views/Achievements/index.vue'),
    meta: { title: '成就勋章' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile/index.vue'),
    meta: { title: '个人主页' }
  },
  {
    path: '/science',
    name: 'Science',
    component: () => import('@/views/Science/index.vue'),
    meta: { title: '手语科普' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings/index.vue'),
    meta: { title: '系统设置' }
  },
  {
    path: '/audit',
    name: 'Audit',
    component: () => import('@/views/Audit/index.vue'),
    meta: { title: '审核状态' }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('@/views/Messages/index.vue'),
    meta: { title: '消息中心' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 掌言手语` : '掌言手语学习平台'
  next()
})

export default router
