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

const form = reactive({
  username: '',
  phone: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '2-20个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (r, v, cb) => v !== form.password ? cb(new Error('两次密码不一致')) : cb(),
      trigger: 'blur'
    }
  ],
  agreement: [
    {
      validator: (r, v, cb) => !v ? cb(new Error('请勾选同意')) : cb(),
      trigger: 'change'
    }
  ]
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await authApi.register({
      username: form.username,
      phone: form.phone,
      password: form.password
    })
    userStore.setToken(res.data.token)
    userStore.setUserInfo(res.data.user_info)
    ElMessage.success('注册成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-panel">
      <div class="panel-left">
        <div class="brand-content">
          <router-link to="/" class="brand-logo">
            <img src="/images/logo.png" alt="掌言" class="logo-img" />
            <span class="logo-text">掌言</span>
          </router-link>
          <h2 class="brand-headline">让无声的世界<br/>被看见</h2>
          <p class="brand-desc">
            连接听障人士与健听人士的桥梁。<br/>
            科学的词汇学习与 AI 识别技术，
            轻松掌握中国手语。
          </p>
          <div class="brand-values">
            <div class="value-item">
              <span class="value-dot"></span>
              <span>科学学习方法</span>
            </div>
            <div class="value-item">
              <span class="value-dot"></span>
              <span>AI 智能识别</span>
            </div>
            <div class="value-item">
              <span class="value-dot"></span>
              <span>免费开放使用</span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel-right">
        <div class="form-container">
          <div class="form-header">
            <h1>创建账号</h1>
            <p>加入掌言</p>
          </div>

          <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="2-20个字符" clearable />
            </el-form-item>

            <el-form-item label="手机号" prop="phone">
              <el-input v-model="form.phone" placeholder="11位手机号" maxlength="11" clearable />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input v-model="form.confirmPassword" type="password" placeholder="再次输入密码" show-password />
            </el-form-item>

            <el-form-item prop="agreement">
              <el-checkbox v-model="form.agreement">
                同意 <el-link type="default" href="#">用户协议</el-link> 和 <el-link type="default" href="#">隐私政策</el-link>
              </el-checkbox>
            </el-form-item>

            <el-button type="primary" size="large" :loading="loading" @click="handleRegister" class="register-btn">
              注册
            </el-button>

            <p class="form-switch">
              已有账号？<router-link to="/login">登录</router-link>
            </p>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafaf8;
  padding: 32px 16px;
}

.register-panel {
  display: flex;
  width: 100%;
  max-width: 900px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
  min-height: 560px;
}

.panel-left {
  flex: 1;
  background: #0d0d0d;
  padding: 48px;
  display: flex;
  align-items: center;

  .brand-content {
    .brand-logo {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      margin-bottom: 48px;

      .logo-img {
        height: 26px;
        width: auto;
      }

      .logo-text {
        font-size: 17px;
        font-weight: 600;
        color: #fff;
      }
    }

    .brand-headline {
      font-size: 32px;
      font-weight: 700;
      color: #fff;
      line-height: 1.2;
      letter-spacing: -0.5px;
      margin: 0 0 20px;
    }

    .brand-desc {
      font-size: 14px;
      line-height: 1.7;
      color: rgba(255, 255, 255, 0.45);
      margin: 0 0 36px;
    }

    .brand-values {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .value-item {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 14px;
        color: rgba(255, 255, 255, 0.7);

        .value-dot {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: #fff;
          opacity: 0.5;
        }
      }
    }
  }
}

.panel-right {
  flex: 1;
  padding: 48px;
  display: flex;
  align-items: center;
  justify-content: center;

  .form-container {
    width: 100%;
    max-width: 320px;

    .form-header {
      margin-bottom: 32px;

      h1 {
        font-size: 22px;
        font-weight: 600;
        color: #0d0d0d;
        margin: 0 0 6px;
        letter-spacing: -0.3px;
      }

      p {
        font-size: 14px;
        color: #8a8a8a;
        margin: 0;
      }
    }

    .el-form-item {
      margin-bottom: 16px;
    }

    .el-form-item__label {
      font-size: 13px;
      font-weight: 500;
      color: #3a3a3a;
      padding-bottom: 6px;
    }

    .el-input__wrapper {
      padding: 2px 14px;
    }

    .register-btn {
      width: 100%;
      height: 44px;
      font-size: 14px;
      font-weight: 500;
      margin-top: 8px;
      border-radius: 6px;
    }

    .form-switch {
      text-align: center;
      font-size: 13px;
      color: #8a8a8a;
      margin: 20px 0 0;

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

@media (max-width: 768px) {
  .register-panel {
    flex-direction: column;
    max-width: 440px;
  }

  .panel-left {
    padding: 32px 24px;
    min-height: auto;

    .brand-content {
      .brand-logo {
        margin-bottom: 24px;
      }

      .brand-headline {
        font-size: 24px;
        margin-bottom: 12px;
      }

      .brand-desc {
        margin-bottom: 20px;
      }

      .brand-values {
        display: none;
      }
    }
  }

  .panel-right {
    padding: 32px 24px;
  }
}
</style>
