<template>
  <div class="arena-page">
    <!-- 开始界面 -->
    <div v-if="state === 'idle'" class="arena-start">
      <div class="arena-header">
        <el-button text @click="$router.push('/learning')">
          <el-icon><ArrowLeft /></el-icon>
          返回学习中心
        </el-button>
      </div>

      <div class="arena-hero">
        <div class="arena-icon">⚔️</div>
        <h1>竞技场挑战</h1>
        <p class="arena-desc">
          随机抽取词汇学习中的选择题和看视频输入题<br>
          共10题，每题仅有8秒钟作答时间<br>
          答对几题，就能获得相应积分！
        </p>

        <div class="arena-rules">
          <h3>挑战规则</h3>
          <ul>
            <li>🎯 题目来源：随机抽取词汇的阶段2（选择题）和阶段3（看视频输入）</li>
            <li>⏱️ 每题作答时间：8秒</li>
            <li>🏆 奖励：答对1题 = 1积分</li>
            <li>📊 积分可累计，用于升级（100积分/级）</li>
          </ul>
        </div>

        <el-button type="primary" size="large" @click="startArena" :loading="loading">
          开始挑战
        </el-button>

        <p class="arena-hint" v-if="!hasLearningRecord">
          暂无学习记录，请先学习一些词汇再来挑战！
        </p>
      </div>
    </div>

    <!-- 答题界面 -->
    <div v-else-if="state === 'playing'" class="arena-play">
      <div class="arena-top-bar">
        <div class="question-progress">
          <span>第 {{ currentIndex + 1 }} / {{ questions.length }} 题</span>
        </div>
        <div class="timer" :class="{ urgent: timeLeft <= 3 }">
          <el-icon><Timer /></el-icon>
          {{ timeLeft }}秒
        </div>
        <div class="score-display">
          得分: {{ correctCount }}
        </div>
      </div>

      <!-- 进度条 -->
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: ((currentIndex + 1) / questions.length * 100) + '%' }"
        ></div>
      </div>

      <!-- 选择题 -->
      <div v-if="currentQuestion.stage === 2" class="question-card">
        <div class="question-type">选择题</div>
        <div class="question-prompt">请根据以下动作描述选择对应的词汇：</div>

        <!-- 动作描述 -->
        <div class="action-description" v-if="currentQuestion.question_text">
          <pre>{{ currentQuestion.question_text }}</pre>
        </div>

        <div class="options-grid">
          <div
            v-for="(option, idx) in currentQuestion.options"
            :key="idx"
            class="option-btn"
            :class="{
              selected: selectedOption === idx,
              correct: showResult && idx === currentQuestion.correct_index,
              wrong: showResult && selectedOption === idx && idx !== currentQuestion.correct_index
            }"
            @click="selectOption(idx)"
          >
            {{ option.word }}
          </div>
        </div>
      </div>

      <!-- 看视频输入题 -->
      <div v-else-if="currentQuestion.stage === 3" class="question-card">
        <div class="question-type">看视频输入</div>
        <div class="question-prompt">请观看视频后输入正确的词汇：</div>

        <div class="video-container">
          <video
            v-if="currentQuestion.video_url"
            :src="currentQuestion.video_url"
            autoplay
            loop
            muted
            playsinline
          ></video>
          <div v-else class="video-placeholder">
            <img
              v-if="currentQuestion.image_url"
              :src="currentQuestion.image_url"
              alt="词汇图片"
            />
            <span v-else>无视频</span>
          </div>
        </div>

        <div class="input-area">
          <el-input
            v-model="userInput"
            placeholder="请输入词汇..."
            size="large"
            :disabled="showResult"
            @keyup.enter="submitInput"
          />
          <el-button type="primary" size="large" @click="submitInput" :disabled="showResult">
            确认
          </el-button>
        </div>
      </div>

      <!-- 结果反馈 -->
      <div v-if="showResult" class="result-feedback" :class="lastAnswerCorrect ? 'correct' : 'wrong'">
        <div class="feedback-icon">{{ lastAnswerCorrect ? '✓' : '✗' }}</div>
        <div class="feedback-text">
          {{ lastAnswerCorrect ? '回答正确！' : '回答错误' }}
          <template v-if="!lastAnswerCorrect">
            ，正确答案是：<strong>{{ correctAnswer }}</strong>
          </template>
        </div>
      </div>
    </div>

    <!-- 结果界面 -->
    <div v-else-if="state === 'finished'" class="arena-result">
      <div class="result-card">
        <div class="result-icon" :class="resultInfo.points_earned > 0 ? 'success' : 'normal'">
          {{ resultInfo.points_earned > 0 ? '🏆' : '💪' }}
        </div>
        <h2>挑战完成！</h2>

        <div class="result-stats">
          <div class="stat-item">
            <span class="stat-value">{{ resultInfo.correct_count }}</span>
            <span class="stat-label">答对题数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ resultInfo.total_count }}</span>
            <span class="stat-label">总题数</span>
          </div>
          <div class="stat-item highlight">
            <span class="stat-value">+{{ resultInfo.points_earned }}</span>
            <span class="stat-label">获得积分</span>
          </div>
        </div>

        <div class="level-info" v-if="resultInfo.level_up">
          <div class="level-up-badge">
            🎉 恭喜升级！当前等级：Lv.{{ resultInfo.new_level }}
          </div>
        </div>

        <div class="result-actions">
          <el-button type="primary" size="large" @click="startArena">
            再来一局
          </el-button>
          <el-button size="large" @click="$router.push('/learning')">
            返回学习中心
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
import { ArrowLeft, Timer } from '@element-plus/icons-vue'
import { arenaApi } from '@/api'

const router = useRouter()

// 状态
const state = ref('idle') // idle, playing, finished
const loading = ref(false)
const questions = ref([])
const currentIndex = ref(0)
const timeLeft = ref(8)
const timer = ref(null)

// 答题状态
const selectedOption = ref(null)
const userInput = ref('')
const showResult = ref(false)
const lastAnswerCorrect = ref(false)
const correctAnswer = ref('')
const answers = ref([])
const correctCount = ref(0)

// 结果
const resultInfo = ref({})
const hasLearningRecord = ref(true)

const currentQuestion = computed(() => {
  return questions.value[currentIndex.value] || null
})

// 开始竞技场
async function startArena() {
  try {
    loading.value = true
    const res = await arenaApi.start()
    if (res.code === 200 && res.data) {
      questions.value = res.data.questions || []
      if (questions.value.length === 0) {
        hasLearningRecord.value = false
        ElMessage.warning('暂无足够的题目，请先学习一些词汇')
        return
      }
      hasLearningRecord.value = true
      currentIndex.value = 0
      correctCount.value = 0
      answers.value = []
      state.value = 'playing'
      startTimer()
    } else {
      hasLearningRecord.value = false
      ElMessage.warning(res.message || '暂无学习记录，请先学习一些词汇')
    }
  } catch (e) {
    console.error('启动竞技场失败:', e)
    ElMessage.error('启动失败，请重试')
  } finally {
    loading.value = false
  }
}

// 开始计时器
function startTimer() {
  timeLeft.value = 8
  clearInterval(timer.value)
  timer.value = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timer.value)
      // 超时处理
      if (!showResult.value) {
        handleTimeout()
      }
    }
  }, 1000)
}

// 超时处理
function handleTimeout() {
  const q = currentQuestion.value
  if (q.stage === 2) {
    // 选择题超时，视为错误
    submitAnswer(false, null)
  } else {
    // 输入题超时，提交空答案
    submitAnswer(false, '')
  }
}

// 选择选项（选择题）
function selectOption(idx) {
  if (showResult.value) return
  selectedOption.value = idx
  submitAnswer(idx === currentQuestion.value.correct_index, idx)
}

// 提交输入（输入题）
function submitInput() {
  if (showResult.value || !userInput.value.trim()) return
  const isCorrect = userInput.value.trim() === currentQuestion.value.word
  submitAnswer(isCorrect, userInput.value.trim())
}

// 提交答案
async function submitAnswer(isCorrect, answer) {
  clearInterval(timer.value)
  showResult.value = true
  lastAnswerCorrect.value = isCorrect
  correctAnswer.value = currentQuestion.value.word

  if (isCorrect) {
    correctCount.value++
  }

  answers.value.push({
    word_id: currentQuestion.value.word_id,
    stage: currentQuestion.value.stage,
    is_correct: isCorrect
  })

  // 等待1.5秒后进入下一题或结束
  setTimeout(() => {
    showResult.value = false
    selectedOption.value = null
    userInput.value = ''

    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value++
      startTimer()
    } else {
      finishArena()
    }
  }, 1500)
}

// 完成竞技场
async function finishArena() {
  try {
    const res = await arenaApi.finish(answers.value)
    if (res.code === 200) {
      resultInfo.value = res.data
      state.value = 'finished'
    } else {
      ElMessage.error(res.message || '提交结果失败')
    }
  } catch (e) {
    console.error('提交结果失败:', e)
    ElMessage.error('提交结果失败')
  }
}

onMounted(() => {
  // 检查是否有学习记录
})

onUnmounted(() => {
  clearInterval(timer.value)
})
</script>

<style scoped lang="scss">
$ink: #0d0d0d;
$ink-light: #3a3a3a;
$ink-faint: #8a8a8a;
$ink-ghost: #c8c8c8;
$ink-line: #e8e8e8;
$paper: #fafaf8;
$paper-warm: #f5f3ef;
$white: #ffffff;
$accent: #1a1a1a;
$success: #3a7a3a;
$error: #dc2626;
$warn: #b45309;
$gold: #f59e0b;

.arena-page {
  min-height: calc(100vh - 60px);
  padding: 48px 32px 80px;
  background: $paper;

  // 开始界面
  .arena-start {
    max-width: 600px;
    margin: 0 auto;

    .arena-header {
      margin-bottom: 32px;

      .el-button {
        color: $ink-faint;
        &:hover { color: $ink; }
      }
    }

    .arena-hero {
      text-align: center;
      background: $white;
      border: 1px solid $ink-line;
      border-radius: 12px;
      padding: 48px 40px;

      .arena-icon {
        font-size: 64px;
        margin-bottom: 16px;
      }

      h1 {
        font-size: 28px;
        font-weight: 700;
        color: $ink;
        margin: 0 0 16px;
      }

      .arena-desc {
        color: $ink-faint;
        font-size: 14px;
        line-height: 1.8;
        margin-bottom: 32px;
      }

      .arena-rules {
        background: $paper-warm;
        border-radius: 8px;
        padding: 20px 24px;
        text-align: left;
        margin-bottom: 32px;

        h3 {
          font-size: 15px;
          font-weight: 600;
          color: $ink;
          margin: 0 0 12px;
        }

        ul {
          margin: 0;
          padding-left: 20px;

          li {
            color: $ink-light;
            font-size: 13px;
            line-height: 1.8;
          }
        }
      }

      .arena-hint {
        color: $error;
        font-size: 13px;
        margin-top: 16px;
      }
    }
  }

  // 答题界面
  .arena-play {
    max-width: 700px;
    margin: 0 auto;

    .arena-top-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: $white;
      border: 1px solid $ink-line;
      border-radius: 8px;
      padding: 16px 20px;
      margin-bottom: 16px;

      .question-progress {
        font-size: 14px;
        color: $ink-faint;
      }

      .timer {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 20px;
        font-weight: 700;
        color: $ink;
        padding: 8px 16px;
        background: $paper-warm;
        border-radius: 6px;

        &.urgent {
          color: $error;
          background: rgba($error, 0.1);
          animation: pulse 0.5s ease-in-out infinite;
        }
      }

      .score-display {
        font-size: 14px;
        color: $ink-faint;

        span {
          font-weight: 700;
          color: $success;
        }
      }
    }

    .progress-bar {
      height: 4px;
      background: $ink-line;
      border-radius: 2px;
      margin-bottom: 24px;

      .progress-fill {
        height: 100%;
        background: $accent;
        border-radius: 2px;
        transition: width 300ms ease;
      }
    }

    .question-card {
      background: $white;
      border: 1px solid $ink-line;
      border-radius: 12px;
      padding: 32px;

      .question-type {
        display: inline-block;
        background: $ink;
        color: $white;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 4px;
        margin-bottom: 16px;
      }

      .question-prompt {
        font-size: 16px;
        color: $ink-light;
        margin-bottom: 16px;
      }

      .action-description {
        background: $paper-warm;
        border: 1px solid $ink-line;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;

        pre {
          margin: 0;
          font-family: inherit;
          font-size: 14px;
          line-height: 1.8;
          color: $ink;
          white-space: pre-wrap;
          word-break: break-word;
        }
      }

      .options-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;

        .option-btn {
          padding: 20px;
          background: $paper-warm;
          border: 2px solid transparent;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          color: $ink;
          cursor: pointer;
          transition: all 200ms ease;

          &:hover:not(.selected):not(.correct):not(.wrong) {
            background: $white;
            border-color: $ink-ghost;
          }

          &.selected {
            border-color: $accent;
            background: rgba($accent, 0.05);
          }

          &.correct {
            border-color: $success;
            background: rgba($success, 0.1);
            color: $success;
          }

          &.wrong {
            border-color: $error;
            background: rgba($error, 0.1);
            color: $error;
          }
        }
      }

      .video-container {
        margin-bottom: 24px;
        border-radius: 8px;
        overflow: hidden;
        background: #1a1a2e;

        video, img {
          width: 100%;
          max-height: 300px;
          object-fit: contain;
        }

        .video-placeholder {
          min-height: 200px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #555;
        }
      }

      .input-area {
        display: flex;
        gap: 12px;

        .el-input {
          flex: 1;
        }
      }
    }

    .result-feedback {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px 20px;
      border-radius: 8px;
      margin-top: 16px;

      &.correct {
        background: rgba($success, 0.1);
        border: 1px solid rgba($success, 0.3);

        .feedback-icon { color: $success; }
        .feedback-text { color: $success; }
      }

      &.wrong {
        background: rgba($error, 0.1);
        border: 1px solid rgba($error, 0.3);

        .feedback-icon { color: $error; }
        .feedback-text { color: $ink-light; }
      }

      .feedback-icon {
        font-size: 24px;
        font-weight: 700;
      }

      .feedback-text {
        font-size: 14px;
      }
    }
  }

  // 结果界面
  .arena-result {
    max-width: 500px;
    margin: 0 auto;

    .result-card {
      background: $white;
      border: 1px solid $ink-line;
      border-radius: 12px;
      padding: 48px 40px;
      text-align: center;

      .result-icon {
        font-size: 72px;
        margin-bottom: 16px;

        &.success { animation: bounce 0.6s ease; }
      }

      h2 {
        font-size: 24px;
        font-weight: 700;
        color: $ink;
        margin: 0 0 32px;
      }

      .result-stats {
        display: flex;
        justify-content: center;
        gap: 32px;
        margin-bottom: 32px;

        .stat-item {
          text-align: center;

          .stat-value {
            display: block;
            font-size: 32px;
            font-weight: 700;
            color: $ink;
          }

          .stat-label {
            font-size: 13px;
            color: $ink-faint;
          }

          &.highlight .stat-value {
            color: $gold;
          }
        }
      }

      .level-info {
        margin-bottom: 32px;

        .level-up-badge {
          display: inline-block;
          background: linear-gradient(135deg, $gold, #f97316);
          color: $white;
          font-size: 14px;
          font-weight: 600;
          padding: 12px 24px;
          border-radius: 999px;
          animation: bounce 0.6s ease;
        }
      }

      .result-actions {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .el-button {
          width: 100%;
        }
      }
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@media (max-width: 768px) {
  .arena-page {
    padding: 24px 16px 60px;

    .arena-start .arena-hero,
    .arena-play .question-card,
    .arena-result .result-card {
      padding: 24px 20px;
    }

    .arena-play .options-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
