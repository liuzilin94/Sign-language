<template>
  <div class="learning-page">
    <div class="page-header">
      <h1>学习中心</h1>
      <p class="subtitle">系统化学习中国手语</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <template v-else>
      <!-- 今日进度卡片 -->
      <div class="progress-section">
        <div class="progress-card">
          <div class="progress-header">
            <el-icon><Calendar /></el-icon>
            <span>今日进度</span>
            <span class="date">{{ todayDate }}</span>
          </div>
          <div class="progress-content">
            <div class="progress-item">
              <div class="progress-label">
                <span class="label-text">学习进度</span>
                <span class="label-count">{{ planData.learned_count }}/{{ planData.new_words_total }}</span>
              </div>
              <el-progress
                :percentage="learnPercentage"
                :stroke-width="8"
                :show-text="false"
                :color="learnProgressColor"
              />
            </div>
            <div class="progress-item">
              <div class="progress-label">
                <span class="label-text">复习进度</span>
                <span class="label-count">{{ planData.reviewed_count }}/{{ planData.review_words_total }}</span>
              </div>
              <el-progress
                :percentage="reviewPercentage"
                :stroke-width="8"
                :show-text="false"
                :color="reviewProgressColor"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 主功能区 -->
      <div class="main-section">
        <!-- 学习卡片 -->
        <div class="main-card learn-card" @click="handleStartLearn">
          <div class="card-icon">
            <el-icon><Reading /></el-icon>
          </div>
          <h2 class="card-title">去学习</h2>
          <p class="card-desc">学习今日新词</p>
          <div class="card-stats">
            <span class="stat-num">{{ planData.new_words_total }}</span>
            <span class="stat-unit">个新词</span>
          </div>
          <div class="card-action">
            <el-button type="primary" :disabled="planData.new_words_completed">
              {{ planData.new_words_completed ? '已完成' : '开始学习' }}
            </el-button>
          </div>
        </div>

        <!-- 复习卡片 -->
        <div class="main-card review-card" @click="handleStartReview">
          <div class="card-icon">
            <el-icon><RefreshRight /></el-icon>
          </div>
          <h2 class="card-title">去复习</h2>
          <p class="card-desc">巩固已学词汇</p>
          <div class="card-stats">
            <span class="stat-num">{{ planData.review_words_total }}</span>
            <span class="stat-unit">个复习词</span>
          </div>
          <div class="card-action">
            <el-button type="warning" :disabled="planData.review_completed">
              {{ planData.review_completed ? '已完成' : '开始复习' }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 小试牛刀入口 -->
      <div class="try-section">
        <div class="try-card" @click="$router.push('/practice')">
          <div class="try-icon practice-icon">
            <el-icon><Aim /></el-icon>
          </div>
          <div class="try-content">
            <h3>小试牛刀</h3>
            <p>进入练习模式，自由练习手语识别</p>
          </div>
          <el-icon class="try-arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- 竞技场入口 -->
      <div class="arena-section">
        <div class="arena-card" @click="$router.push('/arena')">
          <div class="arena-icon-wrap">
            <el-icon><Trophy /></el-icon>
          </div>
          <div class="arena-content">
            <h3>竞技场</h3>
            <p>随机挑战10题，8秒限时，赢取积分！</p>
          </div>
          <el-icon class="arena-arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- 完成提示 -->
      <div v-if="planData.is_all_completed" class="completed-banner">
        <el-icon><CircleCheck /></el-icon>
        <span>太棒了！今日学习任务已全部完成</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Calendar,
  Reading,
  RefreshRight,
  Aim,
  ArrowRight,
  CircleCheck,
  Loading,
  Trophy
} from '@element-plus/icons-vue'
import { learningApi } from '@/api/learning'
import { useSettingsStore } from '@/store/settings'

const router = useRouter()
const settingsStore = useSettingsStore()

const loading = ref(true)
const todayDate = computed(() => {
  const now = new Date()
  return `${now.getMonth() + 1}月${now.getDate()}日`
})

const planData = ref({
  learned_count: 0,
  reviewed_count: 0,
  new_words_total: 0,
  review_words_total: 0,
  new_words_completed: false,
  review_completed: false,
  is_all_completed: false
})

const learnPercentage = computed(() => {
  if (planData.value.new_words_total === 0) return 0
  return Math.round((planData.value.learned_count / planData.value.new_words_total) * 100)
})

const reviewPercentage = computed(() => {
  if (planData.value.review_words_total === 0) return 0
  return Math.round((planData.value.reviewed_count / planData.value.review_words_total) * 100)
})

const learnProgressColor = computed(() => {
  if (planData.value.new_words_completed) return '#67c23a'
  if (learnPercentage.value > 50) return '#409eff'
  return '#409eff'
})

const reviewProgressColor = computed(() => {
  if (planData.value.review_completed) return '#67c23a'
  if (reviewPercentage.value > 50) return '#e6a23c'
  return '#e6a23c'
})

async function loadTodayPlan() {
  try {
    loading.value = true
    const res = await learningApi.getTodayPlan()
    planData.value = {
      learned_count: res.data?.learned_count || 0,
      reviewed_count: res.data?.reviewed_count || 0,
      new_words_total: res.data?.new_words_total || 0,
      review_words_total: res.data?.review_words_total || 0,
      new_words_completed: res.data?.new_words_completed || false,
      review_completed: res.data?.review_completed || false,
      is_all_completed: res.data?.is_all_completed || false
    }
  } catch (e) {
    console.error('加载今日计划失败:', e)
    ElMessage.error('加载失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

function handleStartLearn() {
  if (planData.value.new_words_completed) {
    ElMessage.info('今日学习任务已完成')
    return
  }
  router.push('/learning/session?type=learn')
}

function handleStartReview() {
  if (planData.value.review_completed) {
    ElMessage.info('今日复习任务已完成')
    return
  }
  router.push('/learning/session?type=review')
}

function checkCompletion() {
  // 检查学习是否完成
  if (planData.value.learned_count >= planData.value.new_words_total) {
    planData.value.new_words_completed = true
  }
  // 检查复习是否完成
  if (planData.value.reviewed_count >= planData.value.review_words_total) {
    planData.value.review_completed = true
  }
  // 检查全部完成
  planData.value.is_all_completed = planData.value.new_words_completed && planData.value.review_completed
}

onMounted(() => {
  settingsStore.loadLearningSettings()
  loadTodayPlan()
})

// 监听设置变化，实时更新（当从设置页面返回时重新加载计划）
watch(() => settingsStore.learningSettings, (newSettings, oldSettings) => {
  // 检查设置是否真的变了（避免初始化时触发）
  if (oldSettings && (newSettings.daily_new_words !== oldSettings.daily_new_words || newSettings.daily_review_words !== oldSettings.daily_review_words)) {
    // 设置变了，重新加载今日计划
    loadTodayPlan()
  }
}, { deep: true })
</script>

<style scoped lang="scss">
.learning-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 48px 32px 80px;
  background: #fafaf8;
  min-height: calc(100vh - 60px);
  margin-bottom: 40px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;

  h1 {
    font-size: 28px;
    font-weight: 700;
    color: #0d0d0d;
    margin: 0 0 8px;
    letter-spacing: -0.5px;
  }

  .subtitle {
    font-size: 14px;
    color: #8a8a8a;
    margin: 0;
  }
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #8a8a8a;
  gap: 12px;

  .el-icon {
    font-size: 32px;
  }
}

// 进度卡片
.progress-section {
  margin-bottom: 32px;
}

.progress-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 24px;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;

  .el-icon {
    color: #409eff;
  }

  .date {
    margin-left: auto;
    font-size: 13px;
    font-weight: 400;
    color: #8a8a8a;
  }
}

.progress-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-item {
  .progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 14px;

    .label-text {
      color: #3a3a3a;
    }

    .label-count {
      color: #8a8a8a;
      font-size: 13px;
    }
  }
}

// 主功能区
.main-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.main-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 200ms ease;
  display: flex;
  flex-direction: column;
  align-items: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  }

  .card-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;

    .el-icon {
      font-size: 28px;
    }
  }

  .card-title {
    font-size: 22px;
    font-weight: 700;
    color: #0d0d0d;
    margin: 0 0 8px;
  }

  .card-desc {
    font-size: 14px;
    color: #8a8a8a;
    margin: 0 0 16px;
  }

  .card-stats {
    margin-bottom: 16px;

    .stat-num {
      font-size: 32px;
      font-weight: 700;
      color: #0d0d0d;
    }

    .stat-unit {
      font-size: 14px;
      color: #8a8a8a;
      margin-left: 4px;
    }
  }

  .card-action {
    .el-button {
      min-width: 120px;
    }
  }
}

.learn-card {
  .card-icon {
    background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
    color: #fff;
  }
}

.review-card {
  .card-icon {
    background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
    color: #fff;
  }
}

// 小试牛刀
.try-section {
  margin-bottom: 24px;
}

.try-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 200ms ease;

  &:hover {
    border-color: #409eff;
    background: #f6f9ff;

    .try-arrow {
      transform: translateX(4px);
    }
  }

  .try-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;

    .el-icon {
      font-size: 24px;
    }
  }

  .try-content {
    flex: 1;

    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #0d0d0d;
      margin: 0 0 4px;
    }

    p {
      font-size: 13px;
      color: #8a8a8a;
      margin: 0;
    }
  }

  .try-arrow {
    color: #c0c4cc;
    font-size: 18px;
    transition: transform 200ms ease;
  }
}

// 竞技场
.arena-section {
  margin-bottom: 24px;
}

.arena-card {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 200ms ease;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 200%;
    background: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, transparent 70%);
    pointer-events: none;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);

    .arena-arrow {
      transform: translateX(4px);
    }
  }

  .arena-icon-wrap {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    flex-shrink: 0;

    .el-icon {
      font-size: 24px;
    }
  }

  .arena-content {
    flex: 1;

    h3 {
      font-size: 16px;
      font-weight: 700;
      color: #fff;
      margin: 0 0 4px;
    }

    p {
      font-size: 13px;
      color: rgba(255, 255, 255, 0.6);
      margin: 0;
    }
  }

  .arena-badge {
    flex-shrink: 0;
  }

  .arena-arrow {
    color: rgba(255, 255, 255, 0.4);
    font-size: 18px;
    transition: transform 200ms ease;
  }
}

// 完成提示
.completed-banner {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(133, 206, 97, 0.1) 100%);
  border: 1px solid rgba(103, 194, 58, 0.3);
  border-radius: 12px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #67c23a;
  font-size: 15px;
  font-weight: 500;

  .el-icon {
    font-size: 20px;
  }
}

// 响应式
@media (max-width: 768px) {
  .learning-page {
    padding: 32px 16px 60px;
  }

  .main-section {
    grid-template-columns: 1fr;
  }

  .page-header h1 {
    font-size: 28px;
  }
}
</style>
