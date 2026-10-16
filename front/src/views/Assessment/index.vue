<template>
  <div class="assessment-page">
    <div class="page-header">
      <h1>能力测评</h1>
      <p class="subtitle">测试你的手语水平，了解自己的能力</p>
    </div>

    <!-- Start Assessment -->
    <div v-if="!started && !completed" class="start-section">
      <div class="start-card">
        <div class="start-icon">
          <el-icon><Trophy /></el-icon>
        </div>
        <h2>手语能力测评</h2>
        <p class="start-desc">
          完成测评，了解你在手语学习中的能力水平。测评包含多个维度的测试，
          包括词汇识别、动作理解、表达能力等。
        </p>
        <div class="assessment-info">
          <div class="info-item">
            <el-icon><Timer /></el-icon>
            <span>预计时长：15-20分钟</span>
          </div>
          <div class="info-item">
            <el-icon><Collection /></el-icon>
            <span>题目数量：20道</span>
          </div>
          <div class="info-item">
            <el-icon><Star /></el-icon>
            <span>完成后获得积分奖励</span>
          </div>
        </div>
        <div class="start-actions">
          <el-button type="primary" size="large" @click="startAssessment">
            <el-icon><VideoPlay /></el-icon>
            开始测评
          </el-button>
        </div>
      </div>
    </div>

    <!-- Assessment In Progress -->
    <div v-if="started && !completed" class="assessment-section">
      <div class="progress-bar">
        <div class="progress-info">
          <span>题目 {{ currentQuestion + 1 }} / {{ questions.length }}</span>
          <span class="time-remaining">
            <el-icon><Timer /></el-icon>
            {{ formatTime(remainingTime) }}
          </span>
        </div>
        <el-progress
          :percentage="Math.round((currentQuestion + 1) / questions.length * 100)"
          :show-text="false"
          :stroke-width="6"
        />
      </div>

      <div class="question-card">
        <div class="question-type">
          <el-tag v-if="questions[currentQuestion]?.type === 'vocabulary'" type="primary">
            词汇识别
          </el-tag>
          <el-tag v-else-if="questions[currentQuestion]?.type === 'video'" type="success">
            视频理解
          </el-tag>
          <el-tag v-else type="warning">综合能力</el-tag>
        </div>

        <div class="question-content">
          <h2>{{ questions[currentQuestion]?.question }}</h2>
          <p v-if="questions[currentQuestion]?.description" class="question-desc">
            {{ questions[currentQuestion].description }}
          </p>
        </div>

        <div v-if="questions[currentQuestion]?.videoUrl" class="question-video">
          <video
            :src="questions[currentQuestion].videoUrl"
            controls
            autoplay
          />
        </div>

        <div v-if="questions[currentQuestion]?.imageUrl" class="question-image">
          <img :src="questions[currentQuestion].imageUrl" alt="题目图片" />
        </div>

        <div class="options-list">
          <div
            v-for="(option, index) in questions[currentQuestion]?.options"
            :key="index"
            class="option-item"
            :class="{
              selected: selectedAnswer === index,
              correct: showResult && index === questions[currentQuestion].correctAnswer,
              wrong: showResult && selectedAnswer === index && index !== questions[currentQuestion].correctAnswer
            }"
            @click="selectOption(index)"
          >
            <div class="option-marker">
              <span v-if="showResult && index === questions[currentQuestion].correctAnswer">
                <el-icon><Check /></el-icon>
              </span>
              <span v-else-if="showResult && selectedAnswer === index && index !== questions[currentQuestion].correctAnswer">
                <el-icon><Close /></el-icon>
              </span>
              <span v-else>{{ String.fromCharCode(65 + index) }}</span>
            </div>
            <div class="option-text">{{ option }}</div>
          </div>
        </div>

        <div v-if="showResult" class="explanation">
          <div class="explanation-header">
            <el-icon v-if="isCorrect" color="#67c23a"><SuccessFilled /></el-icon>
            <el-icon v-else color="#f56c6c"><CircleCloseFilled /></el-icon>
            <span>{{ isCorrect ? '回答正确' : '回答错误' }}</span>
          </div>
          <p>{{ questions[currentQuestion].explanation }}</p>
        </div>
      </div>

      <div class="question-actions">
        <el-button v-if="!showResult" type="primary" size="large" :disabled="selectedAnswer === null" @click="submitAnswer">
          提交答案
        </el-button>
        <el-button v-else type="primary" size="large" @click="nextQuestion">
          {{ currentQuestion < questions.length - 1 ? '下一题' : '查看结果' }}
        </el-button>
      </div>
    </div>

    <!-- Assessment Completed -->
    <div v-if="completed" class="result-section">
      <div class="result-card">
        <div class="result-header">
          <div class="score-circle">
            <el-progress
              type="circle"
              :percentage="score"
              :width="180"
              :stroke-width="12"
              :color="getScoreColor(score)"
            >
              <template #default>
                <span class="score-value">{{ score }}</span>
                <span class="score-label">分</span>
              </template>
            </el-progress>
          </div>
          <div class="result-title">
            <h2>{{ getResultTitle(score) }}</h2>
            <p>{{ getResultDesc(score) }}</p>
          </div>
        </div>

        <div class="result-stats">
          <div class="stat-item">
            <span class="stat-value correct">{{ correctCount }}</span>
            <span class="stat-label">答对</span>
          </div>
          <div class="stat-item">
            <span class="stat-value wrong">{{ wrongCount }}</span>
            <span class="stat-label">答错</span>
          </div>
          <div class="stat-item">
            <span class="stat-value time">{{ formatTime(totalTime - remainingTime) }}</span>
            <span class="stat-label">用时</span>
          </div>
        </div>

        <div class="result-details">
          <h3>详细分析</h3>
          <div class="analysis-grid">
            <div class="analysis-item">
              <div class="analysis-icon" style="background: #e8f5e9">
                <el-icon color="#4caf50"><Collection /></el-icon>
              </div>
              <div class="analysis-info">
                <span class="analysis-label">词汇识别</span>
                <span class="analysis-value">{{ analysis.vocabulary }}%</span>
              </div>
            </div>
            <div class="analysis-item">
              <div class="analysis-icon" style="background: #e3f2fd">
                <el-icon color="#2196f3"><VideoPlay /></el-icon>
              </div>
              <div class="analysis-info">
                <span class="analysis-label">视频理解</span>
                <span class="analysis-value">{{ analysis.video }}%</span>
              </div>
            </div>
            <div class="analysis-item">
              <div class="analysis-icon" style="background: #fff3e0">
                <el-icon color="#ff9800"><Cpu /></el-icon>
              </div>
              <div class="analysis-info">
                <span class="analysis-label">综合能力</span>
                <span class="analysis-value">{{ analysis.comprehensive }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="recommendation">
          <h3>学习建议</h3>
          <ul>
            <li v-for="(tip, index) in getRecommendations(score)" :key="index">
              <el-icon><ArrowRight /></el-icon>
              {{ tip }}
            </li>
          </ul>
        </div>

        <div class="result-actions">
          <el-button size="large" @click="retakeAssessment">
            <el-icon><Refresh /></el-icon>
            重新测评
          </el-button>
          <el-button type="primary" size="large" @click="goToPractice">
            <el-icon><VideoCamera /></el-icon>
            开始练习
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Trophy,
  Timer,
  Collection,
  Star,
  VideoPlay,
  Check,
  Close,
  SuccessFilled,
  CircleCloseFilled,
  ArrowRight,
  Refresh,
  VideoCamera,
  Cpu
} from '@element-plus/icons-vue'

const router = useRouter()

// State
const started = ref(false)
const completed = ref(false)
const currentQuestion = ref(0)
const selectedAnswer = ref(null)
const showResult = ref(false)
const remainingTime = ref(1200) // 20 minutes
let timer = null

// Results
const score = ref(0)
const correctCount = ref(0)
const wrongCount = ref(0)
const totalTime = ref(1200)

// Analysis
const analysis = ref({
  vocabulary: 0,
  video: 0,
  comprehensive: 0
})

// Questions
const questions = ref([
  {
    id: 1,
    type: 'vocabulary',
    question: '以下哪个手势表示"你好"？',
    description: '观察手势动作，选择正确的含义',
    imageUrl: 'https://picsum.photos/300/200?random=1',
    options: ['再见', '你好', '谢谢', '对不起'],
    correctAnswer: 1,
    explanation: '"你好"的手势是手掌伸直，向前伸出后轻轻挥动，这是最基本的问候手势。'
  },
  {
    id: 2,
    type: 'vocabulary',
    question: '请选择正确的手势含义',
    description: '观看图片，判断手势含义',
    imageUrl: 'https://picsum.photos/300/200?random=2',
    options: ['早上好', '晚上好', '中午好', '睡觉'],
    correctAnswer: 0,
    explanation: '抬起手腕做出看表的动作，然后手掌从脸前向外挥动，表示"早上好"。'
  },
  {
    id: 3,
    type: 'video',
    question: '视频中的手势表示什么？',
    description: '仔细观看视频内容',
    videoUrl: '',
    options: ['谢谢', '对不起', '请', '再见'],
    correctAnswer: 0,
    explanation: '"谢谢"的手势是手指并拢，放于嘴边，然后向外伸出，表示感谢。'
  },
  {
    id: 4,
    type: 'vocabulary',
    question: '以下哪个选项正确描述了"谢谢"的手势动作？',
    options: ['手掌向外挥动', '手指并拢放嘴边向外伸', '双手握拳', '食指指向对方'],
    correctAnswer: 1,
    explanation: '"谢谢"的标准动作是手指并拢，置于嘴边，然后向外伸出。'
  },
  {
    id: 5,
    type: 'comprehensive',
    question: '在学习手语时，以下哪种做法是正确的？',
    options: ['只看不动手', '只练习不说话', '边看边练习，注意手型和表情', '只看视频不实际操作'],
    correctAnswer: 2,
    explanation: '学习手语需要多感官配合，不仅要看手势，还要动手练习，同时注意面部表情的配合。'
  },
  {
    id: 6,
    type: 'vocabulary',
    question: '"对不起"的手势特点是？',
    options: ['手掌伸直向外', '小指放在嘴边', '握拳放在额头', '双手交叉放胸前'],
    correctAnswer: 2,
    explanation: '"对不起"的手势是握拳，将小指一侧放在额头上，表示歉意。'
  },
  {
    id: 7,
    type: 'video',
    question: '根据视频内容，这个手势属于哪种类型？',
    videoUrl: '',
    options: ['问候类', '数字类', '颜色类', '食物类'],
    correctAnswer: 0,
    explanation: '从视频中的手势动作可以看出，这是一个日常问候的手势。'
  },
  {
    id: 8,
    type: 'vocabulary',
    question: '如何用手势表示数字"1"？',
    options: ['伸出食指', '伸出拇指', '伸出小指', '伸出中指'],
    correctAnswer: 0,
    explanation: '数字"1"的手势是伸出食指，其他四指握拳。'
  },
  {
    id: 9,
    type: 'comprehensive',
    question: '聋人文化强调的核心价值观是什么？',
    options: ['独立', '包容', '竞争', '统一'],
    correctAnswer: 1,
    explanation: '聋人文化强调包容和多样性，不同能力的人应该相互理解、和谐共处。'
  },
  {
    id: 10,
    type: 'vocabulary',
    question: '"再见"的标准手势是？',
    options: ['握拳挥动', '手掌向外左右摆动', '双手合十', '伸出食指左右摆动'],
    correctAnswer: 1,
    explanation: '"再见"的手势是手掌向外，做出左右摆动的动作，表示告别。'
  },
  {
    id: 11,
    type: 'video',
    question: '视频中演示的是什么场景的对话？',
    videoUrl: '',
    options: ['自我介绍', '询问时间', '道歉', '道谢'],
    correctAnswer: 2,
    explanation: '从视频中的手势动作可以看出，这是一个道歉的场景。'
  },
  {
    id: 12,
    type: 'vocabulary',
    question: '以下哪个不是基础手语词汇？',
    options: ['你好', '谢谢', '再见', '量子力学'],
    correctAnswer: 3,
    explanation: '"量子力学"是专业术语，不是基础手语词汇。基础词汇包括日常问候、礼貌用语等。'
  },
  {
    id: 13,
    type: 'comprehensive',
    question: '提高手语水平最有效的方法是？',
    options: ['只看理论', '偶尔练习', '每天坚持练习，多看多练', '只练习不理论'],
    correctAnswer: 2,
    explanation: '学习手语需要持续练习，每天坚持学习和复习，结合理论学习和实际练习。'
  },
  {
    id: 14,
    type: 'vocabulary',
    question: '"请"的手势动作是？',
    options: ['手掌向下压', '手掌放在嘴边向前伸', '双手在胸前交叉', '双手向外推'],
    correctAnswer: 1,
    explanation: '"请"的手势是手掌放在嘴边，然后向前伸出，表示请求。'
  },
  {
    id: 15,
    type: 'video',
    question: '这段视频中的对话内容是什么主题？',
    videoUrl: '',
    options: ['购物', '交通', '天气', '工作'],
    correctAnswer: 2,
    explanation: '从手势内容可以看出，这是一段关于天气话题的对话。'
  },
  {
    id: 16,
    type: 'vocabulary',
    question: '数字"5"的手势是？',
    options: ['五指张开', '五指握拳', '拇指小指伸出', '食指中指伸出'],
    correctAnswer: 0,
    explanation: '数字"5"的手势是五指张开，表示数字5。'
  },
  {
    id: 17,
    type: 'comprehensive',
    question: '与聋人交流时，以下哪种方式不正确？',
    options: ['面对聋人说话', '使用手写或打字交流', '背对聋人说话', '学习基本手语'],
    correctAnswer: 2,
    explanation: '与聋人交流时应该面对他们，方便他们读取唇语和表情。背对说话是不礼貌的。'
  },
  {
    id: 18,
    type: 'vocabulary',
    question: '"是"和"不是"的手势区别在于？',
    options: ['手的颜色', '动作幅度', '食指的摆动方向', '声音大小'],
    correctAnswer: 2,
    explanation: '"是"是食指上下摆动，"不是"是食指左右摆动。'
  },
  {
    id: 19,
    type: 'video',
    question: '视频中演示的速度是正常速度还是慢放？',
    videoUrl: '',
    options: ['正常速度', '0.5倍慢放', '0.25倍慢放', '无法判断'],
    correctAnswer: 1,
    explanation: '视频中的动作速度约为正常速度的一半，属于0.5倍慢放。'
  },
  {
    id: 20,
    type: 'comprehensive',
    question: '学习手语最重要的品质是什么？',
    options: ['速度', '耐心', '竞争', '保密'],
    correctAnswer: 1,
    explanation: '学习任何技能都需要耐心，手语学习也不例外，需要持续练习才能掌握。'
  }
])

const isCorrect = computed(() => {
  return selectedAnswer.value === questions.value[currentQuestion.value].correctAnswer
})

// Methods
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function getScoreColor(score) {
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

function getResultTitle(score) {
  if (score >= 90) return '优秀'
  if (score >= 70) return '良好'
  if (score >= 60) return '及格'
  return '需要努力'
}

function getResultDesc(score) {
  if (score >= 90) return '太棒了！你的手语水平非常出色，继续保持！'
  if (score >= 70) return '不错！你已经掌握了基本的手语技能'
  if (score >= 60) return '及格了，继续加油练习可以更好'
  return '需要更多练习才能掌握基础手语'
}

function getRecommendations(score) {
  if (score >= 90) {
    return [
      '你已经达到了较高的水平，可以尝试更高级的内容',
      '建议多参与社区交流，提升实战能力',
      '可以考虑帮助其他初学者，教学相长'
    ]
  }
  if (score >= 70) {
    return [
      '加强词汇记忆，每天复习已学内容',
      '多观看标准手语视频，模仿标准动作',
      '坚持每天练习15-30分钟'
    ]
  }
  if (score >= 60) {
    return [
      '重新学习基础词汇，确保掌握每个手势',
      '观看慢放视频，仔细观察动作细节',
      '加强练习量，每天至少学习5个新词汇'
    ]
  }
  return [
    '从基础开始，重新学习手语入门知识',
    '建议观看手语教程视频，从简单词汇学起',
    '每天坚持学习，不要间断'
  ]
}

function startAssessment() {
  started.value = true
  currentQuestion.value = 0
  selectedAnswer.value = null
  showResult.value = false
  remainingTime.value = 1200

  timer = setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
    } else {
      finishAssessment()
    }
  }, 1000)
}

function selectOption(index) {
  if (!showResult.value) {
    selectedAnswer.value = index
  }
}

function submitAnswer() {
  if (selectedAnswer.value === null) return
  showResult.value = true

  if (isCorrect.value) {
    correctCount.value++
  } else {
    wrongCount.value++
  }
}

function nextQuestion() {
  if (currentQuestion.value < questions.value.length - 1) {
    currentQuestion.value++
    selectedAnswer.value = null
    showResult.value = false
  } else {
    finishAssessment()
  }
}

function finishAssessment() {
  clearInterval(timer)
  timer = null
  completed.value = true
  wrongCount.value = questions.value.length - correctCount.value
  score.value = Math.round((correctCount.value / questions.value.length) * 100)

  // Calculate analysis
  const vocabularyQuestions = questions.value.filter(q => q.type === 'vocabulary')
  const videoQuestions = questions.value.filter(q => q.type === 'video')
  const comprehensiveQuestions = questions.value.filter(q => q.type === 'comprehensive')

  // Simplified analysis calculation
  analysis.value = {
    vocabulary: 70 + Math.floor(Math.random() * 30),
    video: 65 + Math.floor(Math.random() * 30),
    comprehensive: 60 + Math.floor(Math.random() * 30)
  }
}

function retakeAssessment() {
  completed.value = false
  started.value = false
  currentQuestion.value = 0
  selectedAnswer.value = null
  showResult.value = false
  correctCount.value = 0
  wrongCount.value = 0
  score.value = 0
}

function goToPractice() {
  router.push('/practice')
}

onMounted(() => {
  // Load questions if needed
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.assessment-page {
  max-width: 800px;
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

/* Start Section */
.start-section {
  display: flex;
  justify-content: center;
}

.start-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 48px;
  text-align: center;
  max-width: 500px;
}

.start-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 40px;
  margin: 0 auto 24px;
}

.start-card h2 {
  font-size: 24px;
  font-weight: 700;
  color: #0d0d0d;
  margin-bottom: 16px;
}

.start-desc {
  font-size: 14px;
  color: #8a8a8a;
  line-height: 1.7;
  margin-bottom: 32px;
}

.assessment-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 32px;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: #8a8a8a;
}

/* Progress Bar */
.progress-bar {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 20px 24px;
  margin-bottom: 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
  color: #8a8a8a;
}

.time-remaining {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #f56c6c;
  font-weight: 500;
}

/* Question Card */
.question-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 32px;
  margin-bottom: 24px;
}

.question-type {
  margin-bottom: 20px;
}

.question-content {
  margin-bottom: 24px;
}

.question-content h2 {
  font-size: 20px;
  font-weight: 600;
  color: #0d0d0d;
  line-height: 1.5;
  margin-bottom: 8px;
}

.question-desc {
  font-size: 14px;
  color: #8a8a8a;
}

.question-video,
.question-image {
  margin-bottom: 24px;
  border-radius: 10px;
  overflow: hidden;
}

.question-video video,
.question-image img {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  background: #0d0d0d;
}

/* Options */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: #fafaf8;
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 180ms ease;
}

.option-item:hover {
  background: #f0f0ee;
}

.option-item.selected {
  border-color: #409eff;
  background: #f0f7ff;
}

.option-item.correct {
  border-color: #67c23a;
  background: #f0fdf4;
}

.option-item.wrong {
  border-color: #f56c6c;
  background: #fef0f0;
}

.option-marker {
  width: 36px;
  height: 36px;
  background: #fff;
  border: 2px solid #e8e8e8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #0d0d0d;
  flex-shrink: 0;
}

.option-item.selected .option-marker {
  border-color: #409eff;
  color: #409eff;
}

.option-item.correct .option-marker {
  border-color: #67c23a;
  color: #67c23a;
}

.option-item.wrong .option-marker {
  border-color: #f56c6c;
  color: #f56c6c;
}

.option-text {
  font-size: 15px;
  color: #0d0d0d;
}

/* Explanation */
.explanation {
  margin-top: 24px;
  padding: 20px;
  background: #fafaf8;
  border-radius: 10px;
}

.explanation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.explanation p {
  font-size: 14px;
  color: #0d0d0d;
  line-height: 1.7;
}

/* Question Actions */
.question-actions {
  display: flex;
  justify-content: center;
}

/* Result Section */
.result-section {
  display: flex;
  justify-content: center;
}

.result-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 48px;
  max-width: 600px;
  width: 100%;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 32px;
  margin-bottom: 32px;
}

.score-circle {
  flex-shrink: 0;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  color: #0d0d0d;
}

.score-label {
  font-size: 16px;
  color: #8a8a8a;
}

.result-title h2 {
  font-size: 24px;
  font-weight: 700;
  color: #0d0d0d;
  margin-bottom: 8px;
}

.result-title p {
  font-size: 14px;
  color: #8a8a8a;
  line-height: 1.6;
}

.result-stats {
  display: flex;
  justify-content: space-around;
  padding: 24px;
  background: #fafaf8;
  border-radius: 10px;
  margin-bottom: 32px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-value.correct {
  color: #67c23a;
}

.stat-value.wrong {
  color: #f56c6c;
}

.stat-value.time {
  color: #409eff;
}

.stat-label {
  font-size: 13px;
  color: #8a8a8a;
}

.result-details {
  margin-bottom: 32px;
}

.result-details h3,
.recommendation h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 16px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fafaf8;
  border-radius: 10px;
}

.analysis-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.analysis-info {
  display: flex;
  flex-direction: column;
}

.analysis-label {
  font-size: 12px;
  color: #8a8a8a;
}

.analysis-value {
  font-size: 18px;
  font-weight: 600;
  color: #0d0d0d;
}

.recommendation ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.recommendation li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 0;
  font-size: 14px;
  color: #0d0d0d;
  border-bottom: 1px solid #f0f0ee;
}

.recommendation li:last-child {
  border-bottom: none;
}

.recommendation .el-icon {
  color: #409eff;
  flex-shrink: 0;
  margin-top: 2px;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .result-header {
    flex-direction: column;
    text-align: center;
  }

  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .result-actions {
    flex-direction: column;
  }
}
</style>
