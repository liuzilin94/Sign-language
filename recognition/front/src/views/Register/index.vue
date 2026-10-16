<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <div class="logo">
          <span class="logo-icon">🖐</span>
          <span class="logo-text">掌言手语</span>
        </div>
        <p>创建账号，开始学习手语</p>
      </div>
      
      <el-form ref="formRef" :model="form" :rules="rules" class="register-form">
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            size="large"
          >
            <template #prefix><el-icon><Phone /></el-icon></template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="code">
          <el-input
            v-model="form.code"
            placeholder="请输入验证码"
            size="large"
          >
            <template #prefix><el-icon><Key /></el-icon></template>
            <template #append>
              <el-button @click="sendCode" :disabled="countdown > 0">
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="设置登录密码（6位以上）"
            size="large"
          >
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
          >
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="agreement">
          <el-checkbox v-model="form.agreement">
            我已阅读并同意
            <router-link to="/agreement">《用户协议》</router-link>
            和
            <router-link to="/privacy">《隐私政策》</router-link>
          </el-checkbox>
        </el-form-item>
        
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handleRegister"
          class="register-btn"
        >
          注册
        </el-button>
      </el-form>
      
      <div class="register-footer">
        <span>已有账号？</span>
        <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store'
import { userApi } from '@/api'
import { Phone, Key, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const countdown = ref(0)

const form = reactive({
  phone: '',
  code: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

const validateConfirm = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次密码输入不一致'))
  } else {
    callback()
  }
}

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ],
  agreement: [
    { validator: (rule, value, callback) => {
      value ? callback() : callback(new Error('请勾选用户协议'))
    }, trigger: 'change' }
  ]
}

async function sendCode() {
  if (!form.phone || !/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning('请输入正确的手机号')
    return
  }
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) clearInterval(timer)
  }, 1000)
  ElMessage.success('验证码已发送')
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    const res = await userApi.register(form.phone, form.code, form.password)
    userStore.login(res.data)
    ElMessage.success('注册成功，欢迎加入！')
    router.push('/')
  } catch (e) {
    ElMessage.error('注册失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  
  .register-container {
    width: 100%;
    max-width: 400px;
    background: #fff;
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    
    .register-header {
      text-align: center;
      margin-bottom: 30px;
      
      .logo {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-bottom: 16px;
        
        .logo-icon { font-size: 36px; }
        .logo-text {
          font-size: 24px;
          font-weight: bold;
          color: #667eea;
        }
      }
      
      p {
        color: #666;
        font-size: 14px;
      }
    }
    
    .register-form {
      .el-form-item { margin-bottom: 20px; }
      
      a {
        color: #667eea;
        text-decoration: none;
      }
      
      .register-btn {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        
        &:hover { opacity: 0.9; }
      }
    }
    
    .register-footer {
      text-align: center;
      margin-top: 20px;
      font-size: 14px;
      color: #666;
      
      a {
        color: #667eea;
        text-decoration: none;
        margin-left: 4px;
      }
    }
  }
}
</style>
