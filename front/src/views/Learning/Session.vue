<template>
  <div class="session-page">
    <!-- 顶部导航 -->
    <div class="session-header">
      <div class="header-left">
        <el-button text @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      <div class="header-center">
        <span class="session-type">{{ sessionType === 'learn' ? '学习' : '复习' }}</span>
        <span class="session-stage">阶段 {{ currentStage }}/{{ maxStage }}</span>
      </div>
      <div class="header-right">
        <span class="progress-text">{{ completedCount }}/{{ totalQuestions }}</span>
      </div>
    </div>

    <!-- 进度条 -->
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>正在加载题目...</span>
    </div>

    <!-- 会话结束 -->
    <div v-else-if="isSessionComplete" class="complete-container">
      <div class="complete-icon">
        <el-icon><CircleCheck /></el-icon>
      </div>
      <p class="complete-stats">
        共{{ sessionType === 'learn' ? '学习' : '复习' }} <strong>{{ completedWords }}</strong> 词
      </p>
      <div class="complete-actions">
        <el-button @click="handleBack">返回学习中心</el-button>
        <el-button type="primary" @click="handleContinue">
          {{ sessionType === 'learn' ? '继续复习' : '重新开始' }}
        </el-button>
      </div>
    </div>

    <!-- 无题目 -->
    <div v-else-if="!currentQuestion" class="empty-container">
      <el-icon><Warning /></el-icon>
      <p>暂无{{ sessionType === 'learn' ? '学习' : '复习' }}任务</p>
      <el-button @click="handleBack">返回学习中心</el-button>
    </div>

    <!-- 题目内容 -->
    <div v-else class="question-container">
      <!-- 阶段1：看视频学习 -->
      <Stage1Video v-if="currentStage === 1"
        :question="currentQuestion"
        @complete="handleStageComplete"
      />

      <!-- 阶段2：选择题 -->
      <Stage2Choice v-else-if="currentStage === 2"
        :question="currentQuestion"
        @answer="handleAnswer"
      />

      <!-- 阶段3：看视频输入 -->
      <Stage3Input v-else-if="currentStage === 3"
        :question="currentQuestion"
        @answer="handleAnswer"
      />

      <!-- 阶段4：手势识别 -->
      <Stage4Gesture v-else-if="currentStage === 4"
        :question="currentQuestion"
        @answer="handleGestureAnswer"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Loading, CircleCheck, Warning } from '@element-plus/icons-vue'

// 导入阶段组件
import Stage1Video from './components/Stage1Video.vue'
import Stage2Choice from './components/Stage2Choice.vue'
import Stage3Input from './components/Stage3Input.vue'
import Stage4Gesture from './components/Stage4Gesture.vue'

import { learningApi } from '@/api/learning'

const router = useRouter()
const route = useRoute()

// 状态
const loading = ref(true)
const sessionType = ref('learn')
const maxStage = ref(4)
const queue = ref([])  // 动态队列
const currentIndex = ref(0)
const completedCount = ref(0)
const correctCount = ref(0)
const totalQuestions = ref(0)
const wordCount = ref(0)  // 词汇数量
const isSessionComplete = ref(false)

// 计算属性
const currentQuestion = computed(() => {
  if (currentIndex.value >= queue.value.length) return null
  return queue.value[currentIndex.value]
})

const currentStage = computed(() => {
  return currentQuestion.value?.stage || 1
})

const progressPercentage = computed(() => {
  if (totalQuestions.value === 0) return 0
  return Math.round((completedCount.value / totalQuestions.value) * 100)
})

const correctRate = computed(() => {
  if (completedCount.value === 0) return 0
  return Math.round((correctCount.value / completedCount.value) * 100)
})

const completedWords = computed(() => {
  return wordCount.value
})

// 启动会话
async function startSession() {
  try {
    loading.value = true
    const res = await learningApi.startSession(sessionType.value)

    if (!res.data) {
      ElMessage.error('获取学习任务失败')
      return
    }

    queue.value = res.data.queue || []
    totalQuestions.value = res.data.total_questions || 0
    wordCount.value = res.data.word_count || res.data.total_questions || 0
    maxStage.value = sessionType.value === 'learn' ? 4 : 3
    currentIndex.value = 0
    completedCount.value = 0
    correctCount.value = 0
    isSessionComplete.value = false

    if (queue.value.length === 0) {
      ElMessage.info('暂无学习任务')
    }
  } catch (e) {
    console.error('启动会话失败:', e)
    ElMessage.error('加载失败，请重试')
  } finally {
    loading.value = false
  }
}

// 处理返回
async function handleBack() {
  if (completedCount.value > 0) {
    try {
      await ElMessageBox.confirm(
        '确定要退出吗？当前进度将会保留。',
        '提示',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
    } catch {
      return
    }
  }
  router.push('/learning')
}

// 阶段1完成
function handleStageComplete() {
  submitAnswer({ stage1_learned: true })
}

// 选择题答案
function handleAnswer(answerData) {
  submitAnswer(answerData)
}

// 手势识别答案
async function handleGestureAnswer(isCorrect) {
  submitAnswer({ stage4_correct: isCorrect })
}

// 提交答案
async function submitAnswer(answerData) {
  try {
    const question = currentQuestion.value
    const res = await learningApi.submitAnswer({
      word_id: question.word_id,
      session_type: sessionType.value,
      stage: question.stage,
      answer: answerData
    })

    const result = res.data

    // 答错或不确定：显示下一题
    if (!result.is_correct || result.is_uncertain) {
      ElMessage.info('跳过此题，稍后会重新出现')
      showNextQuestion(result.next_question)
    } else if (result.is_completed) {
      // 当前词全部完成
      completedCount.value++
      correctCount.value++
      ElMessage.success('太棒了！此词已掌握')
      showNextQuestion(result.next_question)
    } else {
      // 阶段正确，显示下一题
      completedCount.value++
      correctCount.value++
      ElMessage.success('正确！')
      showNextQuestion(result.next_question)
    }
  } catch (e) {
    console.error('提交答案失败:', e)
    ElMessage.error('提交失败，请重试')
  }
}

// 显示下一题
function showNextQuestion(nextQuestion) {
  if (nextQuestion) {
    // 后端返回了下一题，直接添加到队列
    currentIndex.value++
    queue.value.splice(currentIndex.value, 0, nextQuestion)
    // 如果下一题是新的词汇，增加总题目数
    if (!nextQuestion.is_retry) {
      // 不增加 totalQuestions，因为后端已计算
    }
  } else {
    // 没有更多题目
    isSessionComplete.value = true
  }
}

// 移动到下一题（用于初始加载）
function moveToNext() {
  currentIndex.value++
  if (currentIndex.value >= queue.value.length) {
    isSessionComplete.value = true
  }
}

// 继续学习/复习
function handleContinue() {
  if (sessionType.value === 'learn') {
    sessionType.value = 'review'
  }
  startSession()
}

// 初始化
onMounted(() => {
  const type = route.query.type
  if (type === 'review') {
    sessionType.value = 'review'
  }
  startSession()
})
</script>

<style scoped lang="scss">
.session-page {
  min-height: 100vh;
  background: #fafaf8;
  display: flex;
  flex-direction: column;
}

// 顶部导航
.session-header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;

  .header-left {
    flex: 1;
  }

  .header-center {
    display: flex;
    align-items: center;
    gap: 12px;

    .session-type {
      font-size: 16px;
      font-weight: 600;
      color: #0d0d0d;
    }

    .session-stage {
      font-size: 14px;
      color: #8a8a8a;
      padding: 4px 12px;
      background: #f5f5f5;
      border-radius: 12px;
    }
  }

  .header-right {
    flex: 1;
    text-align: right;

    .progress-text {
      font-size: 14px;
      color: #8a8a8a;
    }
  }
}

// 进度条
.progress-bar {
  height: 4px;
  background: #e8e8e8;

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
    transition: width 300ms ease;
  }
}

// 加载状态
.loading-container,
.empty-container,
.complete-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;

  .el-icon {
    font-size: 48px;
    color: #c0c4cc;
    margin-bottom: 16px;
  }

  span, p {
    color: #8a8a8a;
    font-size: 15px;
  }
}

.empty-container {
  .el-icon {
    font-size: 64px;
  }
}

// 完成页面
.complete-container {
  .complete-icon {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24px;

    .el-icon {
      font-size: 40px;
      color: #fff;
      margin: 0;
    }
  }

  h2 {
    font-size: 24px;
    font-weight: 700;
    color: #0d0d0d;
    margin: 0 0 12px;
  }

  .complete-stats {
    font-size: 15px;
    color: #8a8a8a;
    margin: 0 0 32px;

    strong {
      color: #0d0d0d;
      font-weight: 600;
    }
  }

  .complete-actions {
    display: flex;
    gap: 12px;
  }
}

// 题目内容
.question-container {
  flex: 1;
  padding: 24px;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .session-header {
    padding: 10px 16px;
  }

  .question-container {
    padding: 16px;
  }
}
</style>
