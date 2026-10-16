<template>
  <div class="tasks-page">
    <div class="page-header">
      <h1>学习中心</h1>
      <p class="subtitle">跟踪你的学习进度，合理安排复习</p>
    </div>

    <!-- Daily Status -->
    <div class="daily-status-card">
      <div class="status-icon">
        <el-icon><Calendar /></el-icon>
      </div>
      <div class="status-content">
        <h2>{{ greeting }}</h2>
        <p>{{ todayMessage }}</p>
      </div>
      <div class="status-actions">
        <el-button type="primary" size="large" @click="startLearning">
          <el-icon><VideoPlay /></el-icon>
          开始学习
        </el-button>
        <el-button size="large" @click="goToReview" :disabled="reviewCount === 0">
          <el-icon><Refresh /></el-icon>
          今日复习 ({{ reviewCount }})
        </el-button>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #e8f5e9">
          <el-icon color="#4caf50"><Collection /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.learnedWords }}</span>
          <span class="stat-label">已学词汇</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #e3f2fd">
          <el-icon color="#2196f3"><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.todayReview }}</span>
          <span class="stat-label">今日复习</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #fff3e0">
          <el-icon color="#ff9800"><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.streak }}</span>
          <span class="stat-label">连续天数</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #fce4ec">
          <el-icon color="#e91e63"><Star /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalPractice }}</span>
          <span class="stat-label">累计练习</span>
        </div>
      </div>
    </div>

    <!-- Quick Entry Cards -->
    <div class="section-title">
      <h2>快速入口</h2>
    </div>
    <div class="quick-cards">
      <div class="quick-card" @click="dailyWord">
        <div class="quick-card-icon">
          <el-icon><Sunrise /></el-icon>
        </div>
        <div class="quick-card-content">
          <h3>每日一词</h3>
          <p>每天学习一个新词汇</p>
        </div>
        <el-icon class="arrow"><ArrowRight /></el-icon>
      </div>

      <div class="quick-card" @click="reviewConsolidation">
        <div class="quick-card-icon" style="background: #e8f5e9">
          <el-icon color="#4caf50"><RefreshLeft /></el-icon>
        </div>
        <div class="quick-card-content">
          <h3>复习巩固</h3>
          <p>根据记忆曲线复习</p>
        </div>
        <el-icon class="arrow"><ArrowRight /></el-icon>
      </div>

      <div class="quick-card" @click="goToPractice">
        <div class="quick-card-icon" style="background: #e3f2fd">
          <el-icon color="#2196f3"><VideoCamera /></el-icon>
        </div>
        <div class="quick-card-content">
          <h3>背词练习</h3>
          <p>摄像头录制练习</p>
        </div>
        <el-icon class="arrow"><ArrowRight /></el-icon>
      </div>

      <div class="quick-card" @click="goToCommunity">
        <div class="quick-card-icon" style="background: #fff3e0">
          <el-icon color="#ff9800"><ChatDotRound /></el-icon>
        </div>
        <div class="quick-card-content">
          <h3>社区交流</h3>
          <p>与其他学习者互动</p>
        </div>
        <el-icon class="arrow"><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- Ebbinghaus Review Stages -->
    <div class="section-title">
      <h2>艾宾浩斯复习计划</h2>
      <p class="section-desc">根据遗忘曲线科学安排复习时间</p>
    </div>
    <div class="ebbinghaus-stages">
      <div
        v-for="stage in ebbinghausStages"
        :key="stage.day"
        class="stage-card"
        :class="{ completed: stage.completed, current: stage.isToday }"
      >
        <div class="stage-header">
          <span class="stage-day">第 {{ stage.day }} 天</span>
          <el-tag
            v-if="stage.isToday"
            size="small"
            type="warning"
          >
            今天
          </el-tag>
          <el-tag
            v-else-if="stage.completed"
            size="small"
            type="success"
          >
            已完成
          </el-tag>
        </div>
        <div class="stage-content">
          <div class="stage-date">{{ stage.date }}</div>
          <div class="stage-words">
            <span>{{ stage.wordCount }} 个词汇</span>
          </div>
        </div>
        <div class="stage-progress">
          <el-progress
            :percentage="stage.progress"
            :show-text="false"
            :stroke-width="4"
          />
        </div>
        <el-button
          v-if="stage.isToday && !stage.completed"
          type="primary"
          size="small"
          @click="startReviewStage(stage)"
        >
          开始复习
        </el-button>
        <el-button
          v-else-if="stage.isToday && stage.completed"
          type="success"
          size="small"
          disabled
        >
          <el-icon><Check /></el-icon>
          已完成
        </el-button>
      </div>
    </div>

    <!-- Review Word List -->
    <div class="section-title">
      <h2>待复习词汇</h2>
      <el-select v-model="reviewFilter" placeholder="筛选" clearable>
        <el-option label="全部" value="all" />
        <el-option label="今天" value="today" />
        <el-option label="本周" value="week" />
        <el-option label="已过期" value="overdue" />
      </el-select>
    </div>

    <div class="review-list">
      <div
        v-for="word in filteredReviewWords"
        :key="word.id"
        class="review-item"
      >
        <div class="review-item-main">
          <div class="word-preview">
            <video v-if="word.videoUrl" :src="word.videoUrl" muted loop />
            <div v-else class="word-placeholder">
              <el-icon><Picture /></el-icon>
            </div>
          </div>
          <div class="word-info">
            <h3>{{ word.title }}</h3>
            <div class="word-meta">
              <span class="category">{{ word.category }}</span>
              <span class="dot">•</span>
              <span class="learn-date">学习于 {{ word.learnDate }}</span>
            </div>
          </div>
        </div>
        <div class="review-item-actions">
          <el-tag v-if="isOverdue(word)" type="danger" size="small">已过期</el-tag>
          <el-tag v-else-if="isDueToday(word)" type="warning" size="small">今天</el-tag>
          <el-button size="small" @click="reviewWord(word)">
            <el-icon><VideoPlay /></el-icon>
            复习
          </el-button>
          <el-button size="small" type="primary" @click="practiceWord(word)">
            <el-icon><VideoCamera /></el-icon>
            练习
          </el-button>
        </div>
      </div>

      <div v-if="filteredReviewWords.length === 0" class="empty-state">
        <el-icon><SuccessFilled /></el-icon>
        <p>太棒了！没有待复习的词汇</p>
      </div>
    </div>

    <!-- Review Dialog -->
    <el-dialog
      v-model="showReviewDialog"
      :title="'复习: ' + currentReviewWord?.title"
      width="700px"
    >
      <div class="review-dialog-content">
        <div class="review-video">
          <video
            v-if="currentReviewWord?.videoUrl"
            :src="currentReviewWord.videoUrl"
            controls
            autoplay
          />
        </div>
        <div class="review-steps">
          <h3>动作分解</h3>
          <div
            v-for="(step, index) in currentReviewWord?.steps"
            :key="index"
            class="step-item"
          >
            <span class="step-num">{{ index + 1 }}</span>
            <span class="step-text">{{ step }}</span>
          </div>
        </div>
        <div class="review-actions">
          <el-button @click="showHint = !showHint">
            <el-icon><QuestionFilled /></el-icon>
            提示
          </el-button>
          <el-button type="success" @click="markAsReviewed">
            <el-icon><Check /></el-icon>
            我记住了
          </el-button>
          <el-button type="warning" @click="needMorePractice">
            <el-icon><RefreshLeft /></el-icon>
            还需要练习
          </el-button>
        </div>
        <div v-if="showHint" class="hint-box">
          <el-icon><InfoFilled /></el-icon>
          <span>{{ currentReviewWord?.hint }}</span>
        </div>
      </div>
    </el-dialog>

    <!-- Practice Dialog -->
    <el-dialog
      v-model="showPracticeDialog"
      :title="'练习: ' + currentPracticeWord?.title"
      width="600px"
    >
      <div class="practice-dialog-content">
        <div class="camera-preview-small">
          <video ref="practiceVideo" autoplay playsinline muted></video>
        </div>
        <div class="practice-controls">
          <el-button
            v-if="!isPracticeRecording"
            type="primary"
            @click="startPracticeRecording"
          >
            <el-icon><VideoCamera /></el-icon>
            开始录制
          </el-button>
          <el-button
            v-else
            type="danger"
            @click="stopPracticeRecording"
          >
            <el-icon><VideoPause /></el-icon>
            停止
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- Learning Progress -->
    <div class="section-title">
      <h2>学习进度</h2>
    </div>
    <div class="learning-progress">
      <div class="progress-overview">
        <div class="progress-circle">
          <el-progress
            type="dashboard"
            :percentage="learningProgress"
            :width="160"
          >
            <template #default>
              <span class="progress-value">{{ learningProgress }}%</span>
              <span class="progress-label">完成度</span>
            </template>
          </el-progress>
        </div>
        <div class="progress-stats">
          <div class="progress-stat">
            <span class="value">{{ progressStats.currentLevel }}</span>
            <span class="label">当前等级</span>
          </div>
          <div class="progress-stat">
            <span class="value">{{ progressStats.wordsToNext }}</span>
            <span class="label">距下一级</span>
          </div>
        </div>
      </div>
      <div class="level-roadmap">
        <div
          v-for="level in levels"
          :key="level.id"
          class="level-item"
          :class="{ completed: level.completed, current: level.current }"
        >
          <div class="level-icon">
            <el-icon v-if="level.completed"><Check /></el-icon>
            <span v-else>{{ level.order }}</span>
          </div>
          <div class="level-info">
            <span class="level-name">{{ level.name }}</span>
            <span class="level-desc">{{ level.description }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { learningApi } from '@/api'
import {
  Calendar,
  VideoPlay,
  Refresh,
  Collection,
  Timer,
  TrendCharts,
  Star,
  Sunrise,
  RefreshLeft,
  VideoCamera,
  ChatDotRound,
  ArrowRight,
  Check,
  Picture,
  SuccessFilled,
  QuestionFilled,
  InfoFilled,
  VideoPause
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// Stats
const stats = ref({
  learnedWords: 0,
  todayReview: 0,
  streak: 0,
  totalPractice: 0
})

// Review
const reviewFilter = ref('all')
const reviewWords = ref([])
const showReviewDialog = ref(false)
const currentReviewWord = ref(null)
const showHint = ref(false)

// Practice
const showPracticeDialog = ref(false)
const currentPracticeWord = ref(null)
const practiceVideo = ref(null)
const isPracticeRecording = ref(false)
let practiceRecorder = null
let practiceChunks = []

// Levels
const levels = ref([
  { id: 1, name: '入门', description: '掌握基础手型', order: 1, completed: true },
  { id: 2, name: '基础', description: '日常问候语', order: 2, completed: true },
  { id: 3, name: '进阶', description: '简单对话', order: 3, completed: false, current: true },
  { id: 4, name: '中级', description: '情感表达', order: 4, completed: false },
  { id: 5, name: '高级', description: '复杂语句', order: 5, completed: false }
])

const progressStats = computed(() => ({
  currentLevel: 3,
  wordsToNext: 25
}))

const learningProgress = computed(() => {
  return Math.round((stats.value.learnedWords / 100) * 100)
})

// Ebbinghaus stages
const ebbinghausStages = ref([
  { day: 1, date: '04-23', wordCount: 10, completed: true, isToday: false, progress: 100 },
  { day: 2, date: '04-24', wordCount: 8, completed: false, isToday: true, progress: 30 },
  { day: 4, date: '04-26', wordCount: 6, completed: false, isToday: false, progress: 0 },
  { day: 7, date: '04-29', wordCount: 5, completed: false, isToday: false, progress: 0 },
  { day: 15, date: '05-07', wordCount: 4, completed: false, isToday: false, progress: 0 },
  { day: 30, date: '05-22', wordCount: 3, completed: false, isToday: false, progress: 0 }
])

// Computed
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

const todayMessage = computed(() => {
  if (reviewCount.value > 0) {
    return `今天有 ${reviewCount.value} 个词汇需要复习`
  }
  return '今天没有待复习的词汇，继续保持'
})

const reviewCount = computed(() => {
  return reviewWords.value.filter(w => isDueToday(w) || isOverdue(w)).length
})

const filteredReviewWords = computed(() => {
  let result = reviewWords.value

  switch (reviewFilter.value) {
    case 'today':
      result = result.filter(w => isDueToday(w))
      break
    case 'week':
      result = result.filter(w => {
        const dueDate = new Date(w.dueDate)
        const now = new Date()
        const weekLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
        return dueDate <= weekLater
      })
      break
    case 'overdue':
      result = result.filter(w => isOverdue(w))
      break
  }

  return result.sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))
})

// Methods
function isDueToday(word) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const dueDate = new Date(word.dueDate)
  dueDate.setHours(0, 0, 0, 0)
  return dueDate.getTime() === today.getTime()
}

function isOverdue(word) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const dueDate = new Date(word.dueDate)
  dueDate.setHours(0, 0, 0, 0)
  return dueDate < today
}

async function loadStats() {
  try {
    const res = await learningApi.getStats(userStore.userInfo?.id)
    stats.value = res.data || {
      learnedWords: 156,
      todayReview: 12,
      streak: 7,
      totalPractice: 428
    }
  } catch (error) {
    stats.value = {
      learnedWords: 156,
      todayReview: 12,
      streak: 7,
      totalPractice: 428
    }
  }
}

async function loadReviewWords() {
  try {
    const res = await learningApi.getReviewWords(userStore.userInfo?.id)
    reviewWords.value = res.data || generateMockReviewWords()
  } catch (error) {
    reviewWords.value = generateMockReviewWords()
  }
}

function generateMockReviewWords() {
  return [
    { id: 1, title: '你好', category: '问候', videoUrl: '', learnDate: '04-20', dueDate: '04-24', steps: ['手掌伸直', '向前伸出', '轻轻挥动'], hint: '这是最基础的问候手势' },
    { id: 2, title: '谢谢', category: '礼貌', videoUrl: '', learnDate: '04-19', dueDate: '04-24', steps: ['手指并拢', '放于嘴边', '向外伸出'], hint: '表示感谢的手势' },
    { id: 3, title: '再见', category: '日常', videoUrl: '', learnDate: '04-18', dueDate: '04-25', steps: ['手掌向外', '左右摆动'], hint: '告别时使用' },
    { id: 4, title: '早上好', category: '问候', videoUrl: '', learnDate: '04-15', dueDate: '04-22', steps: ['抬起手腕', '看表动作', '手掌从脸前向外'], hint: '早晨问候语' }
  ]
}

function startLearning() {
  router.push('/practice')
}

function goToReview() {
  if (reviewCount.value > 0) {
    showReviewDialog.value = true
    currentReviewWord.value = reviewWords.value.find(w => isDueToday(w) || isOverdue(w))
  }
}

function goToPractice() {
  router.push('/practice')
}

function goToCommunity() {
  router.push('/community')
}

function dailyWord() {
  router.push('/practice')
}

function reviewConsolidation() {
  router.push('/practice')
}

function reviewWord(word) {
  currentReviewWord.value = word
  showHint.value = false
  showReviewDialog.value = true
}

function practiceWord(word) {
  currentPracticeWord.value = word
  showPracticeDialog.value = true
  initPracticeCamera()
}

function startReviewStage(stage) {
  showReviewDialog.value = true
  currentReviewWord.value = reviewWords.value[0]
}

function markAsReviewed() {
  ElMessage.success('太棒了！已标记为已复习')
  showReviewDialog.value = false
}

function needMorePractice() {
  showReviewDialog.value = false
  router.push('/practice')
}

async function initPracticeCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    if (practiceVideo.value) {
      practiceVideo.value.srcObject = stream
    }
  } catch (error) {
    ElMessage.error('无法访问摄像头')
  }
}

function startPracticeRecording() {
  isPracticeRecording.value = true
  practiceChunks = []
}

function stopPracticeRecording() {
  isPracticeRecording.value = false
  ElMessage.success('录制完成，正在提交...')
  setTimeout(() => {
    showPracticeDialog.value = false
  }, 1000)
}

onMounted(() => {
  loadStats()
  loadReviewWords()
})
</script>

<style scoped>
.tasks-page {
  max-width: 1200px;
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

/* Daily Status */
.daily-status-card {
  display: flex;
  align-items: center;
  gap: 24px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 32px;
  margin-bottom: 32px;
}

.status-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
}

.status-content {
  flex: 1;
}

.status-content h2 {
  font-size: 22px;
  font-weight: 700;
  color: #0d0d0d;
  margin-bottom: 4px;
}

.status-content p {
  font-size: 14px;
  color: #8a8a8a;
}

.status-actions {
  display: flex;
  gap: 12px;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 48px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #0d0d0d;
}

.stat-label {
  font-size: 12px;
  color: #8a8a8a;
}

/* Section */
.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-title h2 {
  font-size: 20px;
  font-weight: 700;
  color: #0d0d0d;
}

.section-desc {
  font-size: 14px;
  color: #8a8a8a;
  margin-left: 12px;
}

/* Quick Cards */
.quick-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 48px;
}

.quick-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 180ms ease;
}

.quick-card:hover {
  border-color: #0d0d0d;
  transform: translateY(-2px);
}

.quick-card-icon {
  width: 48px;
  height: 48px;
  background: #e8e8e8;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #0d0d0d;
}

.quick-card-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 4px;
}

.quick-card-content p {
  font-size: 12px;
  color: #8a8a8a;
}

.arrow {
  color: #8a8a8a;
  font-size: 20px;
}

/* Ebbinghaus */
.ebbinghaus-stages {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 48px;
}

.stage-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  transition: all 180ms ease;
}

.stage-card.current {
  border-color: #409eff;
  background: #f0f7ff;
}

.stage-card.completed {
  background: #f0fdf4;
  border-color: #67c23a;
}

.stage-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.stage-day {
  font-size: 14px;
  font-weight: 600;
  color: #0d0d0d;
}

.stage-content {
  margin-bottom: 12px;
}

.stage-date {
  font-size: 12px;
  color: #8a8a8a;
  margin-bottom: 4px;
}

.stage-words {
  font-size: 14px;
  color: #0d0d0d;
  font-weight: 500;
}

.stage-progress {
  margin-bottom: 12px;
}

/* Review List */
.review-list {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 48px;
}

.review-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e8e8;
  transition: background 180ms ease;
}

.review-item:last-child {
  border-bottom: none;
}

.review-item:hover {
  background: #fafaf8;
}

.review-item-main {
  display: flex;
  align-items: center;
  gap: 16px;
}

.word-preview {
  width: 80px;
  height: 60px;
  background: #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
}

.word-preview video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.word-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a8a8a;
}

.word-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 4px;
}

.word-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #8a8a8a;
}

.dot {
  color: #dcdfe6;
}

.review-item-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-state {
  padding: 60px 24px;
  text-align: center;
  color: #8a8a8a;
}

.empty-state .el-icon {
  font-size: 48px;
  color: #67c23a;
  margin-bottom: 16px;
}

/* Review Dialog */
.review-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.review-video {
  width: 100%;
  aspect-ratio: 16/9;
  background: #0d0d0d;
  border-radius: 10px;
  overflow: hidden;
}

.review-video video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.review-steps h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 12px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 0;
}

.step-num {
  width: 24px;
  height: 24px;
  background: #0d0d0d;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-text {
  font-size: 14px;
  color: #0d0d0d;
  line-height: 1.6;
}

.review-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.hint-box {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #fff3cd;
  border-radius: 8px;
  font-size: 14px;
  color: #664d03;
}

.hint-box .el-icon {
  flex-shrink: 0;
}

/* Practice Dialog */
.practice-dialog-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.camera-preview-small {
  width: 100%;
  aspect-ratio: 16/9;
  background: #0d0d0d;
  border-radius: 10px;
  overflow: hidden;
}

.camera-preview-small video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.practice-controls {
  display: flex;
  gap: 12px;
}

/* Learning Progress */
.learning-progress {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 32px;
}

.progress-overview {
  display: flex;
  align-items: center;
  gap: 48px;
  margin-bottom: 32px;
}

.progress-value {
  font-size: 32px;
  font-weight: 700;
  color: #0d0d0d;
  display: block;
}

.progress-label {
  font-size: 12px;
  color: #8a8a8a;
}

.progress-stats {
  display: flex;
  gap: 32px;
}

.progress-stat {
  display: flex;
  flex-direction: column;
}

.progress-stat .value {
  font-size: 24px;
  font-weight: 700;
  color: #0d0d0d;
}

.progress-stat .label {
  font-size: 12px;
  color: #8a8a8a;
}

.level-roadmap {
  display: flex;
  gap: 12px;
}

.level-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fafaf8;
  border-radius: 8px;
  transition: all 180ms ease;
}

.level-item.current {
  background: #e8f5e9;
  border: 1px solid #67c23a;
}

.level-item.completed .level-icon {
  background: #67c23a;
  color: #fff;
}

.level-icon {
  width: 32px;
  height: 32px;
  background: #e8e8e8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #0d0d0d;
  flex-shrink: 0;
}

.level-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.level-name {
  font-size: 14px;
  font-weight: 600;
  color: #0d0d0d;
}

.level-desc {
  font-size: 11px;
  color: #8a8a8a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 1024px) {
  .stats-grid,
  .quick-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .ebbinghaus-stages {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .daily-status-card {
    flex-direction: column;
    text-align: center;
  }

  .status-actions {
    flex-direction: column;
  }

  .stats-grid,
  .quick-cards {
    grid-template-columns: 1fr;
  }

  .ebbinghaus-stages {
    grid-template-columns: repeat(2, 1fr);
  }

  .review-item {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .level-roadmap {
    flex-direction: column;
  }
}
</style>
