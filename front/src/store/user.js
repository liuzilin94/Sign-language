import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

  const isLoggedIn = computed(() => !!token.value)

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUserInfo(info) {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  // 登录（调用真实API）
  async function login(phone, password) {
    try {
      const res = await authApi.login({ phone, password })
      setToken(res.data.token)
      setUserInfo(res.data.user_info)
      return res.data
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  // 注册（调用真实API）
  async function register(username, phone, password) {
    try {
      const res = await authApi.register({ username, phone, password })
      return res.data
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    }
  }

  // 退出登录
  function logout() {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  // 获取用户信息（从API）
  async function fetchUserInfo() {
    if (!token.value) return

    try {
      const res = await authApi.getMe()
      setUserInfo(res.data)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // Token失效时清空状态
      if (error.response?.status === 401) {
        logout()
      }
      throw error
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    setToken,
    setUserInfo,
    login,
    register,
    logout,
    fetchUserInfo
  }
})
