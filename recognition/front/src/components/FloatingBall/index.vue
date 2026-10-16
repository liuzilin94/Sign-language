<template>
  <Teleport to="body">
    <!-- 悬浮球（弹窗打开时隐藏） -->
    <div
      v-if="!isExpanded"
      class="floating-ball"
      :class="{ dragging: isBallDragging }"
      :style="ballStyle"
      @click="handleClick"
    >
      <div
        class="ball-icon"
        @mousedown.stop="startBallDrag"
        @touchstart.prevent.stop="startBallDrag"
      >
        <el-icon><ChatDotRound /></el-icon>
      </div>
    </div>

    <!-- 聊天弹窗（独立位置） -->
    <div
      v-if="isExpanded"
      class="chat-panel"
      :class="{ dragging: isPanelDragging }"
      :style="panelStyle"
      @mousedown="startPanelDrag"
      @touchstart.prevent="startPanelDrag"
    >
      <div class="panel-header">
        <span>AI 手语助手</span>
        <div class="header-actions">
          <el-tag v-if="isTyping" type="info" size="small" effect="plain">思考中...</el-tag>
          <el-button type="text" size="small" @click.stop="clearChat">
            <el-icon><Delete /></el-icon>
          </el-button>
          <el-button type="text" size="small" @click.stop="closePanel">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="messages" ref="messagesRef">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="['message', msg.role]"
        >
          <div class="message-content" v-html="formatContent(msg.content)"></div>
        </div>

        <!-- 思考中提示 -->
        <div v-if="isTyping" class="message assistant">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
      <div class="quick-suggestions" v-if="messages.length === 1 && messages[0].role === 'assistant'">
        <el-button
          v-for="suggestion in quickSuggestions"
          :key="suggestion"
          size="small"
          type="primary"
          plain
          @click="sendMessage(suggestion)"
        >
          {{ suggestion }}
        </el-button>
      </div>
      <div class="input-area">
        <el-input
          v-model="inputText"
          placeholder="输入你的手语问题..."
          size="small"
          @keyup.enter="sendMessage"
          :disabled="isTyping"
        >
          <template #append>
            <el-button @click="sendMessage" :loading="isTyping">
              <el-icon><Promotion /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, watch, computed } from 'vue'
import { ChatDotRound, Close, Delete, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const isExpanded = ref(false)

// 悬浮球位置（独立）
const ballPosition = reactive({ x: 0, y: 0 })
// 弹窗位置（独立）
const panelPosition = reactive({ x: 0, y: 0 })

const inputText = ref('')
const messages = ref([])
const messagesRef = ref(null)
const isBallDragging = ref(false)
const isPanelDragging = ref(false)
const isTyping = ref(false)
let ballJustDragged = false
let panelJustDragged = false

// 智谱AI API配置（GLM-5模型 - 通过百炼调用）
const ZHIPU_API_KEY = import.meta.env.VITE_DASHSCOPE_API_KEY || 'sk-e121784bebcb4865a1d9e6dd287cb3cf'
const ZHIPU_API_URL = import.meta.env.VITE_DASHSCOPE_API_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
const MODEL_NAME = 'glm-5'  // GLM-5模型（百炼平台）

// 快捷建议
const quickSuggestions = [
  '手语"你好"怎么做？',
  '手语"谢谢"的动作要点',
  '如何提高手语识别准确率？',
  '这个词汇的示范视频在哪里看？'
]

// 格式化内容（处理Markdown）
function formatContent(content) {
  if (!content) return ''
  
  let html = content
    // 转义HTML特殊字符
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // 代码块 ```code```
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // 行内代码 `code`
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 标题 ### 标题
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    // 标题 ## 标题
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    // 标题 # 标题
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    // 粗体 **text**
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // 斜体 *text*
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // 无序列表 - item
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // 有序列表 1. item
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // 包裹连续的li为ul
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    // 换行
    .replace(/\n/g, '<br>')
    // 清理多余的br在ul/ol内
    .replace(/<ul><br>/g, '<ul>')
    .replace(/<\/li><br>/g, '</li>')
  
  return html
}

const ballSize = 50
const panelWidth = 350
const panelHeight = 500

// 从localStorage加载悬浮球位置
function loadBallPosition() {
  try {
    const saved = localStorage.getItem('floatingBallPosition')
    if (saved) {
      const pos = JSON.parse(saved)
      ballPosition.x = Math.max(0, Math.min(window.innerWidth - ballSize, pos.x))
      ballPosition.y = Math.max(0, Math.min(window.innerHeight - ballSize, pos.y))
    } else {
      // 默认位置：右下角
      ballPosition.x = window.innerWidth - ballSize - 10
      ballPosition.y = window.innerHeight / 2 - ballSize / 2
    }
  } catch (e) {
    ballPosition.x = window.innerWidth - ballSize - 10
    ballPosition.y = window.innerHeight / 2 - ballSize / 2
  }
}

// 从localStorage加载弹窗位置（仅用于初始打开位置）
function loadPanelPosition() {
  try {
    const saved = localStorage.getItem('chatPanelPosition')
    if (saved) {
      const pos = JSON.parse(saved)
      panelPosition.x = Math.max(0, Math.min(window.innerWidth - panelWidth, pos.x))
      panelPosition.y = Math.max(0, Math.min(window.innerHeight - panelHeight, pos.y))
    }
  } catch (e) {
    // 加载失败时使用默认位置
  }
}

// 保存悬浮球位置
function saveBallPosition() {
  try {
    localStorage.setItem('floatingBallPosition', JSON.stringify({
      x: ballPosition.x,
      y: ballPosition.y
    }))
  } catch (e) {
    // localStorage写入失败时忽略
  }
}

// 保存弹窗位置
function savePanelPosition() {
  try {
    localStorage.setItem('chatPanelPosition', JSON.stringify({
      x: panelPosition.x,
      y: panelPosition.y
    }))
  } catch (e) {
    // localStorage写入失败时忽略
  }
}

const ballStyle = computed(() => ({
  left: ballPosition.x + 'px',
  top: ballPosition.y + 'px'
}))

const panelStyle = computed(() => ({
  left: panelPosition.x + 'px',
  top: panelPosition.y + 'px'
}))

onMounted(() => {
  loadBallPosition()
  loadPanelPosition()
  
  // 窗口大小改变时调整位置
  const handleResize = () => {
    ballPosition.x = Math.max(0, Math.min(window.innerWidth - ballSize, ballPosition.x))
    ballPosition.y = Math.max(0, Math.min(window.innerHeight - ballSize, ballPosition.y))
    panelPosition.x = Math.max(0, Math.min(window.innerWidth - panelWidth, panelPosition.x))
    panelPosition.y = Math.max(0, Math.min(window.innerHeight - panelHeight, panelPosition.y))
    saveBallPosition()
    savePanelPosition()
  }
  window.addEventListener('resize', handleResize)

  // 添加欢迎消息
  messages.value = [{
    role: 'assistant',
    content: '你好！我是你的AI手语学习助手。我可以帮你：\n• 解答手语动作疑问\n• 提供学习建议\n• 分析识别结果\n• 推荐练习方法\n\n请问有什么可以帮你的吗？',
    timestamp: Date.now()
  }]
})

// 监听消息自动滚动
watch(messages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

// 点击悬浮球打开/关闭弹窗
function handleClick() {
  // 如果刚刚拖拽过，不触发点击事件
  if (ballJustDragged) {
    ballJustDragged = false
    return
  }
  if (isExpanded.value) {
    closePanel()
  } else {
    openPanel()
  }
}

function openPanel() {
  isExpanded.value = true
  // 打开弹窗时，将弹窗定位到悬浮球附近
  panelPosition.x = ballPosition.x
  panelPosition.y = ballPosition.y - panelHeight - 10
  // 如果上方空间不足，就显示在悬浮球下方
  if (panelPosition.y < 0) {
    panelPosition.y = ballPosition.y + ballSize + 10
  }
  // 确保弹窗不超出屏幕边界
  panelPosition.x = Math.max(0, Math.min(window.innerWidth - panelWidth, panelPosition.x))
  panelPosition.y = Math.max(0, Math.min(window.innerHeight - panelHeight, panelPosition.y))
}

function closePanel() {
  isExpanded.value = false
  // 关闭弹窗时不保存弹窗位置，下次打开时会回到上次保存的位置
  // 悬浮球位置保持不变
}

// 悬浮球拖拽
function startBallDrag(e) {
  e.preventDefault()
  isBallDragging.value = false
  ballJustDragged = false

  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const clientY = e.touches ? e.touches[0].clientY : e.clientY
  const startPos = { x: clientX - ballPosition.x, y: clientY - ballPosition.y }

  const moveHandler = (moveEvent) => {
    moveEvent.preventDefault()
    const clientX = moveEvent.touches ? moveEvent.touches[0].clientX : moveEvent.clientX
    const clientY = moveEvent.touches ? moveEvent.touches[0].clientY : moveEvent.clientY

    const newX = clientX - startPos.x
    const newY = clientY - startPos.y

    if (!isBallDragging.value && (Math.abs(newX - ballPosition.x) > 3 || Math.abs(newY - ballPosition.y) > 3)) {
      isBallDragging.value = true
      ballJustDragged = true
    }

    if (isBallDragging.value) {
      const targetX = Math.max(0, Math.min(window.innerWidth - ballSize, newX))
      const targetY = Math.max(0, Math.min(window.innerHeight - ballSize, newY))
      ballPosition.x = targetX
      ballPosition.y = targetY
    }
  }

  const upHandler = () => {
    isBallDragging.value = false
    saveBallPosition()
    document.removeEventListener('mousemove', moveHandler)
    document.removeEventListener('mouseup', upHandler)
    document.removeEventListener('touchmove', moveHandler)
    document.removeEventListener('touchend', upHandler)
  }

  document.addEventListener('mousemove', moveHandler)
  document.addEventListener('mouseup', upHandler)
  document.addEventListener('touchmove', moveHandler, { passive: false })
  document.addEventListener('touchend', upHandler)
}

// 弹窗拖拽
function startPanelDrag(e) {
  // 阻止在输入框、按钮等交互元素上的拖拽
  if (e.target.closest('.el-input') || e.target.closest('button') || e.target.closest('.el-button')) {
    return
  }

  e.preventDefault()
  isPanelDragging.value = false
  panelJustDragged = false

  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const clientY = e.touches ? e.touches[0].clientY : e.clientY
  const startPos = { x: clientX - panelPosition.x, y: clientY - panelPosition.y }

  const moveHandler = (moveEvent) => {
    moveEvent.preventDefault()
    const clientX = moveEvent.touches ? moveEvent.touches[0].clientX : moveEvent.clientX
    const clientY = moveEvent.touches ? moveEvent.touches[0].clientY : moveEvent.clientY

    const newX = clientX - startPos.x
    const newY = clientY - startPos.y

    if (!isPanelDragging.value && (Math.abs(newX - panelPosition.x) > 3 || Math.abs(newY - panelPosition.y) > 3)) {
      isPanelDragging.value = true
      panelJustDragged = true
    }

    if (isPanelDragging.value) {
      const targetX = Math.max(0, Math.min(window.innerWidth - panelWidth, newX))
      const targetY = Math.max(0, Math.min(window.innerHeight - panelHeight, newY))
      panelPosition.x = targetX
      panelPosition.y = targetY
    }
  }

  const upHandler = () => {
    isPanelDragging.value = false
    savePanelPosition()  // 拖拽结束时保存弹窗位置
    document.removeEventListener('mousemove', moveHandler)
    document.removeEventListener('mouseup', upHandler)
    document.removeEventListener('touchmove', moveHandler)
    document.removeEventListener('touchend', upHandler)
  }

  document.addEventListener('mousemove', moveHandler)
  document.addEventListener('mouseup', upHandler)
  document.addEventListener('touchmove', moveHandler, { passive: false })
  document.addEventListener('touchend', upHandler)
}

// 发送消息（调用百炼API）
async function sendMessage(text = null) {
  // 如果传入的是事件对象或非字符串，使用inputText.value
  if (typeof text !== 'string') {
    text = inputText.value.trim()
  }

  if (!text || isTyping.value) return

  messages.value.push({
    role: 'user',
    content: text,
    timestamp: Date.now()
  })

  inputText.value = ''
  isTyping.value = true

  try {
    const response = await callDashscopeAPI(text)
    messages.value.push({
      role: 'assistant',
      content: response,
      timestamp: Date.now()
    })
  } catch (error) {
    console.error('❌ API调用失败:', error)
    ElMessage.error('AI回复失败: ' + error.message)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题。请检查网络连接或API配置。',
      timestamp: Date.now()
    })
  } finally {
    isTyping.value = false
  }
}

// 调用智谱AI API (GLM-4)
async function callDashscopeAPI(userMessage) {
  // 构建API消息格式（包含所有历史对话）
  const apiMessages = [
    {
      role: 'system',
      content: '你是中国国家通用手语专家，严格按标准词典描述动作，不编造。'
    },
    ...messages.value.map(m => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.content
    }))
  ]

  const response = await fetch(ZHIPU_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${ZHIPU_API_KEY}`
    },
    body: JSON.stringify({
      model: MODEL_NAME,
      messages: apiMessages,
      temperature: 0.1,
      top_p: 0.8,
      stream: false
    })
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.error?.message || 'API请求失败')
  }

  const data = await response.json()
  return data.choices[0].message.content
}

function clearChat() {
  messages.value = [{
    role: 'assistant',
    content: '对话已清空。有什么新问题吗？',
    timestamp: Date.now()
  }]
}

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}
</script>

<style scoped lang="scss">
.floating-ball {
  position: fixed;
  z-index: 9999;
  cursor: pointer;
  user-select: none;

  .ball-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 24px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;

    &:hover {
      transform: scale(1.1);
      box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
  }

  &.dragging {
    .ball-icon {
      cursor: move;
    }
  }
}

.chat-panel {
  position: fixed;
  z-index: 9998;
  width: 350px;
  height: 500px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  cursor: move;

  &.dragging {
    cursor: move;
    opacity: 0.9;
  }

  .panel-header {
    padding: 12px 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
    cursor: move;

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;

      .el-button {
        color: #fff;
        padding: 4px;

        &:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }

  .messages {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    background: #f9fafb;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-thumb {
      background: #c0c4cc;
      border-radius: 3px;
    }
  }

  .message {
    margin-bottom: 12px;
    padding: 10px 14px;
    border-radius: 12px;
    max-width: 80%;
    line-height: 1.5;
    font-size: 14px;
    animation: fadeIn 0.3s ease;

    &.user {
      background: #409eff;
      color: #fff;
      margin-left: auto;
      border-bottom-right-radius: 4px;
    }

    &.assistant {
      background: #f5f5f5;
      color: #333;
      border-bottom-left-radius: 4px;

      .message-content {
        h2, h3, h4 {
          color: #333;
          margin: 8px 0 4px 0;
        }
        h2 { font-size: 16px; }
        h3 { font-size: 15px; }
        h4 { font-size: 14px; }
        strong { color: #409eff; }
        em { color: #666; }
        ul {
          margin: 6px 0;
          padding-left: 20px;
          list-style: disc;
          li { margin: 3px 0; }
        }
        code {
          background: #e8e8e8;
          padding: 2px 6px;
          border-radius: 4px;
          font-family: Consolas, monospace;
          font-size: 13px;
        }
        pre {
          background: #2d2d2d;
          color: #f8f8f2;
          padding: 12px;
          border-radius: 8px;
          overflow-x: auto;
          margin: 8px 0;
          code {
            background: transparent;
            padding: 0;
            color: inherit;
          }
        }
      }
    }
  }

  .typing-indicator {
    display: flex;
    gap: 4px;
    padding: 4px 0;

    span {
      width: 6px;
      height: 6px;
      background: #c0c4cc;
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out both;

      &:nth-child(1) { animation-delay: -0.32s; }
      &:nth-child(2) { animation-delay: -0.16s; }
    }
  }

  .quick-suggestions {
    padding: 8px 16px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    border-top: 1px solid #e4e7ed;
    background: #fff;
  }

  .input-area {
    padding: 12px;
    border-top: 1px solid #eee;
    display: flex;
    gap: 8px;

    .el-input {
      flex: 1;
    }
  }
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
