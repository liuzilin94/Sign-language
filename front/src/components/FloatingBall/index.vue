<template>
  <Teleport to="body">
    <div
      v-if="!isExpanded"
      class="fab"
      :style="fabStyle"
      @click="handleFabClick"
    >
      <div class="fab-inner" @mousedown.stop="startDrag" @touchstart.prevent.stop="startDrag">
        <el-icon class="fab-icon"><ChatDotSquare /></el-icon>
      </div>
    </div>

    <div
      v-if="isExpanded"
      class="chat-window"
      :style="panelStyle"
    >
      <div class="chat-header" @mousedown="startPanelDrag" @touchstart.prevent="startPanelDrag">
        <span class="chat-title">AI 助手</span>
        <div class="chat-header-actions">
          <el-tag v-if="isTyping" type="info" size="small" effect="plain">思考中</el-tag>
          <el-button text size="small" @click.stop="clearChat">
            <el-icon><Delete /></el-icon>
          </el-button>
          <el-button text size="small" @click.stop="closePanel">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>

      <div class="chat-messages" ref="messagesRef">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="['chat-msg', msg.role]"
        >
          <div class="msg-bubble" v-html="formatContent(msg.content)"></div>
        </div>
        <div v-if="isTyping" class="chat-msg assistant">
          <div class="msg-bubble typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="chat-suggestions" v-if="messages.length <= 2">
        <el-button
          v-for="s in quickSuggestions"
          :key="s"
          size="small"
          @click="sendMessage(s)"
        >
          {{ s }}
        </el-button>
      </div>

      <div class="chat-input-area">
        <el-input
          v-model="inputText"
          placeholder="输入你的问题..."
          size="small"
          @keyup.enter="sendMessage"
          :disabled="isTyping"
        >
          <template #append>
            <el-button @click="sendMessage" :disabled="isTyping || !inputText.trim()">
              <el-icon><Promotion /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ChatDotSquare, Close, Delete, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const isExpanded = ref(false)
const fabPos = ref({ x: window.innerWidth - 68, y: window.innerHeight - 60 })
const panelPos = ref({ x: window.innerWidth - 344, y: window.innerHeight - 520 })
const inputText = ref('')
const messages = ref([])
const messagesRef = ref(null)
const isTyping = ref(false)

// 拖拽状态
const isPanelDragging = ref(false)
let fabDragging = false
let panelDragging = false
let hasDragged = false

const FAB_SIZE = 44
const PANEL_W = 320
const PANEL_H = 440

const ZHIPU_API_KEY = 'sk-e121784bebcb4865a1d9e6dd287cb3cf'
const ZHIPU_API_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
const MODEL_NAME = 'glm-5'

const quickSuggestions = [
  '手语"你好"怎么做？',
  '手语"谢谢"的动作要点',
  '如何提高手语识别准确率？',
]

// 统一使用 left/top 定位
const fabStyle = computed(() => ({
  left: fabPos.value.x + 'px',
  top: fabPos.value.y + 'px'
}))

const panelStyle = computed(() => ({
  left: panelPos.value.x + 'px',
  top: panelPos.value.y + 'px'
}))

onMounted(() => {
  // 恢复保存的位置
  try {
    const savedFabPos = localStorage.getItem('fabPos')
    if (savedFabPos) {
      const parsed = JSON.parse(savedFabPos)
      fabPos.value.x = Math.max(0, Math.min(window.innerWidth - FAB_SIZE, parsed.x || window.innerWidth - 68))
      fabPos.value.y = Math.max(0, Math.min(window.innerHeight - FAB_SIZE, parsed.y || window.innerHeight - 60))
    }
    const savedPanelPos = localStorage.getItem('panelPos')
    if (savedPanelPos) {
      const parsed = JSON.parse(savedPanelPos)
      panelPos.value.x = Math.max(0, Math.min(window.innerWidth - PANEL_W, parsed.x || window.innerWidth - 344))
      panelPos.value.y = Math.max(0, Math.min(window.innerHeight - PANEL_H, parsed.y || window.innerHeight - 520))
    }
  } catch {}
  messages.value = [{
    role: 'assistant',
    content: '你好！我是你的 AI 手语助手。我可以帮你解答手语动作疑问、提供学习建议。请问有什么可以帮你的吗？'
  }]
})

watch(messages, async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}, { deep: true })

function openPanel() {
  isExpanded.value = true
  // 计算面板位置：在悬浮球上方8px
  let newPanelX = fabPos.value.x - (PANEL_W - FAB_SIZE) / 2
  let newPanelY = fabPos.value.y - PANEL_H - 8

  // 如果上方空间不够，放到悬浮球下方
  if (newPanelY < 0) {
    newPanelY = fabPos.value.y + FAB_SIZE + 8
  }

  // 限制在视口范围内
  panelPos.value.x = Math.max(0, Math.min(window.innerWidth - PANEL_W, newPanelX))
  panelPos.value.y = Math.max(0, Math.min(window.innerHeight - PANEL_H, newPanelY))
}

function closePanel() {
  isExpanded.value = false
}

function clearChat() {
  messages.value = [{
    role: 'assistant',
    content: '已清空对话，有什么新问题吗？'
  }]
}

// ==================== DRAG ====================
// 悬浮球拖拽
function startDrag(e) {
  e.preventDefault()
  e.stopPropagation()

  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const clientY = e.touches ? e.touches[0].clientY : e.clientY

  // 记录初始位置
  let startX = clientX
  let startY = clientY
  let startFabX = fabPos.value.x
  let startFabY = fabPos.value.y
  fabDragging = false

  const moveHandler = (ev) => {
    const cx = ev.touches ? ev.touches[0].clientX : ev.clientX
    const cy = ev.touches ? ev.touches[0].clientY : ev.clientY

    // 移动超过5px才算拖拽
    if (!fabDragging) {
      const dx = cx - startX
      const dy = cy - startY
      if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
        fabDragging = true
      }
    }

    if (fabDragging) {
      // 计算偏移量，直接应用到 left/top
      const dx = cx - startX
      const dy = cy - startY
      fabPos.value.x = Math.max(0, Math.min(window.innerWidth - FAB_SIZE, startFabX + dx))
      fabPos.value.y = Math.max(0, Math.min(window.innerHeight - FAB_SIZE, startFabY + dy))
    }
  }

  const upHandler = () => {
    document.removeEventListener('mousemove', moveHandler)
    document.removeEventListener('mouseup', upHandler)
    document.removeEventListener('touchmove', moveHandler)
    document.removeEventListener('touchend', upHandler)

    // 如果发生拖拽，设置标志并在300ms后重置
    if (fabDragging) {
      hasDragged = true
      setTimeout(() => { hasDragged = false }, 300)
    }

    fabDragging = false
    try { localStorage.setItem('fabPos', JSON.stringify(fabPos.value)) } catch {}
  }

  document.addEventListener('mousemove', moveHandler)
  document.addEventListener('mouseup', upHandler)
  document.addEventListener('touchmove', moveHandler, { passive: false })
  document.addEventListener('touchend', upHandler)
}

function handleFabClick() {
  if (hasDragged) return
  if (isExpanded.value) {
    closePanel()
  } else {
    openPanel()
  }
}

// 弹窗拖拽
function startPanelDrag(e) {
  e.preventDefault()

  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const clientY = e.touches ? e.touches[0].clientY : e.clientY

  let startX = clientX
  let startY = clientY
  let startPanelX = panelPos.value.x
  let startPanelY = panelPos.value.y
  panelDragging = false

  const moveHandler = (ev) => {
    const cx = ev.touches ? ev.touches[0].clientX : ev.clientX
    const cy = ev.touches ? ev.touches[0].clientY : ev.clientY

    if (!panelDragging) {
      const dx = cx - startX
      const dy = cy - startY
      if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
        panelDragging = true
      }
    }

    if (panelDragging) {
      const dx = cx - startX
      const dy = cy - startY
      panelPos.value.x = Math.max(0, Math.min(window.innerWidth - PANEL_W, startPanelX + dx))
      panelPos.value.y = Math.max(0, Math.min(window.innerHeight - PANEL_H, startPanelY + dy))
    }
  }

  const upHandler = () => {
    document.removeEventListener('mousemove', moveHandler)
    document.removeEventListener('mouseup', upHandler)
    document.removeEventListener('touchmove', moveHandler)
    document.removeEventListener('touchend', upHandler)
    panelDragging = false
    try { localStorage.setItem('panelPos', JSON.stringify(panelPos.value)) } catch {}
  }

  document.addEventListener('mousemove', moveHandler)
  document.addEventListener('mouseup', upHandler)
  document.addEventListener('touchmove', moveHandler, { passive: false })
  document.addEventListener('touchend', upHandler)
}

// ==================== API ====================
async function sendMessage(text = null) {
  const msg = typeof text === 'string' ? text : inputText.value.trim()
  if (!msg || isTyping.value) return

  messages.value.push({ role: 'user', content: msg })
  if (typeof text !== 'string') inputText.value = ''
  isTyping.value = true

  try {
    const response = await callAPI(msg)
    messages.value.push({ role: 'assistant', content: response })
  } catch (e) {
    ElMessage.error('AI 回复失败，请稍后重试')
    messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用。' })
  } finally {
    isTyping.value = false
  }
}

async function callAPI(userMessage) {
  const apiMessages = [
    { role: 'system', content: '你是中国国家通用手语专家，严格按标准词典描述动作，不编造。' },
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
    body: JSON.stringify({ model: MODEL_NAME, messages: apiMessages, temperature: 0.1 })
  })

  if (!response.ok) throw new Error('API error')
  const data = await response.json()
  return data.choices[0].message.content
}

function formatContent(content) {
  if (!content) return ''

  // 转义 HTML 特殊字符
  let html = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // 处理代码块 (```code```)
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')

  // 处理行内代码 (`code`)
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')

  // 处理标题 (# ## ###)
  html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>')

  // 处理加粗 (**text**)
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')

  // 处理斜体 (*text*)
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')

  // 处理列表项 (- item 或 1. item)
  html = html.replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')

  // 包裹连续的 li 元素为 ul
  html = html.replace(/(<li>.*?<\/li>(\s*<li>.*?<\/li>)*)/gs, '<ul>$1</ul>')

  // 处理换行
  html = html.replace(/\n/g, '<br>')

  // 清理多余的 br
  html = html.replace(/<br><br>/g, '<br>')

  return html
}
</script>

<style scoped lang="scss">
.fab {
  position: fixed;
  z-index: 9999;
  width: 44px;
  height: 44px;
  cursor: pointer;

  .fab-inner {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #0d0d0d;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    transition: all 200ms ease;

    &:hover {
      transform: scale(1.05);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    .fab-icon {
      font-size: 18px;
      color: #fff;
    }
  }
}

.chat-window {
  position: fixed;
  z-index: 9998;
  width: 320px;
  height: 440px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  cursor: move;

  .chat-header {
    padding: 14px 16px;
    border-bottom: 1px solid #e8e8e8;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: move;
    flex-shrink: 0;

    .chat-title {
      font-size: 14px;
      font-weight: 600;
      color: #0d0d0d;
    }

    .chat-header-actions {
      display: flex;
      align-items: center;
      gap: 6px;

      .el-button {
        color: #8a8a8a;
        padding: 4px;

        &:hover {
          color: #0d0d0d;
          background: transparent;
        }
      }
    }
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: #e8e8e8;
      border-radius: 2px;
    }

    .chat-msg {
      display: flex;

      &.user {
        justify-content: flex-end;

        .msg-bubble {
          background: #0d0d0d;
          color: #fff;
          border-radius: 12px 12px 4px 12px;
          max-width: 78%;
        }
      }

      &.assistant {
        justify-content: flex-start;

        .msg-bubble {
          background: #f5f3ef;
          color: #0d0d0d;
          border-radius: 12px 12px 12px 4px;
          max-width: 82%;
          font-size: 13px;
          line-height: 1.6;

          :deep(h2) { font-size: 15px; font-weight: 600; margin: 8px 0 4px; color: #1a1a1a; }
          :deep(h3) { font-size: 14px; font-weight: 600; margin: 6px 0 4px; color: #1a1a1a; }
          :deep(h4) { font-size: 13px; font-weight: 600; margin: 6px 0 4px; color: #333; }
          :deep(strong) { color: #0d0d0d; font-weight: 600; }
          :deep(em) { color: #666; font-style: italic; }
          :deep(code) { background: #ebe9e4; padding: 1px 5px; border-radius: 3px; font-size: 12px; font-family: monospace; }
          :deep(.code-block) { background: #2d2d2d; color: #f8f8f2; padding: 10px 12px; border-radius: 6px; margin: 6px 0; overflow-x: auto; code { background: transparent; padding: 0; color: inherit; } }
          :deep(ul) { margin: 4px 0; padding-left: 16px; }
          :deep(li) { margin: 3px 0; }
          :deep(p) { margin: 4px 0; }
        }
      }

      .msg-bubble {
        padding: 9px 14px;
        font-size: 13px;
        line-height: 1.55;
        animation: fadeIn 0.25s ease;

        &.typing {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 10px 14px;

          span {
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #c8c8c8;
            animation: typingDot 1.4s infinite ease-in-out both;

            &:nth-child(1) { animation-delay: -0.32s; }
            &:nth-child(2) { animation-delay: -0.16s; }
          }
        }
      }
    }
  }

  .chat-suggestions {
    padding: 8px 14px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    border-top: 1px solid #e8e8e8;
    flex-shrink: 0;
  }

  .chat-input-area {
    padding: 12px 14px;
    border-top: 1px solid #e8e8e8;
    flex-shrink: 0;

    .el-input {
      .el-input__wrapper {
        border-radius: 6px;
        padding: 2px 8px;
      }
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes typingDot {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
