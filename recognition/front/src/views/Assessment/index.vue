<template>
  <div class="assessment-page">
    <div class="page-header">
      <el-button @click="$router.back()" text>
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h2>学习测评</h2>
    </div>
    
    <div class="test-selection" v-if="!testStarted">
      <div class="test-list">
        <div
          v-for="test in testList"
          :key="test.id"
          class="test-card"
          :class="{ locked: test.locked }"
          @click="startTest(test)"
        >
          <div class="test-header">
            <span class="test-level">{{ test.level }}</span>
            <el-tag v-if="test.completed" type="success" size="small">已完成</el-tag>
            <el-tag v-else-if="test.locked" type="info" size="small">未解锁</el-tag>
          </div>
          <h3>{{ test.name }}</h3>
          <p>{{ test.desc }}</p>
          <div class="test-meta">
            <span>{{ test.questionCount }} 题</span>
            <span>满分 {{ test.totalScore }} 分</span>
            <span>{{ test.timeLimit }} 分钟</span>
          </div>
          <div class="test-progress" v-if="test.bestScore">
            <span>最高得分：{{ test.bestScore }} 分</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="test-area" v-else>
      <div class="test-info">
        <span>{{ currentTest.name }}</span>
        <span class="timer">
          <el-icon><Timer /></el-icon>
          {{ formatTime(remainingTime) }}
        </span>
      </div>
      
      <div class="question-card">
        <div class="question-header">
          <span class="question-num">第 {{ currentQuestionIndex + 1 }} 题</span>
          <span class="question-type">{{ currentQuestion.type }}</span>
        </div>
        
        <div class="question-content">
          <h3>{{ currentQuestion.content }}</h3>
        </div>
        
        <VideoPlayer v-if="currentQuestion.videoUrl" :src="currentQuestion.videoUrl" />
        
        <div class="options">
          <div
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            class="option-item"
            :class="{ selected: answers[currentQuestionIndex] === index }"
            @click="selectAnswer(index)"
          >
            <span class="option-letter">{{ ['A', 'B', 'C', 'D'][index] }}</span>
            <span class="option-text">{{ option }}</span>
          </div>
        </div>
        
        <div class="question-actions">
          <el-button @click="prevQuestion" :disabled="currentQuestionIndex === 0">
            <el-icon><ArrowLeft /></el-icon> 上一题
          </el-button>
          <el-button v-if="currentQuestionIndex < totalQuestions - 1" type="primary" @click="nextQuestion">
            下一题 <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button v-else type="primary" @click="submitTest">
            提交试卷
          </el-button>
        </div>
      </div>
      
      <div class="question-nav">
        <span
          v-for="i in totalQuestions"
          :key="i"
          :class="{
            current: currentQuestionIndex === i - 1,
            answered: answers[i - 1] !== undefined && answers[i - 1] !== null
          }"
          @click="goToQuestion(i - 1)"
        >
          {{ i }}
        </span>
      </div>
    </div>
    
    <el-dialog v-model="resultDialogVisible" title="测评结果" width="500px" :close-on-click-modal="false">
      <div class="result-content">
        <div class="score-display">
          <el-progress type="circle" :percentage="scorePercent" :width="120" />
          <div class="score-info">
            <span class="score">{{ resultScore }}</span>
            <span class="total">满分 {{ currentTest?.totalScore }}</span>
          </div>
        </div>
        <div class="result-detail">
          <div class="detail-item">
            <span class="label">正确题数</span>
            <span class="value">{{ correctCount }} / {{ totalQuestions }}</span>
          </div>
          <div class="detail-item">
            <span class="label">正确率</span>
            <span class="value">{{ Math.round(correctCount / totalQuestions * 100) }}%</span>
          </div>
          <div class="detail-item">
            <span class="label">用时</span>
            <span class="value">{{ formatTime(usedTime) }}</span>
          </div>
          <div class="detail-item">
            <span class="label">评级</span>
            <span class="value grade">{{ getGrade(scorePercent) }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewWrongQuestions">查看错题</el-button>
        <el-button type="primary" @click="resultDialogVisible = false; testStarted = false">
          返回测评列表
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { ArrowLeft, ArrowRight, Timer } from '@element-plus/icons-vue'
import VideoPlayer from '@/components/VideoPlayer/index.vue'

const testStarted = ref(false)
const resultDialogVisible = ref(false)
const currentTest = ref(null)
const currentQuestionIndex = ref(0)
const answers = ref({})
const remainingTime = ref(0)
const usedTime = ref(0)
const resultScore = ref(0)
const correctCount = ref(0)
const timer = ref(null)

const testList = ref([
  { id: 1, level: '第一单元', name: '基础问候语', desc: '测试你好、谢谢、再见等基础词汇', questionCount: 10, totalScore: 100, timeLimit: 10, completed: false, bestScore: 0, locked: false },
  { id: 2, level: '第二单元', name: '日常生活', desc: '测试家庭、饮食、社会交往相关词汇', questionCount: 15, totalScore: 100, timeLimit: 15, completed: false, bestScore: 0, locked: false },
  { id: 3, level: '第三单元', name: '社会交往', desc: '测试工作、学习相关词汇', questionCount: 20, totalScore: 100, timeLimit: 20, completed: false, bestScore: 0, locked: true },
  { id: 4, level: '第四单元', name: '综合测试', desc: '综合测试所有词汇', questionCount: 25, totalScore: 100, timeLimit: 25, completed: false, bestScore: 0, locked: true }
])

const testQuestions = {
  1: [
    { type: '选择题', content: '以下哪个手势表示"你好"？', options: ['A. 五指并拢向前伸出', 'B. 握拳手腕左右摆动', 'C. 拇指弯曲其余四指并拢', 'D. 食指伸出放于嘴边'], correct: 0, explanation: '"你好"的手型是五指并拢向前伸出，表示友好问候。' },
    { type: '选择题', content: '表示"谢谢"时，手势应该放在哪个位置？', options: ['A. 头顶', 'B. 胸前', 'C. 腹部', 'D. 腰部'], correct: 1, explanation: '"谢谢"的手势放在胸前，表示感谢之情。' },
    { type: '选择题', content: '"再见"的手型特征是什么？', options: ['A. 握拳', 'B. 五指并拢伸直', 'C. 拇指弯曲', 'D. 食指伸出'], correct: 1, explanation: '"再见"的手型是五指并拢伸直，手掌朝下。' },
    { type: '选择题', content: '称呼"妈妈"的手势动作是？', options: ['A. 放在嘴边', 'B. 放在额头向上提', 'C. 放在胸前', 'D. 放在肩膀'], correct: 1, explanation: '"妈妈"的手势是将手放在额头，然后向上轻轻提起。' },
    { type: '选择题', content: '表示"高兴"时，面部表情应该是？', options: ['A. 眉头紧皱', 'B. 面无表情', 'C. 笑容灿烂', 'D. 嘴角下垂'], correct: 2, explanation: '表示"高兴"时，应该面带微笑，笑容灿烂。' },
    { type: '选择题', content: '"对不起"的手型特点是？', options: ['A. 五指张开', 'B. 握拳', 'C. 食指伸出', 'D. 拇指与其他四指捏合'], correct: 1, explanation: '"对不起"的手型是握拳，拇指压在食指上方。' },
    { type: '选择题', content: '表示"吃饭"的动作是？', options: ['A. 双手放在嘴边上下交替', 'B. 双手举过头顶', 'C. 双手放在胸前', 'D. 双手放在腰间'], correct: 0, explanation: '"吃饭"的动作是双手放在嘴边，模拟进食的上下交替动作。' },
    { type: '选择题', content: '"喜欢"的手势特征是？', options: ['A. 四指伸直，拇指弯曲', 'B. 五指张开', 'C. 握拳', 'D. 食指伸出'], correct: 0, explanation: '"喜欢"的手型是四指伸直并拢，拇指弯曲，掌心向外放在胸前。' },
    { type: '选择题', content: '表示"学习"时，手势应该放在哪个位置？', options: ['A. 头顶', 'B. 太阳穴', 'C. 胸前', 'D. 腹部'], correct: 1, explanation: '"学习"的手势是伸出食指放在太阳穴位置，然后向外轻轻推出。' },
    { type: '选择题', content: '"朋友"的手势动作是？', options: ['A. 拇指和食指捏合放于下巴', 'B. 五指张开放于胸前', 'C. 握拳放于腹部', 'D. 食指伸出放于嘴边'], correct: 0, explanation: '"朋友"的手势是拇指和食指伸出成L形，放在下巴附近轻轻摇动。' }
  ],
  2: [
    { type: '选择题', content: '"电脑"的手势动作是？', options: ['A. 双手食指相对上下敲击', 'B. 单手握拳', 'C. 双手张开', 'D. 拇指食指捏合'], correct: 0, explanation: '"电脑"的手势是双手食指相对，模拟键盘打字的动作。' },
    { type: '选择题', content: '表示"难过"时，面部表情应该是？', options: ['A. 面带微笑', 'B. 眉头紧皱眼神低落', 'C. 表情平静', 'D. 眼神明亮'], correct: 1, explanation: '表示"难过"时，眉头微皱，眼神低落，表情悲伤。' },
    { type: '选择题', content: '"工作"的手势动作特征是？', options: ['A. 双手握拳上下交替捶动', 'B. 单手伸出食指', 'C. 双手放在胸前不动', 'D. 手掌向下按压'], correct: 0, explanation: '"工作"的手势是双手握拳，放在胸前上下交替捶动，模拟工作状态。' },
    { type: '选择题', content: '表示"帮助"时，手势的特点是？', options: ['A. 手掌向下按压', 'B. 双手掌心向上向上托起', 'C. 握拳捶动', 'D. 食指伸出'], correct: 1, explanation: '"帮助"的手势是双手掌心向上，然后向上托起，表示关爱和帮助。' },
    { type: '选择题', content: '"讨厌"的手型特征是？', options: ['A. 拇指弯曲四指伸直', 'B. 五指张开掌心向外向下按', 'C. 握拳', 'D. 食指中指伸出'], correct: 1, explanation: '"讨厌"的手型是五指张开，掌心向外，然后向下按压，表示厌恶。' },
    { type: '选择题', content: '"手机"的手势动作是？', options: ['A. 拇指和食指捏合放在耳边', 'B. 五指张开放在头顶', 'C. 双手握拳放在胸前', 'D. 食指伸出放在嘴边'], correct: 0, explanation: '"手机"的手势是拇指和食指捏合，模拟接听电话的动作。' },
    { type: '选择题', content: '"早上好"的手势动作是？', options: ['A. 手掌横放眼前向外滑动', 'B. 掌心向上从下向上抬起', 'C. 手掌放在胸前', 'D. 握拳捶动'], correct: 1, explanation: '"早上好"的手势是掌心向上，手臂从下向上抬起，表示早晨。' },
    { type: '选择题', content: '"晚安"的手势动作是？', options: ['A. 手掌从眼前向外向下移动', 'B. 双手向上托起', 'C. 手掌放在胸前', 'D. 五指张开'], correct: 0, explanation: '"晚安"的手势是手掌横放在眼前，然后向外向下移动，表示晚间。' },
    { type: '选择题', content: '"喝水"的手势动作是？', options: ['A. 食指伸出放在嘴边倾斜', 'B. 五指张开放在胸前', 'C. 握拳放在头顶', 'D. 双手向上托起'], correct: 0, explanation: '"喝水"的手势是伸出食指放在嘴边，手腕微倾模拟喝水动作。' },
    { type: '选择题', content: '"老师"的手势动作特征是？', options: ['A. 双手握拳放在胸前', 'B. 两食指交叉放在胸前', 'C. 五指张开放在头顶', 'D. 拇指食指捏合放在耳边'], correct: 1, explanation: '"老师"的手势是伸出两食指，在胸前交叉，表示尊敬。' },
    { type: '选择题', content: '"爸爸"和"妈妈"手势的主要区别是？', options: ['A. 手型不同', 'B. 动作方向不同', 'C. 位置不同', 'D. 无区别'], correct: 1, explanation: '"爸爸"是放在额头向外轻挑；"妈妈"是放在额头向上轻提，主要区别是动作方向。' },
    { type: '选择题', content: '以下哪个不是手语的四要素之一？', options: ['A. 手型', 'B. 位置', 'C. 颜色', 'D. 动作'], correct: 2, explanation: '手语的四要素是：手型、位置、动作、表情，不包括颜色。' },
    { type: '选择题', content: '"家庭"的手势动作是？', options: ['A. 单手握拳', 'B. 两手食指弯曲靠拢', 'C. 五指张开', 'D. 拇指食指捏合'], correct: 1, explanation: '"家庭"的手势是两食指弯曲靠拢，模拟家人在一起的形状。' },
    { type: '选择题', content: '表示"快乐"时，面部表情应该是？', options: ['A. 面带微笑眼神明亮', 'B. 皱眉', 'C. 面无表情', 'D. 嘴角下垂'], correct: 0, explanation: '表示"快乐"时，应该面带微笑，眼神明亮愉悦。' },
    { type: '选择题', content: '"医生"的手势动作是？', options: ['A. 两手食指交叉', 'B. 两手食指伸直靠拢', 'C. 握拳放于胸前', 'D. 五指张开'], correct: 1, explanation: '"医生"的手势是两食指伸直靠拢，模拟听诊器的形状。' }
  ]
}

const currentQuestion = computed(() => {
  if (!currentTest.value) return null
  return testQuestions[currentTest.value.id]?.[currentQuestionIndex.value]
})

const totalQuestions = computed(() => currentTest.value ? testQuestions[currentTest.value.id]?.length || 0 : 0)
const scorePercent = computed(() => currentTest.value ? Math.round(resultScore.value / currentTest.value.totalScore * 100) : 0)

function startTest(test) {
  if (test.locked) return
  
  currentTest.value = test
  currentQuestionIndex.value = 0
  answers.value = {}
  remainingTime.value = test.timeLimit * 60
  usedTime.value = 0
  testStarted.value = true
  
  timer.value = setInterval(() => {
    remainingTime.value--
    usedTime.value++
    if (remainingTime.value <= 0) {
      submitTest()
    }
  }, 1000)
}

function selectAnswer(index) {
  answers.value[currentQuestionIndex.value] = index
}

function prevQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

function nextQuestion() {
  if (currentQuestionIndex.value < totalQuestions.value - 1) {
    currentQuestionIndex.value++
  }
}

function goToQuestion(index) {
  currentQuestionIndex.value = index
}

function submitTest() {
  clearInterval(timer.value)
  
  let correct = 0
  const questions = testQuestions[currentTest.value.id]
  questions.forEach((q, i) => {
    if (answers.value[i] === q.correct) {
      correct++
    }
  })
  
  correctCount.value = correct
  resultScore.value = Math.round(correct / totalQuestions.value * currentTest.value.totalScore)
  resultDialogVisible.value = true
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function getGrade(percent) {
  if (percent >= 90) return '优秀'
  if (percent >= 80) return '良好'
  if (percent >= 60) return '及格'
  return '不及格'
}

function viewWrongQuestions() {
  console.log('查看错题')
}

onUnmounted(() => {
  if (timer.value) clearInterval(timer.value)
})
</script>

<style scoped lang="scss">
.assessment-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 130px);
  
  .page-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 30px;
    
    h2 {
      font-size: 24px;
      color: #333;
      margin: 0;
    }
  }
  
  .test-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    
    .test-card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover:not(.locked) {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
      }
      
      &.locked {
        opacity: 0.6;
        cursor: not-allowed;
      }
      
      .test-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        
        .test-level {
          color: #667eea;
          font-size: 14px;
        }
      }
      
      h3 {
        font-size: 18px;
        color: #333;
        margin-bottom: 8px;
      }
      
      p {
        font-size: 14px;
        color: #999;
        margin-bottom: 16px;
      }
      
      .test-meta {
        display: flex;
        gap: 16px;
        font-size: 12px;
        color: #666;
        padding-top: 16px;
        border-top: 1px solid #f0f0f0;
      }
      
      .test-progress {
        margin-top: 12px;
        font-size: 12px;
        color: #67c23a;
      }
    }
  }
  
  .test-area {
    background: #fff;
    border-radius: 12px;
    padding: 30px;
    
    .test-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      font-size: 16px;
      color: #333;
      
      .timer {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #f56c6c;
        font-weight: bold;
      }
    }
    
    .question-card {
      .question-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        
        .question-num {
          color: #667eea;
          font-weight: bold;
        }
        
        .question-type {
          padding: 4px 12px;
          background: #f0f9ff;
          color: #667eea;
          border-radius: 12px;
          font-size: 12px;
        }
      }
      
      .question-content {
        margin-bottom: 24px;
        
        h3 {
          font-size: 20px;
          color: #333;
        }
      }
      
      .options {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin: 24px 0;
        
        .option-item {
          display: flex;
          align-items: center;
          padding: 16px 20px;
          border: 2px solid #e4e7ed;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s;
          
          &:hover {
            border-color: #667eea;
          }
          
          &.selected {
            border-color: #667eea;
            background: #f0f9ff;
          }
          
          .option-letter {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #f5f7fa;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 16px;
          }
          
          .option-text {
            font-size: 16px;
            color: #333;
          }
        }
      }
      
      .question-actions {
        display: flex;
        justify-content: space-between;
        gap: 16px;
      }
    }
    
    .question-nav {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid #f0f0f0;
      
      span {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #f5f7fa;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 14px;
        color: #666;
        
        &.current {
          background: #667eea;
          color: #fff;
        }
        
        &.answered:not(.current) {
          background: #e6f7ff;
          color: #667eea;
        }
      }
    }
  }
  
  .result-content {
    text-align: center;
    
    .score-display {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 24px;
      margin-bottom: 24px;
      
      .score-info {
        display: flex;
        flex-direction: column;
        
        .score {
          font-size: 48px;
          font-weight: bold;
          color: #667eea;
        }
        
        .total {
          font-size: 14px;
          color: #999;
        }
      }
    }
    
    .result-detail {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      
      .detail-item {
        padding: 12px;
        background: #f9fafb;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        
        .label {
          color: #999;
        }
        
        .value {
          font-weight: bold;
          color: #333;
          
          &.grade {
            color: #667eea;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .assessment-page {
    .test-area {
      padding: 20px;
      
      .question-card .question-content h3 {
        font-size: 16px;
      }
    }
  }
}
</style>
