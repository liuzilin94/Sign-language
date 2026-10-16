<template>
  <div class="login-page">
    <div class="login-panel">
      <div class="login-header">
        <router-link to="/" class="logo">
          <img src="/images/logo.png" alt="掌言" class="logo-img" />
          <span class="logo-text">掌言</span>
        </router-link>
        <h1 class="login-title">欢迎回来</h1>
        <p class="login-subtitle">登录你的账号</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @submit.prevent="handleLogin">
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="手机号"
            size="large"
            autocomplete="tel"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            autocomplete="current-password"
            show-password
          />
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handleLogin"
          class="login-btn"
          native-type="submit"
        >
          登录
        </el-button>
      </el-form>

      <p class="login-switch">
        没有账号？
        <router-link to="/register">注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { authApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ phone: '', password: '' })

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await authApi.login({ phone: form.phone, password: form.password })
    userStore.setToken(res.data.token)
    userStore.setUserInfo(res.data.user_info)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafaf8;
  padding: 32px 16px;

  .login-panel {
    width: 100%;
    max-width: 380px;
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 12px;
    padding: 40px 36px;

    .login-header {
      text-align: center;
      margin-bottom: 36px;

      .logo {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
        margin-bottom: 28px;

        .logo-img {
          height: 26px;
          width: auto;
        }

        .logo-text {
          font-size: 17px;
          font-weight: 600;
          letter-spacing: 0.3px;
        }
      }

      .login-title {
        font-size: 22px;
        font-weight: 600;
        color: #0d0d0d;
        margin: 0 0 6px;
        letter-spacing: -0.3px;
      }

      .login-subtitle {
        font-size: 14px;
        color: #8a8a8a;
        margin: 0;
      }
    }

    .login-form {
      .el-form-item {
        margin-bottom: 20px;
      }

      .el-input__wrapper {
        padding: 2px 14px;
      }

      .login-btn {
        width: 100%;
        height: 44px;
        font-size: 14px;
        font-weight: 500;
        letter-spacing: 0.3px;
        margin-top: 4px;
        border-radius: 6px;
      }
    }

    .login-switch {
      text-align: center;
      font-size: 13px;
      color: #8a8a8a;
      margin: 24px 0 0;

      a {
        color: #3a3a3a;
        font-weight: 500;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
}
</style>






