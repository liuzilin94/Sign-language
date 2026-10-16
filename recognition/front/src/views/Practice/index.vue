<template>
  <div class="practice-page">
    <div class="page-header">
      <el-button @click="$router.back()" text>
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h2>手语背词练习</h2>
      <div class="model-status" :class="modelStatusClass">
        <el-icon><InfoFilled /></el-icon>
        {{ modelStatusText }}
      </div>
    </div>

    <!-- 第一步：选择词条 -->
    <div class="word-select-section" v-if="currentStep === 'select'">
      <div class="section-title">
        <el-icon><Reading /></el-icon>
        选择练习词条
      </div>

      <div class="filter-bar">
        <el-select v-model="filterCategory" placeholder="类别筛选" clearable size="default">
          <el-option label="全部" value="" />
          <el-option label="基础" value="基础" />
          <el-option label="生活" value="生活" />
          <el-option label="社会" value="社会" />
          <el-option label="情感" value="情感" />
          <el-option label="科技" value="科技" />
        </el-select>
        <el-select v-model="filterDifficulty" placeholder="难度筛选" clearable size="default">
          <el-option label="全部" value="" />
          <el-option label="入门" value="1" />
          <el-option label="基础" value="2" />
          <el-option label="进阶" value="3" />
        </el-select>
        <el-input
          v-model="filterKeyword"
          placeholder="搜索词条"
          clearable
          size="default"
          style="width: 200px"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>

      <div class="word-grid">
        <div
          v-for="word in filteredWords"
          :key="word.id"
          class="word-card"
          :class="{
            selected: selectedWordId === word.id,
            learned: learnedWords.includes(word.id)
          }"
          @click="selectWord(word)"
        >
          <div class="word-main">{{ word.word }}</div>
          <div class="word-meta">
            <el-tag size="small" :type="difficultyType(word.difficulty)">{{ difficultyLabel(word.difficulty) }}</el-tag>
            <el-tag size="small">{{ word.category }}</el-tag>
          </div>
          <div class="word-status" v-if="learnedWords.includes(word.id)">
            <el-icon><CircleCheck style="color: #67c23a" /></el-icon>
          </div>
        </div>
      </div>

      <div class="select-summary" v-if="selectedWordId">
        <span>已选：<strong>{{ selectedWord?.word }}</strong></span>
        <el-button type="primary" size="large" @click="startCameraPractice" :loading="cameraLoading" :disabled="!isModelReady">
          <el-icon><VideoCamera /></el-icon>
          开始摄像头练习
        </el-button>
        <el-button size="large" @click="startVideoPractice">
          <el-icon><VideoPlay /></el-icon>
          观看示范练习
        </el-button>
      </div>
    </div>

    <!-- 第二步：摄像头手语练习 -->
    <div class="camera-section" v-if="currentStep === 'camera'">
      <div class="camera-header">
        <el-button @click="goBackToSelect" text>
          <el-icon><ArrowLeft /></el-icon> 重新选择
        </el-button>
        <span class="target-word">请比划：<strong>{{ currentWord?.word }}</strong></span>
        <el-tag v-if="!isModelReady" type="danger" size="small">模型未就绪</el-tag>
      </div>

      <div class="camera-content">
        <div class="camera-wrapper">
          <video ref="videoRef" class="camera-video" autoplay playsinline></video>
          <div class="camera-overlay" v-if="!cameraActive">
            <div class="overlay-content">
              <el-icon :size="48"><VideoCamera /></el-icon>
              <p>点击启动摄像头</p>
              <el-button type="primary" @click="startCamera" :disabled="!isModelReady">启动摄像头</el-button>
            </div>
          </div>
          <div class="camera-guide" v-if="cameraActive">
            <div class="guide-hint">
              <el-icon><InfoFilled /></el-icon>
              请在镜头前比划 "{{ currentWord?.word }}" 的手语动作
            </div>
          </div>
          <div class="recording-indicator" v-if="isRecording">
            <span class="dot"></span> 识别中
          </div>
        </div>

        <div class="word-reference">
          <div class="reference-card">
            <div class="reference-header">
              <el-icon><QuestionFilled /></el-icon>
              <span>动作要点提示</span>
            </div>
            <ul class="reference-tips">
              <li v-for="(tip, i) in currentWord?.tips" :key="i">{{ tip }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="camera-controls">
        <el-button
          type="primary"
          size="large"
          @click="startRecognition"
          :disabled="!cameraActive || !isModelReady"
          :loading="isRecording"
        >
          <el-icon><Pointer /></el-icon>
          开始识别
        </el-button>
        <el-button size="large" @click="showReference = !showReference">
          <el-icon><View /></el-icon>
          {{ showReference ? '隐藏' : '查看' }}示范
        </el-button>
      </div>

      <!-- 示范视频/图片区 -->
      <div class="reference-demo" v-if="showReference">
        <VideoPlayer
          v-if="currentWord?.demoVideo"
          :src="currentWord.demoVideo"
        />
        <div class="demo-placeholder" v-else>
          <el-icon :size="64"><VideoPlay /></el-icon>
          <p>示范视频</p>
          <span>{{ currentWord?.word }} 手语演示</span>
        </div>
      </div>
    </div>

    <!-- 第三步：结果反馈 -->
    <div class="result-section" v-if="currentStep === 'result'">
      <div class="result-card" :class="resultClass">
        <div class="result-icon">
          <el-icon v-if="accuracy >= 50"><CircleCheck /></el-icon>
          <el-icon v-else><CircleClose /></el-icon>
        </div>
        <h3>{{ resultTitle }}</h3>
        <p class="result-desc">{{ resultDesc }}</p>

        <!-- 对比信息区 -->
        <div class="compare-info">
          <div class="compare-row">
            <span class="label">目标词汇</span>
            <span class="value">{{ compareTarget }}</span>
          </div>
          <div class="compare-row">
            <span class="label">识别结果</span>
            <span class="value" :class="isMatch ? 'match' : 'mismatch'">{{ compareResult }}</span>
          </div>
          <div class="compare-row">
            <span class="label">识别置信度</span>
            <span class="value">{{ compareConfidence }}</span>
          </div>
          <div class="compare-row">
            <span class="label">判定阈值</span>
            <span class="value">50%</span>
          </div>
        </div>

        <div class="accuracy-display">
          <div class="accuracy-ring">
            <svg viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" stroke="#e4e7ed" stroke-width="8" />
              <circle
                cx="50" cy="50" r="45" fill="none"
                :stroke="accuracyColor"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="`${accuracy * 2.83} 283`"
                transform="rotate(-90 50 50)"
              />
            </svg>
            <div class="accuracy-text">
              <span class="value">{{ accuracy }}</span>
              <span class="unit">%</span>
            </div>
          </div>
          <div class="accuracy-label">目标词汇置信度</div>
        </div>

        <div class="score-breakdown">
          <div class="score-item">
            <span class="label">手型</span>
            <el-rate v-model="scores.posture" disabled show-text>
              <template #text>
                <span :style="{ color: scores.posture >= 3 ? '#67c23a' : '#f56c6c' }">
                  {{ ['较差', '一般', '良好', '优秀', '完美'][scores.posture - 1] }}
                </span>
              </template>
            </el-rate>
          </div>
          <div class="score-item">
            <span class="label">位置</span>
            <el-rate v-model="scores.location" disabled show-text>
              <template #text>
                <span :style="{ color: scores.location >= 3 ? '#67c23a' : '#f56c6c' }">
                  {{ ['较差', '一般', '良好', '优秀', '完美'][scores.location - 1] }}
                </span>
              </template>
            </el-rate>
          </div>
          <div class="score-item">
            <span class="label">动作</span>
            <el-rate v-model="scores.movement" disabled show-text>
              <template #text>
                <span :style="{ color: scores.movement >= 3 ? '#67c23a' : '#f56c6c' }">
                  {{ ['较差', '一般', '良好', '优秀', '完美'][scores.movement - 1] }}
                </span>
              </template>
            </el-rate>
          </div>
        </div>

        <div class="result-actions">
          <el-button @click="goBackToSelect">换个词条</el-button>
          <el-button type="primary" @click="retryPractice">再练一次</el-button>
          <el-button type="success" @click="goToNextWord">下一个词</el-button>
        </div>
      </div>
    </div>

    <!-- 第四步：观看示范练习 -->
    <div class="video-practice-section" v-if="currentStep === 'video'">
      <div class="camera-header">
        <el-button @click="goBackToSelect" text>
          <el-icon><ArrowLeft /></el-icon> 重新选择
        </el-button>
        <span class="target-word">跟练：<strong>{{ currentWord?.word }}</strong></span>
      </div>

      <div class="video-practice-content">
        <div class="demo-display">
          <VideoPlayer
            v-if="currentWord?.demoVideo"
            :src="currentWord.demoVideo"
            :autoplay="true"
          />
          <div class="demo-placeholder" v-else>
            <el-icon :size="80"><VideoPlay /></el-icon>
            <p>{{ currentWord?.word }}</p>
            <span>手语示范演示</span>
          </div>
          <div class="playback-controls">
            <el-button-group>
              <el-button @click="slowMotion = 0.5" :type="slowMotion === 0.5 ? 'primary' : ''">0.5x</el-button>
              <el-button @click="slowMotion = 1" :type="slowMotion === 1 ? 'primary' : ''">1x</el-button>
              <el-button @click="slowMotion = 0.25" :type="slowMotion === 0.25 ? 'primary' : ''">慢放 0.25x</el-button>
            </el-button-group>
            <el-button-group>
              <el-button @click="cameraAngle = 'front'" :type="cameraAngle === 'front' ? 'primary' : ''">正面</el-button>
              <el-button @click="cameraAngle = 'side'" :type="cameraAngle === 'side' ? 'primary' : ''">侧面</el-button>
              <el-button @click="cameraAngle = 'top'" :type="cameraAngle === 'top' ? 'primary' : ''">俯视</el-button>
            </el-button-group>
          </div>
        </div>

        <div class="practice-tips">
          <div class="tips-card">
            <div class="tips-header">
              <el-icon><InfoFilled /></el-icon>
              <span>动作分解</span>
            </div>
            <div class="tips-steps">
              <div class="step" v-for="(step, i) in currentWord?.steps" :key="i">
                <span class="step-num">{{ i + 1 }}</span>
                <span class="step-text">{{ step }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="video-practice-actions">
        <el-button size="large" @click="startCameraFromVideo">摄像头练习</el-button>
        <el-button type="primary" size="large" @click="markAsLearned">我学会了</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  ArrowLeft, Reading, VideoCamera, VideoPlay, CircleCheck,
  CircleClose, Warning, Search, InfoFilled, Pointer, View,
  QuestionFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import VideoPlayer from '@/components/VideoPlayer/index.vue'

// ============ 状态定义 ============
const currentStep = ref('select')
const selectedWordId = ref(null)
const cameraActive = ref(false)
const cameraLoading = ref(false)
const isRecording = ref(false)
const showReference = ref(false)
const slowMotion = ref(1)
const cameraAngle = ref('front')
const accuracy = ref(0)
const scores = ref({ posture: 3, location: 3, movement: 3 })
const learnedWords = ref(JSON.parse(localStorage.getItem('learnedWords') || '[]'))

const isModelReady = ref(false)
const modelLoading = ref(false)

let mediaStream = null
const videoRef = ref(null)

const filterCategory = ref('')
const filterDifficulty = ref('')
const filterKeyword = ref('')

const API_BASE = 'http://localhost:5001'

// ============ 词汇数据 ============
const allWords = ref([])
const wordExtensions = {}
const defaultTips = ['请比划该词汇的标准手语动作', '注意手型和动作规范', '保持自然表情']
const defaultSteps = ['第一步：做出标准手语姿势', '第二步：保持动作稳定', '第三步：完成手势表达']

async function loadVocabulary() {
  try {
    const response = await fetch(`${API_BASE}/api/vocabulary`)
    const data = await response.json()
    if (data.success && data.vocabulary) {
      allWords.value = data.vocabulary.map((item, idx) => {
        const ext = wordExtensions[item.id] || {}
        return {
          id: idx,
          backendId: item.id,
          word: item.text,
          category: ext.category || '���分类',
          difficulty: ext.difficulty || 1,
          scene: ext.scene || '',
          region: ext.region || '',
          tips: ext.tips || defaultTips,
          steps: ext.steps || defaultSteps,
          demoVideo: ext.demoVideo || ''
        }
      })
      console.log(`✅ 词汇表加载成功，共 ${allWords.value.length} 个词汇`)
    } else {
      ElMessage.error('词汇表数据格式错误')
    }
  } catch (error) {
    console.error('❌ 加载词汇表失败:', error)
    ElMessage.error('无法加载词汇表，请确保后端服务已启动')
  }
}

async function initModel() {
  if (isModelReady.value) return
  modelLoading.value = true
  try {
    const response = await fetch(`${API_BASE}/api/init-isolated`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_type: 'cnn_lstm' })
    })
    const data = await response.json()
    if (data.success) {
      isModelReady.value = true
      ElMessage.success('模型初始化成功')
    } else {
      ElMessage.error('模型初始化失败: ' + data.message)
      isModelReady.value = false
    }
  } catch (error) {
    console.error('❌ 模型初始化失败:', error)
    ElMessage.error('无法连接到后端服务')
    isModelReady.value = false
  } finally {
    modelLoading.value = false
  }
}

// ============ 计算属性 ============
const filteredWords = computed(() => {
  return allWords.value.filter(w => {
    if (filterCategory.value && w.category !== filterCategory.value) return false
    if (filterDifficulty.value && w.difficulty !== Number(filterDifficulty.value) * 1) return false
    if (filterKeyword.value && !w.word.includes(filterKeyword.value)) return false
    return true
  })
})

const selectedWord = computed(() => allWords.value.find(w => w.id === selectedWordId.value))

const resultClass = computed(() => {
  if (accuracy.value >= 80) return 'result-excellent'
  if (accuracy.value >= 50) return 'result-good'
  return 'result-poor'
})

const resultTitle = computed(() => {
  if (accuracy.value >= 90) return '太棒了！完美！'
  if (accuracy.value >= 80) return '表现优秀！'
  if (accuracy.value >= 60) return '还不错，继续加油！'
  if (accuracy.value >= 40) return '还需多练习'
  return '继续努力，多看示范'
})

const resultDesc = computed(() => {
  if (accuracy.value >= 80) return '你的手语动作非常标准，继续保持！'
  if (accuracy.value >= 50) return '动作基本正确，注意细节会更棒！'
  return '建议多观看示范视频，练习动作分解'
})

const accuracyColor = computed(() => {
  if (accuracy.value >= 80) return '#67c23a'
  if (accuracy.value >= 50) return '#e6a23c'
  return '#f56c6c'
})

const compareTarget = computed(() => selectedWord.value?.word || '--')
const compareResult = computed(() => lastRecognitionResult.value?.predicted || '--')
const compareConfidence = computed(() => {
  const conf = lastRecognitionResult.value?.target_confidence || 0
  return `${(conf * 100).toFixed(1)}%`
})
const isMatch = computed(() => lastRecognitionResult.value?.predicted === compareTarget.value)

const modelStatusText = computed(() => {
  if (modelLoading.value) return '模型初始化中...'
  if (isModelReady.value) return '✅ 模型就绪'
  return '❌ 模型未就绪'
})

const modelStatusClass = computed(() => {
  if (modelLoading.value) return 'status-loading'
  if (isModelReady.value) return 'status-ready'
  return 'status-error'
})

// ============ 工具函数 ============
function difficultyLabel(d) {
  return ['', '入门', '基础', '进阶'][d] || '入门'
}

function difficultyType(d) {
  return ['', 'success', 'warning', 'danger'][d] || 'success'
}

function selectWord(word) {
  selectedWordId.value = word.id
}

// ============ 摄像头控制 ============
async function startCamera() {
  try {
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
      mediaStream = null
    }

    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' },
      audio: false
    })

    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 150))

    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      await videoRef.value.play()
      cameraActive.value = true
      console.log('✅ Camera started')
    } else {
      console.error('❌ videoRef is null')
      ElMessage.error('摄像头元素未就绪')
    }
  } catch (err) {
    console.error('❌ Camera error:', err)
    ElMessage.error('摄像头启动失败: ' + err.message)
    cameraActive.value = false
  }
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  cameraActive.value = false
}

// 监听步骤变化，自动管理摄像头
watch(currentStep, async (newStep, oldStep) => {
  if (newStep === 'camera') {
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))
    if (!cameraActive.value && isModelReady.value) {
      await startCamera()
    }
  } else if (oldStep === 'camera' && newStep !== 'camera') {
    stopCamera()
  }
})

// ============ 页面导航 ============
function startCameraPractice() {
  currentStep.value = 'camera'
  cameraLoading.value = true
  setTimeout(() => { cameraLoading.value = false }, 500)
}

function startVideoPractice() {
  currentStep.value = 'video'
}

function goBackToSelect() {
  currentStep.value = 'select'
}

// ============ 核心识别逻辑 ============
const lastRecognitionResult = ref(null)

async function startRecognition() {
  if (!cameraActive.value || !selectedWordId.value || !isModelReady.value) {
    ElMessage.warning('请确保摄像头已启动且模型已就绪')
    return
  }

  isRecording.value = true
  try {
    const videoBlob = await recordVideo(3000)
    const formData = new FormData()
    formData.append('video', videoBlob, 'recording.webm')
    formData.append('target_index', selectedWordId.value.toString())

    ElMessage.info('正在识别，请稍候...')
    const response = await fetch(`${API_BASE}/api/predict-isolated`, {
      method: 'POST',
      body: formData
    })
    const data = await response.json()

    if (data.success) {
      lastRecognitionResult.value = {
        predicted: data.predicted,
        confidence: data.confidence,
        target: data.target,
        target_confidence: data.target_confidence
      }

      const threshold = 0.5
      const isCorrect = (data.predicted === data.target) && (data.target_confidence >= threshold)
      accuracy.value = Math.round(data.target_confidence * 100)
      const score = isCorrect ? 4 : 3
      scores.value = { posture: score, location: score, movement: score }

      currentStep.value = 'result'

      if (isCorrect) {
        markWordLearned()
        ElMessage.success('识别正确！')
      } else {
        ElMessage.warning('识别不准确，请多练习')
      }
    } else {
      ElMessage.error('识别失败: ' + data.message)
    }
  } catch (error) {
    console.error('❌ 识别过程出错:', error)
    ElMessage.error('识别失败: ' + error.message)
  } finally {
    isRecording.value = false
  }
}

function recordVideo(duration) {
  return new Promise((resolve, reject) => {
    if (!mediaStream) {
      reject(new Error('摄像头未启动'))
      return
    }
    const chunks = []
    const recorder = new MediaRecorder(mediaStream, { mimeType: 'video/webm' })
    recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data) }
    recorder.onstop = () => resolve(new Blob(chunks, { type: 'video/webm' }))
    recorder.onerror = () => reject(new Error('录制失败'))
    recorder.start()
    setTimeout(() => recorder.stop(), duration)
  })
}

// ============ 学习记录 ============
function markWordLearned() {
  if (!learnedWords.value.includes(selectedWordId.value)) {
    learnedWords.value.push(selectedWordId.value)
    localStorage.setItem('learnedWords', JSON.stringify(learnedWords.value))
  }
}

function retryPractice() {
  accuracy.value = 0
  lastRecognitionResult.value = null
  currentStep.value = 'camera'
}

function goToNextWord() {
  const currentIdx = allWords.value.findIndex(w => w.id === selectedWordId.value)
  const nextWord = allWords.value[(currentIdx + 1) % allWords.value.length]
  selectedWordId.value = nextWord.id
  accuracy.value = 0
  lastRecognitionResult.value = null
  currentStep.value = 'camera'
}

function markAsLearned() {
  markWordLearned()
  ElMessage.success('太棒了！已标记为已学会')
  const currentIdx = allWords.value.findIndex(w => w.id === selectedWordId.value)
  if (currentIdx < allWords.value.length - 1) {
    goToNextWord()
  } else {
    currentStep.value = 'select'
  }
}

// ============ 生命周期 ============
onMounted(async () => {
  await loadVocabulary()
  await initModel()
})

onUnmounted(() => {
  stopCamera()
})
</script>

<style scoped lang="scss">
.practice-page {
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

    .model-status {
      margin-left: auto;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: bold;
      display: flex;
      align-items: center;
      gap: 4px;

      &.status-ready {
        background: rgba(103, 194, 58, 0.1);
        color: #67c23a;
      }

      &.status-loading {
        background: rgba(230, 162, 60, 0.1);
        color: #e6a23c;
      }

      &.status-error {
        background: rgba(245, 108, 108, 0.1);
        color: #f56c6c;
      }
    }
  }
}

/* 词条选择区 */
.word-select-section {
  .section-title {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      color: #667eea;
    }
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }

  .word-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .word-card {
    background: #fff;
    border: 2px solid #e4e7ed;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    position: relative;

    &:hover {
      border-color: #667eea;
      transform: translateY(-2px);
    }

    &.selected {
      border-color: #667eea;
      background: #f0f5ff;
    }

    &.learned {
      opacity: 0.7;
    }

    .word-main {
      font-size: 22px;
      font-weight: bold;
      color: #333;
      margin-bottom: 10px;
    }

    .word-meta {
      display: flex;
      gap: 4px;
      justify-content: center;
      flex-wrap: wrap;
    }

    .word-status {
      position: absolute;
      top: 8px;
      right: 8px;
    }
  }

  .select-summary {
    display: flex;
    align-items: center;
    gap: 16px;
    background: #f9fafb;
    border-radius: 12px;
    padding: 16px 24px;
    font-size: 16px;

    strong {
      color: #667eea;
      font-size: 20px;
    }

    .el-button {
      margin-left: auto;
    }
  }
}

/* 摄像头练习区 */
.camera-section {
  .camera-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;

    .target-word {
      font-size: 18px;
      color: #333;

      strong {
        color: #667eea;
        font-size: 24px;
      }
    }
  }

  .camera-content {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 24px;
    margin-bottom: 20px;
  }

  .camera-wrapper {
    position: relative;
    background: #1a1a2e;
    border-radius: 16px;
    overflow: hidden;
    aspect-ratio: 4/3;
    display: flex;
    align-items: center;
    justify-content: center;

    .camera-video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transform: scaleX(-1);
    }

    .camera-overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;

      .overlay-content {
        text-align: center;
        color: #fff;

        .el-icon { color: #fff; margin-bottom: 16px; }
        p { margin-bottom: 20px; }
      }
    }

    .camera-guide {
      position: absolute;
      bottom: 16px;
      left: 16px;
      right: 16px;

      .guide-hint {
        background: rgba(0, 0, 0, 0.6);
        color: #fff;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .recording-indicator {
      position: absolute;
      top: 16px;
      right: 16px;
      background: rgba(245, 108, 108, 0.9);
      color: #fff;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 6px;

      .dot {
        width: 8px;
        height: 8px;
        background: #fff;
        border-radius: 50%;
        animation: blink 1s infinite;
      }
    }
  }

  .word-reference {
    .reference-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      height: 100%;

      .reference-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: bold;
        color: #333;
        margin-bottom: 16px;

        .el-icon { color: #e6a23c; }
      }

      .reference-tips {
        list-style: none;
        padding: 0;
        margin: 0;

        li {
          padding: 8px 0;
          color: #666;
          font-size: 14px;
          border-bottom: 1px dashed #f0f0f0;
          display: flex;
          align-items: center;
          gap: 8px;

          &::before {
            content: '•';
            color: #667eea;
            font-size: 18px;
          }

          &:last-child { border-bottom: none; }
        }
      }
    }
  }

  .camera-controls {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin-bottom: 20px;
  }

  .reference-demo {
    .demo-placeholder {
      background: #f5f7fa;
      border-radius: 12px;
      padding: 40px;
      text-align: center;
      border: 2px dashed #dcdfe6;

      .el-icon { color: #c0c4cc; margin-bottom: 16px; }
      p { font-size: 18px; color: #666; margin-bottom: 4px; }
      span { font-size: 14px; color: #999; }
    }
  }
}

/* 结果反馈区 */
.result-section {
  .result-card {
    background: #fff;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    max-width: 600px;
    margin: 0 auto;

    &.result-excellent .result-icon .el-icon { color: #67c23a; font-size: 80px; }
    &.result-good .result-icon .el-icon { color: #e6a23c; font-size: 80px; }
    &.result-poor .result-icon .el-icon { color: #f56c6c; font-size: 80px; }

    h3 {
      font-size: 28px;
      margin: 16px 0 8px;
    }

    .result-desc {
      color: #999;
      margin-bottom: 20px;
    }

    .compare-info {
      background: #f9fafb;
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 24px;
      text-align: left;
      border: 1px solid #e4e7ed;

      .compare-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #ebeef5;

        &:last-child { border-bottom: none; }

        .label {
          color: #666;
          font-size: 14px;
        }

        .value {
          font-weight: bold;
          font-size: 14px;

          &.match { color: #67c23a; }
          &.mismatch { color: #f56c6c; }
        }
      }
    }

    .accuracy-display {
      margin-bottom: 24px;

      .accuracy-ring {
        width: 140px;
        height: 140px;
        margin: 0 auto 12px;
        position: relative;

        svg {
          width: 100%;
          height: 100%;
        }

        .accuracy-text {
          position: absolute;
          inset: 0;
          display: flex;
          align-items: center;
          justify-content: center;

          .value {
            font-size: 36px;
            font-weight: bold;
            color: #333;
          }

          .unit {
            font-size: 16px;
            color: #999;
          }
        }
      }

      .accuracy-label {
        font-size: 13px;
        color: #999;
      }
    }

    .score-breakdown {
      text-align: left;
      background: #f9fafb;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 24px;

      .score-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;

        &:last-child { margin-bottom: 0; }

        .label {
          width: 50px;
          font-size: 14px;
          color: #666;
          font-weight: bold;
        }
      }
    }

    .result-actions {
      display: flex;
      gap: 12px;
      justify-content: center;
    }
  }
}

/* 示范练习区 */
.video-practice-section {
  .camera-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;

    .target-word {
      font-size: 18px;

      strong {
        color: #667eea;
        font-size: 24px;
      }
    }
  }

  .video-practice-content {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 24px;
    margin-bottom: 24px;
  }

  .demo-display {
    background: #1a1a2e;
    border-radius: 16px;
    overflow: hidden;
    display: flex;
    flex-direction: column;

    .demo-placeholder {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 300px;
      color: #fff;

      .el-icon { color: rgba(255,255,255,0.5); }
      p { font-size: 24px; margin: 16px 0 4px; }
      span { font-size: 14px; color: rgba(255,255,255,0.5); }
    }

    .playback-controls {
      background: rgba(0,0,0,0.5);
      padding: 12px 16px;
      display: flex;
      gap: 12px;
      justify-content: center;
    }
  }

  .practice-tips {
    .tips-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      height: 100%;

      .tips-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: bold;
        color: #333;
        margin-bottom: 16px;

        .el-icon { color: #667eea; }
      }

      .tips-steps {
        .step {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 10px 0;
          border-bottom: 1px solid #f0f0f0;

          &:last-child { border-bottom: none; }

          .step-num {
            width: 24px;
            height: 24px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            flex-shrink: 0;
          }

          .step-text {
            font-size: 14px;
            color: #666;
            line-height: 1.6;
          }
        }
      }
    }
  }

  .video-practice-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
  }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@media (max-width: 768px) {
  .camera-content,
  .video-practice-content {
    grid-template-columns: 1fr !important;
  }

  .select-summary {
    flex-wrap: wrap;
  }

  .word-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
}
</style>
