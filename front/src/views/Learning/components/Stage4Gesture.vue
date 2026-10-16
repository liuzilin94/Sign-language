<template>
  <div class="stage-gesture">
    <div class="stage-header">
      <div class="stage-badge stage4">
        <span class="badge-num">4</span>
        <span class="badge-text">手势识别</span>
      </div>
      <h2 class="target-word">
        请打出「<span>{{ question.word }}</span>」的手势
      </h2>
    </div>

    <!-- 摄像头预览 -->
    <div class="camera-container">
      <video ref="videoEl" autoplay muted playsinline></video>
      <div class="camera-placeholder" :class="{ hidden: !!mediaStream }">
        <el-icon><VideoCamera /></el-icon>
        <span>点击"开始摄像头"启用预览</span>
      </div>
      <div class="recording-overlay" :class="{ active: isRecording }">
        <div class="recording-dot"></div>
        <span>录制中...</span>
      </div>
    </div>

    <!-- 阈值设置 -->
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
        size="large"
        @click="toggleCamera"
      >
        <el-icon><VideoCamera v-if="!mediaStream" /><VideoPause v-else /></el-icon>
        {{ mediaStream ? '停止摄像头' : '开始摄像头' }}
      </el-button>
      <el-button
        type="success"
        size="large"
        :disabled="!mediaStream || isRecording"
        @click="startRecording"
      >
        <el-icon><Camera /></el-icon>
        开始验证
      </el-button>
    </div>

    <!-- 结果显示 -->
    <div v-if="showResult" class="result-section" :class="resultClass">
      <div class="result-icon">{{ resultIcon }}</div>
      <div class="result-text">{{ resultText }}</div>
      <div v-if="confidence !== null" class="result-confidence">
        正确度：{{ confidence }}%
      </div>
    </div>

    <!-- 状态提示 -->
    <div class="status-bar" :class="statusType">
      {{ statusText }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { recognitionApi } from '@/api'

const props = defineProps({
  question: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['answer'])

// 词汇表
const vocabulary = ref([])

// 摄像头
const videoEl = ref(null)
let mediaStream = null
let mediaRecorder = null
const recordedChunks = []
const isRecording = ref(false)
let recordingTimer = null
const RECORDING_DURATION = 3000

// 状态
const threshold = ref(80)
const statusText = ref('正在加载...')
const statusType = ref('')

// 结果
const showResult = ref(false)
const resultIcon = ref('')
const resultText = ref('')
const resultClass = ref('')
const confidence = ref(null)

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

    statusText.value = '摄像头已启动，请做出手势'
    statusType.value = 'ok'
  } catch (e) {
    statusText.value = '摄像头启动失败，请检查权限'
    statusType.value = 'error'
    ElMessage.error('摄像头启动失败，请检查权限设置')
  }
}

// 加载词汇表
async function loadVocabulary() {
  try {
    const res = await recognitionApi.getVocabulary()
    if (res.success && res.vocabulary) {
      vocabulary.value = res.vocabulary
      statusText.value = '请先启动摄像头'
      statusType.value = 'ok'
    } else {
      throw new Error('词汇表加载失败')
    }
  } catch (e) {
    statusText.value = '词汇表加载失败'
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

// 根据词汇文本查找索引
function findWordIndex(wordText) {
  if (!wordText || vocabulary.value.length === 0) return null
  const item = vocabulary.value.find(v => (v.text || v.word) === wordText)
  return item ? item.id : null
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

// 开始录制
async function startRecording() {
  if (!mediaStream) return

  isRecording.value = true
  statusText.value = '正在录制视频...'
  statusType.value = 'warn'
  recordedChunks.length = 0

  const mimeType = 'video/webm;codecs=vp8,opus'
  try {
    mediaRecorder = new MediaRecorder(mediaStream, {
      mimeType: mimeType.startsWith('video/webm') ? mimeType : 'video/webm'
    })
  } catch {
    mediaRecorder = new MediaRecorder(mediaStream)
  }

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) recordedChunks.push(e.data)
  }

  mediaRecorder.onstop = async () => {
    await performRecognition()
  }

  mediaRecorder.start()
  statusText.value = '录制中...'

  recordingTimer = setTimeout(() => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop()
    }
  }, RECORDING_DURATION)
}

// 执行识别
async function performRecognition() {
  if (recordedChunks.length === 0) {
    ElMessage.error('录制失败，未获取到视频数据')
    isRecording.value = false
    statusText.value = '录制失败，请重试'
    statusType.value = 'error'
    return
  }

  const blob = new Blob(recordedChunks, { type: 'video/webm' })
  const targetWordText = props.question.word || props.question.text

  statusText.value = '正在处理视频...'
  statusType.value = 'warn'

  try {
    // 使用与小试牛刀相同的方式：通过词汇文本查找索引
    const targetIdx = findWordIndex(targetWordText)

    if (targetIdx === null) {
      console.error('[verify] 无法找到词汇索引:', targetWordText, 'vocabulary:', vocabulary.value)
      throw new Error('无法找到词汇索引')
    }

    console.log('[verify] 目标词汇:', targetWordText, '索引:', targetIdx)

    // 调用识别API
    const res = await recognitionApi.predict(blob, targetIdx)
    console.log('[verify] 识别响应:', res)

    if (res.success) {
      // 使用与小试牛刀相同的响应处理方式
      const rd = res.data ?? res
      const rawPredicted = rd.predicted ?? rd.result ?? '未知'
      const rawTargetConf = rd.target_confidence ?? 0

      const predicted = (typeof rawPredicted === 'string' && rawPredicted !== 'undefined') ? rawPredicted : '未知'
      const conf = Number.isNaN(rawTargetConf) ? 0 : Math.max(0, Math.min(1, rawTargetConf))
      const confPct = Math.round(conf * 100)
      confidence.value = confPct

      console.log('[verify] 预测结果:', predicted, '置信度:', confPct + '%')

      const isCorrect = conf >= threshold.value / 100

      if (isCorrect) {
        resultIcon.value = '✓'
        resultText.value = '正确！手势识别成功'
        resultClass.value = 'success'
        statusText.value = '验证通过！'
        statusType.value = 'ok'
      } else {
        resultIcon.value = '✗'
        resultText.value = `回答错误（识别为"${predicted}"）`
        resultClass.value = 'error'
        statusText.value = '验证失败，正确度未达标'
        statusType.value = 'error'
      }

      showResult.value = true

      // 发送结果
      setTimeout(() => {
        emit('answer', isCorrect)
      }, 1500)
    } else {
      console.error('[verify] 识别失败:', res.message)
      throw new Error(res.message || '识别失败')
    }
  } catch (e) {
    console.error('识别失败:', e)
    resultIcon.value = '✗'
    resultText.value = '识别失败，请重试'
    resultClass.value = 'error'
    showResult.value = true
    statusText.value = '识别失败'
    statusType.value = 'error'

    // 发送失败结果
    setTimeout(() => {
      emit('answer', false)
    }, 1500)
  } finally {
    isRecording.value = false
    if (recordingTimer) {
      clearTimeout(recordingTimer)
      recordingTimer = null
    }
  }
}

// 清理
function cleanup() {
  stopCamera()
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    try { mediaRecorder.stop() } catch {}
  }
  if (recordingTimer) {
    clearTimeout(recordingTimer)
  }
}

// 题目切换时重置状态
watch(
  () => props.question ? `${props.question.word_id}-${props.question.stage}` : '',
  () => {
    showResult.value = false
    resultIcon.value = ''
    resultText.value = ''
    resultClass.value = ''
    confidence.value = null
    statusText.value = '正在加载...'
    statusType.value = 'warn'
  }
)

// 组件挂载时初始化
onMounted(async () => {
  statusText.value = '正在加载...'
  statusType.value = 'warn'
  await loadVocabulary()
  await initModel()
})

// 组件卸载时清理
onUnmounted(cleanup)
</script>

<style scoped lang="scss">
.stage-gesture {
  background: #fff;
  border-radius: 16px;
  padding: 32px 24px;
}

.stage-header {
  text-align: center;
  margin-bottom: 24px;

  .stage-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
    border-radius: 20px;
    margin-bottom: 16px;

    .badge-num {
      width: 20px;
      height: 20px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 700;
      color: #fff;
    }

    .badge-text {
      font-size: 14px;
      font-weight: 500;
      color: #fff;
    }
  }

  .target-word {
    font-size: 20px;
    font-weight: 600;
    color: #0d0d0d;
    margin: 0;

    span {
      color: #67c23a;
      font-weight: 700;
    }
  }
}

.camera-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  background: #1a1a2e;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;

  video {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .camera-placeholder {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #555;
    font-size: 14px;

    .el-icon {
      font-size: 48px;
      margin-bottom: 12px;
    }

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
    background: rgba(#f56c6c, 0.9);
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
  gap: 12px;
  padding: 12px 16px;
  background: #fafaf8;
  border-radius: 8px;
  margin-bottom: 16px;

  label {
    font-size: 14px;
    font-weight: 500;
    color: #3a3a3a;
    white-space: nowrap;
  }

  .threshold-badge {
    min-width: 44px;
    padding: 4px 10px;
    background: #0d0d0d;
    color: #fff;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    text-align: center;
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;

  .el-button {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }
}

.result-section {
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 16px;

  &.success {
    background: linear-gradient(135deg, rgba(#67c23a, 0.1), #fff);
    border: 2px solid rgba(#67c23a, 0.3);
  }

  &.error {
    background: linear-gradient(135deg, rgba(#f56c6c, 0.1), #fff);
    border: 2px solid rgba(#f56c6c, 0.3);
  }

  .result-icon {
    font-size: 48px;
    margin-bottom: 8px;
  }

  .result-text {
    font-size: 18px;
    font-weight: 600;
    color: #0d0d0d;
    margin-bottom: 4px;
  }

  .result-confidence {
    font-size: 14px;
    color: #8a8a8a;
  }
}

.status-bar {
  padding: 12px 14px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  background: #fafaf8;
  border: 1px solid #e8e8e8;
  color: #8a8a8a;

  &.ok {
    background: rgba(#67c23a, 0.06);
    border-color: rgba(#67c23a, 0.2);
    color: #67c23a;
  }

  &.error {
    background: rgba(#f56c6c, 0.06);
    border-color: rgba(#f56c6c, 0.2);
    color: #f56c6c;
  }

  &.warn {
    background: rgba(#e6a23c, 0.06);
    border-color: rgba(#e6a23c, 0.2);
    color: #e6a23c;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
