<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <div class="logo">
          <span class="logo-icon">🖐</span>
          <span class="logo-text">掌言手语</span>
        </div>
        <p>欢迎回来</p>
      </div>
      
      <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            size="large"
            prefix-icon="Phone"
          />
        </el-form-item>
        
        <el-form-item prop="code">
          <el-input
            v-model="form.code"
            placeholder="请输入验证码"
            size="large"
            prefix-icon="Key"
          >
            <template #append>
              <el-button @click="sendCode" :disabled="codeLoading || countdown > 0">
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <div class="extra-options">
          <el-checkbox v-model="form.remember">记住我</el-checkbox>
          <span class="forgot-link" @click="showForgotDialog = true">忘记密码？</span>
        </div>
        
        <el-button type="primary" size="large" :loading="loading" @click="handleLogin" class="login-btn">
          登录
        </el-button>
      </el-form>
      
      <div class="login-footer">
        <span>还没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </div>
      
      <div class="agreement">
        登录即代表同意
        <router-link to="/agreement">《用户协议》</router-link>
        和
        <router-link to="/privacy">《隐私政策》</router-link>
      </div>
    </div>
    
    <el-dialog v-model="showForgotDialog" title="找回密码" width="400px">
      <el-form ref="forgotFormRef" :model="forgotForm" :rules="forgotRules">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="forgotForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="forgotForm.password" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="验证码" prop="code">
          <el-input v-model="forgotForm.code" placeholder="请输入验证码">
            <template #append>
              <el-button @click="sendForgotCode" :disabled="forgotCountdown > 0">
                {{ forgotCountdown > 0 ? `${forgotCountdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForgotDialog = false">取消</el-button>
        <el-button type="primary" @click="handleForgot">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store'
import { userApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const forgotFormRef = ref(null)
const loading = ref(false)
const codeLoading = ref(false)
const countdown = ref(0)
const forgotCountdown = ref(0)
const showForgotDialog = ref(false)

const form = reactive({
  phone: '',
  code: '',
  remember: false
})

const forgotForm = reactive({
  phone: '',
  password: '',
  code: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
  ]
}

const forgotRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ]
}

async function sendCode() {
  if (!form.phone || !/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning('请输入正确的手机号')
    return
  }
  codeLoading.value = true
  await new Promise(r => setTimeout(r, 500))
  codeLoading.value = false
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) clearInterval(timer)
  }, 1000)
  ElMessage.success('验证码已发送')
}

async function sendForgotCode() {
  if (!forgotForm.phone) {
    ElMessage.warning('请输入手机号')
    return
  }
  forgotCountdown.value = 60
  const timer = setInterval(() => {
    forgotCountdown.value--
    if (forgotCountdown.value <= 0) clearInterval(timer)
  }, 1000)
  ElMessage.success('验证码已发送')
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    const res = await userApi.login(form.phone, form.code)
    userStore.login(res.data)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    ElMessage.error('登录失败，请检查验证码')
  } finally {
    loading.value = false
  }
}

async function handleForgot() {
  const valid = await forgotFormRef.value.validate().catch(() => false)
  if (!valid) return
  ElMessage.success('密码重置成功')
  showForgotDialog.value = false
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  
  .login-container {
    width: 100%;
    max-width: 400px;
    background: #fff;
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    
    .login-header {
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
    
    .login-form {
      .el-form-item { margin-bottom: 20px; }
      
      .extra-options {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        
        .forgot-link {
          color: #667eea;
          cursor: pointer;
          font-size: 14px;
        }
      }
      
      .login-btn {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        
        &:hover {
          opacity: 0.9;
        }
      }
    }
    
    .login-footer {
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
    
    .agreement {
      text-align: center;
      margin-top: 16px;
      font-size: 12px;
      color: #999;
      
      a {
        color: #667eea;
        text-decoration: none;
      }
    }
  }
}
</style>
