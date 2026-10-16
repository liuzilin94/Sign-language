<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>系统设置</h1>
      <p class="subtitle">个性化你的学习体验</p>
    </div>

    <!-- Tabs -->
    <div class="settings-container">
      <div class="settings-nav">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          class="nav-item"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <el-icon><component :is="tab.icon" /></el-icon>
          <span>{{ tab.label }}</span>
        </div>
      </div>

      <div class="settings-content">
        <!-- Interface Tab -->
        <div v-if="activeTab === 'interface'" class="settings-panel">
          <h2>界面设置</h2>

          <div class="setting-group">
            <div class="setting-item">
              <div class="setting-info">
                <h3>悬浮球</h3>
                <p>在页面右下角显示快捷操作悬浮球</p>
              </div>
              <el-switch v-model="settings.floatingBall" @change="saveSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>深色模式</h3>
                <p>开启后使用深色主题显示</p>
              </div>
              <el-switch v-model="settings.darkMode" @change="saveSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>页面动画</h3>
                <p>开启页面切换和元素动画效果</p>
              </div>
              <el-switch v-model="settings.animations" @change="saveSettings" />
            </div>
          </div>

          <div class="setting-group">
            <h3>显示设置</h3>
            <div class="setting-item">
              <div class="setting-info">
                <h3>每页显示数量</h3>
                <p>列表和卡片每页显示的内容数量</p>
              </div>
              <el-select v-model="settings.pageSize" @change="saveSettings">
                <el-option label="10条" :value="10" />
                <el-option label="20条" :value="20" />
                <el-option label="30条" :value="30" />
                <el-option label="50条" :value="50" />
              </el-select>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>卡片视图</h3>
                <p>选择内容列表的显示方式</p>
              </div>
              <el-radio-group v-model="settings.cardView" @change="saveSettings">
                <el-radio label="grid">网格</el-radio>
                <el-radio label="list">列表</el-radio>
              </el-radio-group>
            </div>
          </div>
        </div>

        <!-- Notification Tab -->
        <div v-if="activeTab === 'notification'" class="settings-panel">
          <h2>通知设置</h2>

          <div class="setting-group">
            <h3>消息通知</h3>
            <div class="setting-item">
              <div class="setting-info">
                <h3>系统通知</h3>
                <p>接收系统公告和重要提醒</p>
              </div>
              <el-switch v-model="settings.notifications.system" @change="saveSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>互动通知</h3>
                <p>接收点赞、评论、关注等互动提醒</p>
              </div>
              <el-switch v-model="settings.notifications.interaction" @change="saveSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>复习提醒</h3>
                <p>根据艾宾浩斯曲线提醒复习</p>
              </div>
              <el-switch v-model="settings.notifications.review" @change="saveSettings" />
            </div>
          </div>

          <div class="setting-group">
            <h3>提醒时间</h3>
            <div class="setting-item">
              <div class="setting-info">
                <h3>每日提醒时间</h3>
                <p>设置每日学习提醒的时间</p>
              </div>
              <el-time-picker
                v-model="settings.reminderTime"
                format="HH:mm"
                value-format="HH:mm"
                @change="saveSettings"
              />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>提醒方式</h3>
                <p>选择接收提醒的方式</p>
              </div>
              <el-checkbox-group v-model="settings.reminderMethods" @change="saveSettings">
                <el-checkbox label="app">应用内通知</el-checkbox>
                <el-checkbox label="email">邮件通知</el-checkbox>
                <el-checkbox label="sms">短信通知</el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </div>

        <!-- Playback Tab -->
        <div v-if="activeTab === 'playback'" class="settings-panel">
          <h2>播放设置</h2>

          <div class="setting-group">
            <h3>视频播放</h3>
            <div class="setting-item">
              <div class="setting-info">
                <h3>自动播放</h3>
                <p>进入页面时自动播放视频</p>
              </div>
              <el-switch v-model="settings.autoplay" @change="saveSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>默认播放速度</h3>
                <p>视频的默认播放倍速</p>
              </div>
              <el-select v-model="settings.defaultSpeed" @change="saveSettings">
                <el-option label="0.5x" :value="0.5" />
                <el-option label="0.75x" :value="0.75" />
                <el-option label="正常" :value="1" />
                <el-option label="1.25x" :value="1.25" />
                <el-option label="1.5x" :value="1.5" />
              </el-select>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>循环播放</h3>
                <p>视频播完后自动重新播放</p>
              </div>
              <el-switch v-model="settings.loopPlayback" @change="saveSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>画质选择</h3>
                <p>视频播放的默认画质</p>
              </div>
              <el-select v-model="settings.videoQuality" @change="saveSettings">
                <el-option label="自动" value="auto" />
                <el-option label="1080p" value="1080p" />
                <el-option label="720p" value="720p" />
                <el-option label="480p" value="480p" />
              </el-select>
            </div>
          </div>

          <div class="setting-group">
            <h3>摄像头设置</h3>
            <div class="setting-item">
              <div class="setting-info">
                <h3>默认摄像头</h3>
                <p>选择练习时使用的摄像头</p>
              </div>
              <el-select v-model="settings.defaultCamera" @change="saveSettings">
                <el-option label="前置摄像头" value="front" />
                <el-option label="后置摄像头" value="back" />
              </el-select>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>录制画质</h3>
                <p>练习视频录制的质量</p>
              </div>
              <el-select v-model="settings.recordQuality" @change="saveSettings">
                <el-option label="高清 (720p)" value="720p" />
                <el-option label="标清 (480p)" value="480p" />
              </el-select>
            </div>
          </div>
        </div>

        <!-- Account Tab -->
        <div v-if="activeTab === 'account'" class="settings-panel">
          <h2>账号设置</h2>

          <div class="account-info">
            <div class="avatar-section">
              <el-avatar :src="userInfo.avatar" :size="100">
                {{ userInfo.name?.charAt(0) }}
              </el-avatar>
              <el-button size="small" @click="changeAvatar">更换头像</el-button>
            </div>
            <div class="account-details">
              <div class="detail-row">
                <span class="label">用户名</span>
                <span class="value">{{ userInfo.name || '未设置' }}</span>
                <el-button text size="small" @click="editUsername">修改</el-button>
              </div>
              <div class="detail-row">
                <span class="label">手机号</span>
                <span class="value">{{ userInfo.phone || '未绑定' }}</span>
                <el-button text size="small" @click="changePhone">
                  {{ userInfo.phone ? '更换' : '绑定' }}
                </el-button>
              </div>
              <div class="detail-row">
                <span class="label">账号注册时间</span>
                <span class="value">{{ userInfo.registerDate }}</span>
              </div>
            </div>
          </div>

          <div class="setting-group">
            <h3>账号安全</h3>
            <div class="setting-item">
              <div class="setting-info">
                <h3>修改密码</h3>
                <p>定期修改密码可以保护账号安全</p>
              </div>
              <el-button @click="changePassword">修改密码</el-button>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>两步验证</h3>
                <p>开启后登录需要输入手机验证码</p>
              </div>
              <el-switch v-model="settings.twoFactor" @change="saveSettings" />
            </div>
          </div>

          <div class="setting-group danger-zone">
            <h3>危险操作</h3>
            <div class="setting-item">
              <div class="setting-info">
                <h3>清除缓存</h3>
                <p>清除本地存储的缓存数据</p>
              </div>
              <el-button @click="clearCache">清除缓存</el-button>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>账号注销</h3>
                <p>永久删除账号及所有相关数据，此操作不可恢复</p>
              </div>
              <el-button type="danger" @click="deleteAccount">注销账号</el-button>
            </div>
          </div>
        </div>

        <!-- Learning Tab -->
        <div v-if="activeTab === 'learning'" class="settings-panel">
          <h2>学习设置</h2>

          <div class="setting-group">
            <h3>每日目标</h3>
            <div class="setting-item">
              <div class="setting-info">
                <h3>每日新词数量</h3>
                <p>每天学习的新词汇数量</p>
              </div>
              <div class="number-input">
                <el-button
                  size="small"
                  :disabled="learningSettings.daily_new_words <= 1"
                  @click="decreaseNewWords"
                >-</el-button>
                <span class="number-value">{{ learningSettings.daily_new_words }}</span>
                <el-button
                  size="small"
                  :disabled="learningSettings.daily_new_words >= 20"
                  @click="increaseNewWords"
                >+</el-button>
              </div>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>每日复习词汇数量</h3>
                <p>每天需要复习的词汇数量</p>
              </div>
              <div class="number-input">
                <el-button
                  size="small"
                  :disabled="learningSettings.daily_review_words <= 1"
                  @click="decreaseReviewWords"
                >-</el-button>
                <span class="number-value">{{ learningSettings.daily_review_words }}</span>
                <el-button
                  size="small"
                  :disabled="learningSettings.daily_review_words >= 50"
                  @click="increaseReviewWords"
                >+</el-button>
              </div>
            </div>
          </div>

          <div class="setting-group">
            <el-button type="primary" @click="saveLearningSettings" :loading="savingSettings">
              保存设置
            </el-button>
          </div>
        </div>

        <!-- Level Tab -->
        <div v-if="activeTab === 'level'" class="settings-panel">
          <h2>等级与积分</h2>

          <!-- 等级卡片 -->
          <div class="level-card">
            <div class="level-badge">
              <div class="level-icon">
                <el-icon><Medal /></el-icon>
              </div>
              <div class="level-number">Lv.{{ levelInfo.level }}</div>
            </div>
            <div class="level-progress-section">
              <div class="level-title">
                <span>距离下一级</span>
                <span class="points-info">{{ levelInfo.points }} / {{ levelInfo.next_level_points }} 积分</span>
              </div>
              <el-progress
                :percentage="levelInfo.progress_percent"
                :stroke-width="12"
                :show-text="false"
                :color="levelProgressColor"
              />
              <div class="level-hint">
                再获得 {{ levelInfo.total_needed - levelInfo.progress }} 积分即可升级
              </div>
            </div>
          </div>

          <!-- 积分规则 -->
          <div class="setting-group">
            <h3>积分获取途径</h3>
            <div class="points-rules">
              <div class="rule-item">
                <div class="rule-icon arena">
                  <el-icon><Trophy /></el-icon>
                </div>
                <div class="rule-content">
                  <h4>竞技场挑战</h4>
                  <p>答对1题 = 1积分</p>
                </div>
              </div>
              <div class="rule-item">
                <div class="rule-icon learning">
                  <el-icon><Reading /></el-icon>
                </div>
                <div class="rule-content">
                  <h4>日常学习</h4>
                  <p>完成新词学习 = 2积分，完成复习 = 1积分</p>
                </div>
              </div>
              <div class="rule-item">
                <div class="rule-icon community">
                  <el-icon><ChatDotRound /></el-icon>
                </div>
                <div class="rule-content">
                  <h4>社区互动</h4>
                  <p>发布动态 = 3积分，发帖被点赞 = 1积分</p>
                </div>
              </div>
              <div class="rule-item">
                <div class="rule-icon dialect">
                  <el-icon><Upload /></el-icon>
                </div>
                <div class="rule-content">
                  <h4>贡献方言手语</h4>
                  <p>上传方言视频并通过审核 = 10积分</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 等级特权 -->
          <div class="setting-group">
            <h3>等级特权</h3>
            <div class="privileges-list">
              <div class="privilege-item" :class="{ unlocked: levelInfo.level >= 1 }">
                <span class="privilege-icon">🏆</span>
                <span class="privilege-text">Lv.1 解锁：基础学习功能</span>
              </div>
              <div class="privilege-item" :class="{ unlocked: levelInfo.level >= 5 }">
                <span class="privilege-icon">⭐</span>
                <span class="privilege-text">Lv.5 解锁：自定义头像框</span>
              </div>
              <div class="privilege-item" :class="{ unlocked: levelInfo.level >= 10 }">
                <span class="privilege-icon">🎨</span>
                <span class="privilege-text">Lv.10 解锁：高级学习统计</span>
              </div>
              <div class="privilege-item" :class="{ unlocked: levelInfo.level >= 20 }">
                <span class="privilege-icon">💎</span>
                <span class="privilege-text">Lv.20 解锁：专属称号</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Password Dialog -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="savePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import {
  Monitor,
  Bell,
  VideoPlay,
  User,
  Setting,
  Reading,
  Medal,
  Trophy,
  ChatDotRound,
  Upload
} from '@element-plus/icons-vue'

import { learningApi } from '@/api/learning'
import { pointsApi } from '@/api'
import { useSettingsStore } from '@/store/settings'

const userStore = useUserStore()
const settingsStore = useSettingsStore()

const activeTab = ref('interface')
const showPasswordDialog = ref(false)

const tabs = [
  { key: 'interface', label: '界面', icon: 'Monitor' },
  { key: 'notification', label: '通知', icon: 'Bell' },
  { key: 'playback', label: '播放', icon: 'VideoPlay' },
  { key: 'account', label: '账号', icon: 'User' },
  { key: 'learning', label: '学习', icon: 'Reading' },
  { key: 'level', label: '等级', icon: 'Medal' }
]

const settings = reactive({
  floatingBall: true,
  darkMode: false,
  animations: true,
  pageSize: 20,
  cardView: 'grid',
  notifications: {
    system: true,
    interaction: true,
    review: true
  },
  reminderTime: '09:00',
  reminderMethods: ['app'],
  autoplay: false,
  defaultSpeed: 1,
  loopPlayback: true,
  videoQuality: 'auto',
  defaultCamera: 'front',
  recordQuality: '720p',
  twoFactor: false
})

const userInfo = ref({
  name: '',
  avatar: '',
  phone: '',
  registerDate: ''
})

const loadingUserInfo = ref(false)

async function loadUserInfo() {
  try {
    loadingUserInfo.value = true
    await userStore.fetchUserInfo()
    const info = userStore.userInfo
    if (info) {
      userInfo.value = {
        name: info.username || '',
        avatar: info.avatar_url || '',
        phone: info.phone ? info.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '',
        registerDate: info.created_at ? info.created_at.split('T')[0] : ''
      }
    }
  } catch (e) {
    console.error('加载用户信息失败:', e)
  } finally {
    loadingUserInfo.value = false
  }
}

const learningSettings = ref({
  daily_new_words: 3,
  daily_review_words: 5
})

const savingSettings = ref(false)

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 等级信息
const levelInfo = ref({
  level: 1,
  points: 0,
  current_level_points: 0,
  next_level_points: 100,
  progress: 0,
  total_needed: 100,
  progress_percent: 0
})

const levelProgressColor = computed(() => {
  if (levelInfo.value.progress_percent >= 80) return '#67c23a'
  if (levelInfo.value.progress_percent >= 50) return '#409eff'
  return '#e6a23c'
})

// 加载等级信息
async function loadLevelInfo() {
  try {
    const res = await pointsApi.getLevelInfo()
    if (res.code === 200 && res.data) {
      levelInfo.value = res.data
    }
  } catch (e) {
    console.error('加载等级信息失败:', e)
  }
}

function saveSettings() {
  localStorage.setItem('appSettings', JSON.stringify(settings))
  ElMessage.success('设置已保存')
}

function loadSettings() {
  const saved = localStorage.getItem('appSettings')
  if (saved) {
    const parsed = JSON.parse(saved)
    Object.assign(settings, parsed)
  }
}

// 加载学习设置
async function loadLearningSettings() {
  try {
    // 先从 store 获取缓存
    if (settingsStore.learningSettings.daily_new_words > 0) {
      learningSettings.value.daily_new_words = settingsStore.learningSettings.daily_new_words
      learningSettings.value.daily_review_words = settingsStore.learningSettings.daily_review_words
    }
    // 同时从 API 获取最新数据
    const res = await learningApi.getSettings()
    if (res.data) {
      learningSettings.value.daily_new_words = res.data.daily_new_words || 3
      learningSettings.value.daily_review_words = res.data.daily_review_words || 5
      // 同步到 store
      settingsStore.learningSettings.daily_new_words = res.data.daily_new_words || 3
      settingsStore.learningSettings.daily_review_words = res.data.daily_review_words || 5
    }
  } catch (e) {
    console.error('加载学习设置失败:', e)
  }
}

function changeAvatar() {
  ElMessage.info('头像上传功能')
}

function editUsername() {
  ElMessage.info('用户名修改功能')
}

function changePhone() {
  ElMessage.info('手机号绑定功能')
}

function changePassword() {
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  showPasswordDialog.value = true
}

async function savePassword() {
  if (!passwordForm.value.oldPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!passwordForm.value.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  ElMessage.success('密码修改成功')
  showPasswordDialog.value = false
}

function increaseNewWords() {
  if (learningSettings.value.daily_new_words < 20) {
    learningSettings.value.daily_new_words++
  }
}

function decreaseNewWords() {
  if (learningSettings.value.daily_new_words > 1) {
    learningSettings.value.daily_new_words--
  }
}

function increaseReviewWords() {
  if (learningSettings.value.daily_review_words < 50) {
    learningSettings.value.daily_review_words++
  }
}

function decreaseReviewWords() {
  if (learningSettings.value.daily_review_words > 1) {
    learningSettings.value.daily_review_words--
  }
}

async function saveLearningSettings() {
  try {
    savingSettings.value = true
    const success = await settingsStore.saveLearningSettings({
      daily_new_words: learningSettings.value.daily_new_words,
      daily_review_words: learningSettings.value.daily_review_words
    })
    if (success) {
      ElMessage.success('学习设置已保存，立即生效')
    } else {
      ElMessage.error('保存失败，请重试')
    }
  } catch (e) {
    console.error('保存学习设置失败:', e)
    ElMessage.error('保存失败，请重试')
  } finally {
    savingSettings.value = false
  }
}

async function clearCache() {
  await ElMessageBox.confirm('确定要清除缓存吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  })

  localStorage.clear()
  ElMessage.success('缓存已清除')
}

async function deleteAccount() {
  await ElMessageBox.confirm(
    '确定要注销账号吗？此操作将永久删除所有数据，且不可恢复！',
    '危险操作',
    {
      confirmButtonText: '确定注销',
      cancelButtonText: '取消',
      type: 'error'
    }
  )

  await ElMessageBox.confirm(
    '这是最后一次确认，注销后所有数据将无法恢复！',
    '再次确认',
    {
      confirmButtonText: '确认注销',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )

  ElMessage.success('账号已提交注销申请')
}

onMounted(() => {
  loadSettings()
  loadLearningSettings()
  loadUserInfo()
  loadLevelInfo()
})
</script>

<style scoped>
.settings-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 48px 32px 80px;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #0d0d0d;
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #8a8a8a;
}

/* Settings Container */
.settings-container {
  display: flex;
  gap: 24px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
}

.settings-nav {
  width: 200px;
  background: #fafaf8;
  padding: 24px 16px;
  flex-shrink: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  color: #8a8a8a;
  transition: all 180ms ease;
  margin-bottom: 4px;
}

.nav-item:hover {
  background: #f0f0ee;
  color: #0d0d0d;
}

.nav-item.active {
  background: #0d0d0d;
  color: #fff;
}

.nav-item .el-icon {
  font-size: 18px;
}

.settings-content {
  flex: 1;
  padding: 32px;
  min-height: 600px;
}

.settings-panel h2 {
  font-size: 20px;
  font-weight: 700;
  color: #0d0d0d;
  margin-bottom: 32px;
}

.setting-group {
  margin-bottom: 32px;
}

.setting-group h3 {
  font-size: 14px;
  font-weight: 600;
  color: #8a8a8a;
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0ee;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info h3 {
  font-size: 15px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 4px;
}

.setting-info p {
  font-size: 13px;
  color: #8a8a8a;
  margin: 0;
}

/* Account Info */
.account-info {
  display: flex;
  gap: 32px;
  padding: 24px;
  background: #fafaf8;
  border-radius: 10px;
  margin-bottom: 32px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.account-details {
  flex: 1;
}

.detail-row {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0ee;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  width: 120px;
  font-size: 14px;
  color: #8a8a8a;
}

.detail-row .value {
  flex: 1;
  font-size: 14px;
  color: #0d0d0d;
}

/* Number Input for Learning Settings */
.number-input {
  display: flex;
  align-items: center;
  gap: 8px;

  .el-button {
    width: 32px;
    height: 32px;
    padding: 0;
    font-size: 16px;
    font-weight: 600;
  }

  .number-value {
    min-width: 40px;
    text-align: center;
    font-size: 18px;
    font-weight: 600;
    color: #0d0d0d;
  }
}

.danger-zone {
  padding-top: 24px;
  border-top: 1px solid #f0f0ee;
}

.danger-zone h3 {
  color: #f56c6c;
}

/* Level Card */
.level-card {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 28px;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border-radius: 12px;
  margin-bottom: 32px;

  .level-badge {
    text-align: center;
    flex-shrink: 0;

    .level-icon {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 8px;

      .el-icon {
        font-size: 36px;
        color: #fff;
      }
    }

    .level-number {
      font-size: 18px;
      font-weight: 700;
      color: #fff;
    }
  }

  .level-progress-section {
    flex: 1;

    .level-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      span:first-child {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.7);
      }

      .points-info {
        font-size: 13px;
        color: #f59e0b;
        font-weight: 600;
      }
    }

    .el-progress {
      margin-bottom: 8px;
    }

    .level-hint {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.5);
    }
  }
}

/* Points Rules */
.points-rules {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafaf8;
  border-radius: 8px;

  .rule-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .el-icon {
      font-size: 20px;
      color: #fff;
    }

    &.arena {
      background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
    }

    &.learning {
      background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
    }

    &.community {
      background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
    }

    &.dialect {
      background: linear-gradient(135deg, #9c27b0 0%, #ba68c8 100%);
    }
  }

  .rule-content {
    flex: 1;

    h4 {
      font-size: 14px;
      font-weight: 600;
      color: #0d0d0d;
      margin: 0 0 4px;
    }

    p {
      font-size: 12px;
      color: #8a8a8a;
      margin: 0;
    }
  }
}

/* Privileges List */
.privileges-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.privilege-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #fafaf8;
  border-radius: 8px;
  opacity: 0.5;
  transition: all 200ms ease;

  &.unlocked {
    opacity: 1;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(249, 115, 22, 0.05) 100%);
    border: 1px solid rgba(245, 158, 11, 0.2);

    .privilege-icon {
      filter: none;
    }
  }

  .privilege-icon {
    font-size: 20px;
    filter: grayscale(100%);
  }

  .privilege-text {
    font-size: 13px;
    color: #3a3a3a;
  }
}

@media (max-width: 768px) {
  .settings-container {
    flex-direction: column;
  }

  .settings-nav {
    width: 100%;
    display: flex;
    overflow-x: auto;
    padding: 16px;
    gap: 8px;
  }

  .nav-item {
    white-space: nowrap;
    margin-bottom: 0;
  }

  .account-info {
    flex-direction: column;
    align-items: center;
  }

  .detail-row {
    flex-wrap: wrap;
  }

  .detail-row .label {
    width: 100%;
    margin-bottom: 4px;
  }
}
</style>
