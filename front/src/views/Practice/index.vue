<template>
  <div class="practice-page">
    <!-- 视图一：词汇列表视图 -->
    <template v-if="isSelecting">
      <div class="page-header">
        <div class="header-nav">
          <el-button text @click="backToLearning">
            <el-icon><ArrowLeft /></el-icon>
            返回学习中心
          </el-button>
        </div>
        <h1>选择练习词汇</h1>
        <p class="subtitle">选择一个词汇开始手语识别练习</p>
      </div>

      <!-- 搜索栏 -->
      <div class="dict-filters">
        <el-input
          v-model="keyword"
          placeholder="搜索词汇..."
          clearable
          class="dict-search"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>

      <!-- 词汇列表 -->
      <div class="dict-main">
        <div class="dict-toolbar">
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button label="grid">
              <el-icon><Grid /></el-icon>
            </el-radio-button>
            <el-radio-button label="list">
              <el-icon><List /></el-icon>
            </el-radio-button>
          </el-radio-group>
        </div>

        <div v-if="loading" class="dict-loading">
          <div class="loading-text">加载中...</div>
        </div>

        <div v-else-if="filteredWords.length === 0" class="dict-empty">
          <p>未找到匹配的词汇</p>
          <el-button @click="resetFilters">重置筛选</el-button>
        </div>

        <div v-else :class="['dict-grid', viewMode]">
          <div
            v-for="word in paginatedWords"
            :key="word.id"
            class="dict-card"
            @click="openPracticeView(word)"
          >
            <div class="dict-card-inner">
              <span class="dict-word">{{ word.text || word.word }}</span>
            </div>
          </div>
        </div>

        <div class="dict-pagination" v-if="filteredWords.length > pageSize">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="filteredWords.length"
            layout="prev, pager, next"
          />
        </div>
      </div>
    </template>

    <!-- 视图二：识别视图 -->
    <template v-else>
      <div class="recognition-header">
        <div class="header-nav">
          <el-button text @click="backToList">
            <el-icon><ArrowLeft /></el-icon>
            返回词汇列表
          </el-button>
          <el-button text @click="backToLearning" class="back-learning-btn">
            <el-icon><HomeFilled /></el-icon>
            返回学习中心
          </el-button>
        </div>
        <div class="current-word-badge">
          当前练习: <strong>{{ selectedTargetText }}</strong>
        </div>
      </div>

      <div class="practice-layout">
        <!-- 左侧：控制面板 -->
        <div class="panel-card">
          <!-- 目标词汇展示 -->
          <div class="target-display active">
            <div class="target-label">目标词汇</div>
            <div class="target-word">{{ selectedTargetText || '--' }}</div>
            <div class="target-index" v-if="selectedWordIndex !== null">
              索引: {{ selectedWordIndex }}
            </div>
          </div>

          <!-- 摄像头预览 -->
          <div class="camera-container">
            <video ref="videoEl" autoplay muted playsinline></video>
            <div class="camera-placeholder" :class="{ hidden: !!mediaStream }">
              <span>点击"开始摄像头"启用预览</span>
            </div>
            <div class="recording-overlay" :class="{ active: isRecording }">
              <div class="recording-dot"></div>
              <span>录制中...</span>
            </div>
          </div>

          <!-- 阈值滑块 -->
          <div class="threshold-row">
            <label>判定阈值</label>
            <el-slider
              v-model="threshold"
              :min="50"
              :max="95"
              :step="5"
              :show-tooltip="false"
              style="flex: 1"
            />
            <div class="threshold-badge">{{ threshold }}%</div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              :type="mediaStream ? 'danger' : 'primary'"
              :disabled="isRecording"
              @click="toggleCamera"
            >
              {{ mediaStream ? '停止摄像头' : '开始摄像头' }}
            </el-button>
            <el-button
              type="primary"
              :disabled="!mediaStream || isRecording"
              @click="startVerify"
            >
              开始验证
            </el-button>
          </div>

          <!-- 状态提示 -->
          <div class="status-bar" :class="statusType">
            {{ statusText }}
          </div>
        </div>

        <!-- 右侧：结果显示 -->
        <div class="panel-card">
          <div class="panel-section-title">验证结果</div>

          <!-- 结果卡片 -->
          <div class="result-card" :class="resultClass">
            <div class="result-icon">{{ resultIcon }}</div>
            <div class="result-title">{{ resultTitle }}</div>
            <div class="result-detail">{{ resultDetail }}</div>
          </div>

          <!-- 正确度条 -->
          <div class="confidence-section">
            <div class="confidence-label-row">
              <span>正确度</span>
              <span class="confidence-pct">{{ displayConfidence }}</span>
            </div>
            <div class="confidence-bar-track">
              <div
                class="confidence-bar-fill"
                :class="{ low: displayConfidenceNum < threshold }"
                :style="{ width: displayConfidenceNum + '%' }"
              ></div>
            </div>
          </div>

          <!-- 对比信息 -->
          <div class="compare-table" v-if="hasResult">
            <div class="compare-row">
              <span class="row-label">目标词汇</span>
              <span class="row-value">{{ compareTarget }}</span>
            </div>
            <div class="compare-row">
              <span class="row-label">识别结果</span>
              <span class="row-value" :class="compareMatchClass">{{ compareResult }}</span>
            </div>
            <div class="compare-row">
              <span class="row-label">正确度</span>
              <span class="row-value">{{ compareConfidence }}</span>
            </div>
            <div class="compare-row">
              <span class="row-label">判定阈值</span>
              <span class="row-value">{{ threshold }}%</span>
            </div>
          </div>

          <!-- 历史记录 -->
          <div class="history-section">
            <div class="history-title">验证历史</div>
            <div class="history-list" v-if="history.length">
              <div
                v-for="(item, idx) in history"
                :key="idx"
                class="history-item"
              >
                <div class="history-icon" :class="item.correct ? 'ok' : 'fail'">
                  {{ item.correct ? '✓' : '✗' }}
                </div>
                <div class="history-info">
                  <div class="history-target">目标: {{ item.target }}</div>
                  <div class="history-detail">识别: {{ item.result }} · {{ item.confidencePct }}</div>
                </div>
                <div class="history-time">{{ item.time }}</div>
              </div>
            </div>
            <div class="history-empty" v-else>暂无历史记录</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Grid, List, ArrowLeft, HomeFilled } from '@element-plus/icons-vue'
import { recognitionApi } from '@/api'

const router = useRouter()

// 视图切换
const isSelecting = ref(true)

// 词汇表
const vocabulary = ref([])
const selectedWordIndex = ref(null)
const loading = ref(false)

// 筛选相关
const keyword = ref('')
const viewMode = ref('grid')
const currentPage = ref(1)
const pageSize = ref(40)

const categories = ['基础', '生活', '社会', '社交', '情感', '科技']
const scenes = ['日常问候', '家庭', '饮食', '职业', '人际', '表达']
const filters = ref({ category: '', scene: '', difficulty: '', region: '' })

// 筛选后的词汇
const filteredWords = computed(() => {
  let result = vocabulary.value
  if (keyword.value) {
    result = result.filter(w => (w.text || w.word || '').includes(keyword.value))
  }
  if (filters.value.category) {
    result = result.filter(w => w.category === filters.value.category)
  }
  if (filters.value.scene) {
    result = result.filter(w => w.scene === filters.value.scene)
  }
  if (filters.value.difficulty) {
    result = result.filter(w => w.difficulty === filters.value.difficulty)
  }
  if (filters.value.region) {
    result = result.filter(w => w.region === filters.value.region || w.region === '全国通用')
  }
  return result
})

const paginatedWords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredWords.value.slice(start, start + pageSize.value)
})

function getDifficultyLabel(difficulty) {
  const labels = { 1: '入门', 2: '基础', 3: '进阶' }
  return labels[difficulty] || '基础'
}

function resetFilters() {
  filters.value = { category: '', scene: '', difficulty: '', region: '' }
  keyword.value = ''
  currentPage.value = 1
}

// 摄像头
const videoEl = ref(null)
let mediaStream = null
let mediaRecorder = null
const recordedChunks = []
const isRecording = ref(false)
let recordingTimer = null
const RECORDING_DURATION = 3000

// 阈值
const threshold = ref(80)

// 状态
const statusText = ref('正在加载词汇表...')
const statusType = ref('')

// 结果
const resultIcon = ref('🎯')
const resultTitle = ref('等待验证')
const resultDetail = ref('请先选择词汇并录制手势')
const resultClass = ref('waiting')

// 对比
const compareTarget = ref('--')
const compareResult = ref('--')
const compareConfidence = ref('--')
const hasResult = ref(false)

// 历史
const history = ref([])

// 计算属性
const selectedTargetText = computed(() => {
  if (selectedWordIndex.value === null) return null
  const item = vocabulary.value.find(v => v.id === selectedWordIndex.value)
  return item ? (item.text || item.word) : null
})

const displayConfidence = computed(() => {
  if (compareConfidence.value === '--') return '--'
  return compareConfidence.value
})

const displayConfidenceNum = computed(() => {
  if (compareConfidence.value === '--') return 0
  const num = parseFloat(compareConfidence.value)
  return isNaN(num) ? 0 : num
})

const compareMatchClass = computed(() => {
  return compareTarget.value !== '--' && compareTarget.value === compareResult.value
    ? 'match'
    : 'mismatch'
})

// 加载词汇表
async function loadVocabulary() {
  try {
    const res = await recognitionApi.getVocabulary()
    if (res.success && res.vocabulary) {
      vocabulary.value = res.vocabulary
      loading.value = false
      statusText.value = '词汇表已加载，请选择词汇'
      statusType.value = 'ok'
    } else {
      throw new Error('词汇表加载失败')
    }
  } catch (e) {
    statusText.value = '词汇表加载失败，请刷新页面'
    statusType.value = 'error'
    console.error('[vocab] 加载失败:', e)
  }
}

// 初始化模型
async function initModel() {
  try {
    const res = await recognitionApi.initModel()
    if (res.success) {
      console.log('模型初始化成功')
    }
  } catch (e) {
    console.error('[model] 初始化失败:', e)
  }
}

// 打开练习视图
function openPracticeView(word) {
  selectedWordIndex.value = word.id
  isSelecting.value = false
  hasResult.value = false
  resetResult()
  statusText.value = `已选择词汇 "${selectedTargetText.value}"，请开始摄像头`
  statusType.value = ''
}

// 返回列表
function backToList() {
  isSelecting.value = true
  cleanup()
  resetResult()
  statusText.value = '词汇表已加载，请选择词汇'
  statusType.value = 'ok'
}

// 返回学习中心
function backToLearning() {
  cleanup()
  router.push('/learning')
}

// 词汇选择变化
function onWordChange(idx) {
  hasResult.value = false
  resetResult()
  if (idx !== null) {
    statusText.value = `已选择词汇 "${selectedTargetText.value}"，请开始摄像头`
    statusType.value = ''
  } else {
    statusText.value = '请选择词汇'
    statusType.value = ''
  }
}

// 切换摄像头
async function toggleCamera() {
  if (mediaStream) {
    stopCamera()
    statusText.value = '摄像头已停止'
    statusType.value = ''
  } else {
    await startCamera()
  }
}

async function startCamera() {
  try {
    statusText.value = '正在启动摄像头...'
    statusType.value = 'warn'
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' },
      audio: false
    })
    if (videoEl.value) {
      videoEl.value.srcObject = mediaStream
    }
    const msg = selectedWordIndex.value !== null
      ? '摄像头已启动，请做手势'
      : '摄像头已启动，请先选择词汇'
    statusText.value = msg
    statusType.value = 'ok'
  } catch (e) {
    statusText.value = '摄像头启动失败，请检查权限'
    statusType.value = 'error'
    console.error('[camera] 启动失败:', e)
  }
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(t => t.stop())
    mediaStream = null
  }
  if (videoEl.value) {
    videoEl.value.srcObject = null
  }
}

// 开始验证
async function startVerify() {
  if (!mediaStream || selectedWordIndex.value === null) return

  isRecording.value = true
  statusText.value = '正在录制视频...'
  statusType.value = 'warn'
  recordedChunks.length = 0

  const mimeType = 'video/webm;codecs=vp8,opus'
  try {
    mediaRecorder = new MediaRecorder(mediaStream, {
      mimeType: mimeType.startsWith('video/webm') ? mimeType : 'video/webm'
    })
  } catch (e) {
    mediaRecorder = new MediaRecorder(mediaStream)
  }

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) recordedChunks.push(e.data)
  }

  mediaRecorder.onstop = async () => {
    await performVerification()
  }

  mediaRecorder.start()
  statusText.value = '录制中...'
  recordingTimer = setTimeout(() => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop()
    }
  }, RECORDING_DURATION)
}

// 执行验证
async function performVerification() {
  if (recordedChunks.length === 0) {
    ElMessage.error('录制失败，未获取到视频数据')
    isRecording.value = false
    statusText.value = '录制失败，请重试'
    statusType.value = 'error'
    return
  }

  const blob = new Blob(recordedChunks, { type: 'video/webm' })
  const targetIdx = selectedWordIndex.value

  statusText.value = '正在处理视频...'
  statusType.value = 'warn'

  try {
    const res = await recognitionApi.predict(blob, targetIdx)
    console.log('[verify] 识别响应:', res)

    if (res.success) {
      const rd = res.data ?? res
      const rawPredicted = rd.predicted ?? rd.result ?? '未知'
      const rawTargetConf = rd.target_confidence ?? 0

      const predicted = (typeof rawPredicted === 'string' && rawPredicted !== 'undefined') ? rawPredicted : '未知'
      const conf = Number.isNaN(rawTargetConf) ? 0 : Math.max(0, Math.min(1, rawTargetConf))
      const confPct = (conf * 100).toFixed(1) + '%'
      const isCorrect = conf >= threshold.value / 100

      compareTarget.value = selectedTargetText.value
      compareResult.value = predicted
      compareConfidence.value = confPct
      hasResult.value = true

      if (isCorrect) {
        resultIcon.value = '✓'
        resultTitle.value = '正确！'
        resultDetail.value = `目标词 "${selectedTargetText.value}" 正确度 ${confPct}`
        resultClass.value = 'success'
        statusText.value = '验证通过！手势识别正确'
        statusType.value = 'ok'
      } else {
        resultIcon.value = '✗'
        resultTitle.value = '错误'
        resultDetail.value = `目标词 "${selectedTargetText.value}" 正确度 ${confPct}（识别为 "${predicted}"）`
        resultClass.value = 'failure'
        statusText.value = '验证失败，正确度未达标'
        statusType.value = 'error'
      }

      const now = new Date()
      const timeStr = now.toLocaleTimeString('zh-CN', { hour12: false })
      history.value.unshift({
        correct: isCorrect,
        target: selectedTargetText.value,
        result: predicted,
        confidencePct: confPct,
        time: timeStr
      })
      if (history.value.length > 10) history.value.pop()

    } else {
      resultIcon.value = '✗'
      resultTitle.value = '验证失败'
      resultDetail.value = res.message || '无法完成识别'
      resultClass.value = 'failure'
      statusText.value = `验证失败: ${res.message}`
      statusType.value = 'error'
      hasResult.value = false
    }
  } catch (e) {
    console.error('[verify] 请求失败:', e)
    resultIcon.value = '✗'
    resultTitle.value = '验证失败'
    resultDetail.value = '请求失败，请检查后端服务'
    resultClass.value = 'failure'
    statusText.value = '验证请求失败，请重试'
    statusType.value = 'error'
  } finally {
    isRecording.value = false
    if (recordingTimer) {
      clearTimeout(recordingTimer)
      recordingTimer = null
    }
  }
}

function resetResult() {
  resultIcon.value = '🎯'
  resultTitle.value = '等待验证'
  resultDetail.value = '请先选择词汇并录制手势'
  resultClass.value = 'waiting'
  compareTarget.value = '--'
  compareResult.value = '--'
  compareConfidence.value = '--'
}

function cleanup() {
  stopCamera()
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    try { mediaRecorder.stop() } catch (e) {}
  }
  if (recordingTimer) {
    clearTimeout(recordingTimer)
  }
}

onMounted(async () => {
  loading.value = true
  await loadVocabulary()
  await initModel()
})

onUnmounted(() => {
  cleanup()
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
$space-1: 8px;
$space-2: 16px;
$space-3: 24px;

.practice-page {
  max-width: 1100px;
  margin: 0 auto;
  min-height: calc(100vh - 60px);
  padding: 48px 32px 80px;
  background: $paper;
  margin-bottom: 40px;

  .page-header {
    text-align: center;
    margin-bottom: 40px;

    .header-nav {
      display: flex;
      justify-content: flex-start;
      margin-bottom: 12px;

      .el-button {
        color: #8a8a8a;
      }
    }

    h1 {
      font-size: 28px;
      font-weight: 700;
      color: $ink;
      margin: 0 0 8px;
    }

    .subtitle {
      color: $ink-faint;
      font-size: 14px;
      margin: 0;
    }
  }

  // 识别视图头部
  .recognition-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    padding: 0 8px;

    .header-nav {
      display: flex;
      align-items: center;
      gap: 4px;

      .back-learning-btn {
        color: #409eff;
      }
    }

    .current-word-badge {
      font-size: 14px;
      color: $ink-light;

      strong {
        color: $accent;
        font-weight: 600;
      }
    }
  }

  // 词典样式复用
  .dict-filters {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 24px;
    background: $white;
    border: 1px solid $ink-line;
    border-radius: 8px;
    padding: 16px 20px;

    .dict-search {
      width: 180px;

      :deep(.el-input__wrapper) {
        border-radius: 6px;
      }
    }

    .dict-select {
      width: 110px;

      :deep(.el-input__wrapper) {
        border-radius: 6px;
      }
    }
  }

  .dict-main {
    background: $white;
    border: 1px solid $ink-line;
    border-radius: 8px;
    padding: 20px 24px;

      .dict-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;

      :deep(.el-radio-button__inner) {
        border-radius: 4px;
      }
    }
  }

  .dict-loading,
  .dict-empty {
    padding: 80px 0;
    text-align: center;
    color: $ink-faint;
    font-size: 14px;

    .loading-text {
      color: $ink-faint;
    }
  }

  .dict-empty p {
    margin-bottom: 16px;
  }

  .dict-grid {
    &.grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 10px;

      .dict-card {
        padding: 20px 14px;
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 8px;
      }
    }

    &.list {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .dict-card {
        padding: 14px 16px;
        flex-direction: row;
        align-items: center;
        gap: 12px;

        .dict-card-inner {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .dict-tags {
          margin-bottom: 0;
        }

        .dict-meta {
          margin-left: auto;
        }
      }
    }

    .dict-card {
      background: $paper-warm;
      border: 1px solid transparent;
      border-radius: 8px;
      cursor: pointer;
      transition: all 180ms ease;
      display: flex;

      &:hover {
        background: $white;
        border-color: $ink-ghost;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
      }

      .dict-card-inner {
        .dict-word {
          font-size: 20px;
          font-weight: 600;
          color: $ink;
        }
      }

      .dict-tags {
        display: flex;
        gap: 5px;
        flex-wrap: wrap;
      }

      .dict-meta {
        display: flex;
        gap: 8px;
        font-size: 11px;
        color: $ink-ghost;
      }
    }
  }

  .dict-pagination {
    margin-top: 24px;
    display: flex;
    justify-content: center;
  }

  // 识别视图布局
  .practice-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    max-width: 1100px;
    margin: 0 auto;

    @media (max-width: 900px) {
      grid-template-columns: 1fr;
    }
  }

  .panel-card {
    background: $white;
    border: 1px solid $ink-line;
    border-radius: 8px;
    padding: $space-3;
    display: flex;
    flex-direction: column;
    gap: $space-2;

    .panel-section-title {
      font-size: 17px;
      font-weight: 600;
      color: $ink;
      margin-bottom: 4px;
    }

    .panel-section {
      .field-label {
        display: block;
        font-size: 13px;
        font-weight: 500;
        color: $ink-light;
        margin-bottom: 8px;
      }
    }

    .target-display {
      background: $paper-warm;
      border: 2px solid rgba(26, 26, 26, 0.12);
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      transition: all 280ms cubic-bezier(0.16, 1, 0.3, 1);

      &.active {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.06), $white);
        border-color: rgba(26, 26, 26, 0.25);
      }

      .target-label {
        color: $ink-faint;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .target-word {
        font-size: 36px;
        font-weight: 800;
        color: $accent;
        margin-top: 8px;
      }

      .target-index {
        margin-top: 6px;
        font-size: 13px;
        color: $ink-faint;
      }
    }

    .camera-container {
      position: relative;
      width: 100%;
      aspect-ratio: 4 / 3;
      background: #1a1a2e;
      border-radius: 12px;
      overflow: hidden;

      video {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .camera-placeholder {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #555;
        font-size: 14px;

        &.hidden {
          display: none;
        }
      }

      .recording-overlay {
        position: absolute;
        top: 12px;
        left: 12px;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba($error, 0.9);
        color: #fff;
        font-size: 12px;
        font-weight: 600;
        display: none;
        align-items: center;
        gap: 6px;

        &.active {
          display: flex;
        }

        .recording-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #fff;
          animation: pulse 1s ease-in-out infinite;
        }
      }
    }

    .threshold-row {
      display: flex;
      align-items: center;
      gap: $space-2;
      padding: 12px 16px;
      background: $paper-warm;
      border-radius: 8px;
      border: 1px solid $ink-line;

      label {
        font-size: 13px;
        font-weight: 500;
        color: $ink-light;
        white-space: nowrap;
      }

      .threshold-badge {
        min-width: 44px;
        padding: 4px 10px;
        background: $accent;
        color: #fff;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        text-align: center;
      }
    }

    .action-buttons {
      display: flex;
      gap: $space-1;

      .el-button {
        flex: 1;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
      }
    }

    .status-bar {
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 13px;
      line-height: 1.5;
      background: $paper-warm;
      border: 1px solid $ink-line;
      color: $ink-faint;

      &.ok {
        background: rgba($success, 0.06);
        border-color: rgba($success, 0.2);
        color: darken($success, 8%);
      }

      &.error {
        background: rgba($error, 0.06);
        border-color: rgba($error, 0.2);
        color: $error;
      }

      &.warn {
        background: rgba($warn, 0.06);
        border-color: rgba($warn, 0.2);
        color: $warn;
      }
    }
  }

  .result-card {
    padding: 24px;
    border-radius: 12px;
    text-align: center;

    &.waiting {
      background: rgba($ink-faint, 0.06);
      border: 2px solid rgba($ink-faint, 0.15);

      .result-icon { font-size: 40px; }
      .result-title { color: $ink-faint; font-size: 22px; font-weight: 700; margin: 8px 0 4px; }
      .result-detail { font-size: 13px; color: $ink-faint; }
    }

    &.success {
      background: linear-gradient(135deg, rgba($success, 0.1), $white);
      border: 2px solid rgba($success, 0.35);

      .result-icon { font-size: 40px; }
      .result-title { color: $success; font-size: 22px; font-weight: 700; margin: 8px 0 4px; }
      .result-detail { font-size: 13px; color: $ink-light; }
    }

    &.failure {
      background: linear-gradient(135deg, rgba($error, 0.1), $white);
      border: 2px solid rgba($error, 0.35);

      .result-icon { font-size: 40px; }
      .result-title { color: $error; font-size: 22px; font-weight: 700; margin: 8px 0 4px; }
      .result-detail { font-size: 13px; color: $ink-light; }
    }
  }

  .confidence-section {
    .confidence-label-row {
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      margin-bottom: 8px;
      color: $ink-light;

      .confidence-pct {
        font-weight: 600;
      }
    }

    .confidence-bar-track {
      height: 10px;
      background: $ink-line;
      border-radius: 5px;
      overflow: hidden;

      .confidence-bar-fill {
        height: 100%;
        border-radius: 5px;
        background: linear-gradient(90deg, $accent, $success);
        transition: width 400ms cubic-bezier(0.16, 1, 0.3, 1);

        &.low {
          background: linear-gradient(90deg, $warn, $error);
        }
      }
    }
  }

  .compare-table {
    border: 1px solid $ink-line;
    border-radius: 8px;
    overflow: hidden;

    .compare-row {
      display: flex;
      justify-content: space-between;
      padding: 10px 14px;
      border-bottom: 1px solid $ink-line;
      font-size: 13px;

      &:last-child { border-bottom: none; }

      .row-label { color: $ink-faint; }
      .row-value { font-weight: 600; color: $ink; }

      .row-value.match { color: $success; }
      .row-value.mismatch { color: $error; }
    }
  }

  .history-section {
    .history-title {
      font-size: 15px;
      font-weight: 600;
      color: $ink;
      margin-bottom: 12px;
    }

    .history-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: 240px;
      overflow-y: auto;
    }

    .history-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: $paper-warm;
      border: 1px solid $ink-line;
      border-radius: 8px;
      font-size: 13px;

      .history-icon {
        font-size: 18px;
        flex-shrink: 0;
        &.ok { color: $success; }
        &.fail { color: $error; }
      }

      .history-info {
        flex: 1;
        .history-target { font-weight: 600; color: $ink; }
        .history-detail { color: $ink-faint; margin-top: 2px; }
      }

      .history-time {
        color: $ink-faint;
        font-size: 12px;
        flex-shrink: 0;
      }
    }

    .history-empty {
      color: $ink-faint;
      font-size: 13px;
      text-align: center;
      padding: 24px;
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@media (max-width: 768px) {
  .practice-page {
    padding: 32px 16px 60px;

    .dict-filters {
      padding: 12px 14px;

      .dict-search {
        width: 100%;
      }

      .dict-select {
        flex: 1;
        min-width: 90px;
      }
    }

    .dict-main {
      padding: 16px;
    }

    .dict-grid.grid {
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;

      .dict-card {
        padding: 16px 8px;

        .dict-word {
          font-size: 17px;
        }
      }
    }
  }
}
</style>
