<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>系统设置</h2>
    </div>
    
    <div class="settings-section">
      <h3>界面设置</h3>
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-label">悬浮球</span>
          <span class="setting-desc">显示 AI 助手悬浮球</span>
        </div>
        <el-switch v-model="settings.floatingBall" />
      </div>
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-label">消息通知</span>
          <span class="setting-desc">接收学习提醒和系统通知</span>
        </div>
        <el-switch v-model="settings.notifications" />
      </div>
    </div>
    
    <div class="settings-section">
      <h3>播放设置</h3>
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-label">自动播放</span>
          <span class="setting-desc">进入页面自动播放视频</span>
        </div>
        <el-switch v-model="settings.autoPlay" />
      </div>
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-label">默认倍速</span>
          <span class="setting-desc">视频默认播放速度</span>
        </div>
        <el-select v-model="settings.defaultSpeed" style="width: 100px">
          <el-option label="0.5x" :value="0.5" />
          <el-option label="0.75x" :value="0.75" />
          <el-option label="1x" :value="1" />
          <el-option label="1.25x" :value="1.25" />
          <el-option label="1.5x" :value="1.5" />
          <el-option label="2x" :value="2" />
        </el-select>
      </div>
    </div>
    
    <div class="settings-section">
      <h3>存储设置</h3>
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-label">离线视频质量</span>
          <span class="setting-desc">下载视频的清晰度</span>
        </div>
        <el-select v-model="settings.downloadQuality" style="width: 100px">
          <el-option label="流畅" value="low" />
          <el-option label="标清" value="medium" />
          <el-option label="高清" value="high" />
        </el-select>
      </div>
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-label">清理缓存</span>
          <span class="setting-desc">清除本地缓存数据</span>
        </div>
        <el-button @click="clearCache">清理</el-button>
      </div>
    </div>
    
    <div class="settings-section">
      <h3>账号安全</h3>
      <div class="setting-item clickable" @click="showChangePhoneDialog">
        <div class="setting-info">
          <span class="setting-label">修改手机号</span>
          <span class="setting-desc">{{ userInfo.phone || '未绑定' }}</span>
        </div>
        <el-icon><ArrowRight /></el-icon>
      </div>
      <div class="setting-item clickable" @click="showChangePasswordDialog">
        <div class="setting-info">
          <span class="setting-label">修改密码</span>
          <span class="setting-desc">定期修改密码保护账号安全</span>
        </div>
        <el-icon><ArrowRight /></el-icon>
      </div>
      <div class="setting-item clickable" @click="showBindWechatDialog">
        <div class="setting-info">
          <span class="setting-label">绑定微信</span>
          <span class="setting-desc">{{ userInfo.wechatBound ? '已绑定' : '绑定后可用微信登录' }}</span>
        </div>
        <el-icon><ArrowRight /></el-icon>
      </div>
    </div>
    
    <div class="settings-section">
      <h3>关于</h3>
      <div class="setting-item">
        <div class="setting-info">
          <span class="setting-label">当前版本</span>
          <span class="setting-desc">掌言手语学习平台</span>
        </div>
        <span class="version">v1.0.0</span>
      </div>
      <div class="setting-item clickable" @click="$router.push('/agreement')">
        <div class="setting-info">
          <span class="setting-label">用户协议</span>
        </div>
        <el-icon><ArrowRight /></el-icon>
      </div>
      <div class="setting-item clickable" @click="$router.push('/privacy')">
        <div class="setting-info">
          <span class="setting-label">隐私政策</span>
        </div>
        <el-icon><ArrowRight /></el-icon>
      </div>
    </div>
    
    <div class="logout-section">
      <el-button type="danger" size="large" @click="logout">退出登录</el-button>
    </div>
    
    <el-dialog v-model="changePhoneDialogVisible" title="修改手机号" width="400px">
      <el-form :model="phoneForm" label-width="80px">
        <el-form-item label="新手机号">
          <el-input v-model="phoneForm.phone" placeholder="请输入新手机号" />
        </el-form-item>
        <el-form-item label="验证码">
          <el-input v-model="phoneForm.code" placeholder="请输入验证码">
            <template #append>
              <el-button @click="sendCode" :disabled="phoneCodeCountdown > 0">
                {{ phoneCodeCountdown > 0 ? `${phoneCodeCountdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePhoneDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="changePhone">确认修改</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="changePasswordDialogVisible" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="原密码">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePasswordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="changePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore, useSettingsStore } from '@/store'

const router = useRouter()
const userStore = useUserStore()
const settingsStore = useSettingsStore()

const settings = reactive({
  floatingBall: true,
  notifications: true,
  autoPlay: false,
  defaultSpeed: 1,
  downloadQuality: 'high'
})

const userInfo = reactive({
  phone: '138****8888',
  wechatBound: false
})

const changePhoneDialogVisible = ref(false)
const changePasswordDialogVisible = ref(false)
const phoneCodeCountdown = ref(0)

const phoneForm = reactive({
  phone: '',
  code: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

function showChangePhoneDialog() {
  changePhoneDialogVisible.value = true
}

function showChangePasswordDialog() {
  changePasswordDialogVisible.value = true
}

function showBindWechatDialog() {
  ElMessage.info('微信绑定功能开发中')
}

function sendCode() {
  phoneCodeCountdown.value = 60
  const timer = setInterval(() => {
    phoneCodeCountdown.value--
    if (phoneCodeCountdown.value <= 0) clearInterval(timer)
  }, 1000)
  ElMessage.success('验证码已发送')
}

function changePhone() {
  if (!phoneForm.phone || !phoneForm.code) {
    ElMessage.warning('请填写完整信息')
    return
  }
  ElMessage.success('手机号修改成功')
  changePhoneDialogVisible.value = false
}

function changePassword() {
  if (!passwordForm.oldPassword || !passwordForm.newPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次密码输入不一致')
    return
  }
  ElMessage.success('密码修改成功')
  changePasswordDialogVisible.value = false
}

function clearCache() {
  ElMessageBox.confirm('确定清除所有缓存数据吗？这不会影响您的账号数据。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    settingsStore.clearCache()
    ElMessage.success('缓存清理成功')
  }).catch(() => {})
}

function logout() {
  ElMessageBox.confirm('确定退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  }).catch(() => {})
}
</script>

<style scoped lang="scss">
.settings-page {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 130px);
  
  .page-header {
    margin-bottom: 24px;
    
    h2 {
      font-size: 24px;
      color: #333;
    }
  }
  
  .settings-section {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    
    h3 {
      font-size: 14px;
      color: #999;
      margin-bottom: 16px;
    }
    
    .setting-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      &.clickable {
        cursor: pointer;
        
        &:hover {
          background: #f9fafb;
          margin: 0 -20px;
          padding-left: 20px;
          padding-right: 20px;
        }
      }
      
      .setting-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
        
        .setting-label {
          color: #333;
          font-size: 15px;
        }
        
        .setting-desc {
          font-size: 12px;
          color: #999;
        }
      }
      
      .version {
        color: #999;
        font-size: 14px;
      }
      
      .el-icon {
        color: #999;
      }
    }
  }
  
  .logout-section {
    padding: 20px 0;
    
    .el-button {
      width: 100%;
    }
  }
}
</style>
