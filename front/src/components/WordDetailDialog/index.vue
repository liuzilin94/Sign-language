<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="dialogVisible" class="detail-overlay" @click.self="close">
        <div class="detail-panel">
          <!-- Header -->
          <div class="detail-header">
            <h2 class="word-title">{{ wordData?.word || '' }}</h2>
            <div class="header-actions">
              <button class="action-btn" @click="toggleFavorite">
                <svg viewBox="0 0 24 24" width="18" height="18" :fill="isFavorite ? '#f59e0b' : 'none'" stroke="currentColor" stroke-width="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                <span>{{ isFavorite ? '已收藏' : '收藏' }}</span>
              </button>
              <button class="close-btn" @click="close">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>

          <!-- Tabs -->
          <div class="tabs-nav">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              :class="['tab-btn', { active: activeTab === tab.id }]"
              @click="activeTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- Tab Content -->
          <div class="tab-content">
            <!-- 视频演示 -->
            <div v-if="activeTab === 'video'" class="tab-pane">
              <div v-if="wordData?.videoUrl" class="video-wrapper">
                <video
                  :src="wordData.videoUrl"
                  controls
                  playsinline
                  muted
                  @error="handleVideoError"
                ></video>
              </div>
              <div v-else class="empty-state">
                <span class="empty-icon">🎬</span>
                <span>视频演示正在录制中...</span>
              </div>
            </div>

            <!-- 图解 -->
            <div v-if="activeTab === 'images'" class="tab-pane">
              <div v-if="wordData?.imageUrl" class="image-grid">
                <div class="image-item">
                  <img :src="wordData.imageUrl" :alt="wordData.word" />
                </div>
              </div>
              <div v-else class="empty-state">
                <span class="empty-icon">🖼️</span>
                <span>暂无图解材料</span>
              </div>
            </div>

            <!-- 动作分解 -->
            <div v-if="activeTab === 'desc'" class="tab-pane">
              <div v-if="wordData?.steps?.length > 0" class="steps-list">
                <div v-for="(step, index) in wordData.steps" :key="index" class="step-item">
                  <div class="step-num">{{ index + 1 }}</div>
                  <div class="step-text">{{ step }}</div>
                </div>
              </div>
              <div v-else class="empty-state">
                <span class="empty-icon">👋</span>
                <span>暂无动作分解</span>
              </div>
            </div>

            <!-- 方言专区 -->
            <div v-if="activeTab === 'dialect'" class="tab-pane">
              <div class="dialect-header">
                <span>共创方言手语</span>
                <button class="primary-btn" @click="goUpload">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                  </svg>
                  上传方言
                </button>
              </div>
              <div class="region-filter">
                <button
                  v-for="r in regions"
                  :key="r.value"
                  :class="['filter-btn', { active: selectedRegion === r.value }]"
                  @click="selectedRegion = r.value"
                >
                  {{ r.label }}
                </button>
              </div>
              <div class="dialect-list">
                <div v-if="loadingDialects" class="empty-state">
                  <span>加载中...</span>
                </div>
                <div v-else-if="filteredDialects.length > 0">
                  <div v-for="d in filteredDialects" :key="d.id" class="dialect-item">
                    <div class="dialect-region">{{ d.region }}</div>
                    <div class="dialect-video" v-if="d.video_url">
                      <video :src="getFullVideoUrl(d.video_url)" controls></video>
                    </div>
                    <div v-else class="dialect-pending">视频待上传</div>
                    <div class="dialect-author">
                      <span v-if="d.author">上传者：{{ d.author }}</span>
                      <span v-if="d.created_at"> · {{ formatDate(d.created_at) }}</span>
                      <span> · {{ statusText[d.status] || '待审核' }}</span>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-state">
                  <span>暂无该地区方言，成为第一个上传者吧</span>
                </div>
              </div>
            </div>

            <!-- 学习笔记 -->
            <div v-if="activeTab === 'notes'" class="tab-pane">
              <div class="notes-header">
                <span>我的笔记</span>
              </div>
              <div class="note-input">
                <textarea
                  v-model="newNote"
                  placeholder="写下你的学习心得..."
                  rows="3"
                ></textarea>
                <button class="primary-btn" @click="addNote">保存笔记</button>
              </div>
              <div class="notes-list">
                <div v-for="(note, idx) in notes" :key="idx" class="note-item">
                  <div class="note-time">{{ note.time }}</div>
                  <div class="note-content">{{ note.content }}</div>
                </div>
                <div v-if="notes.length === 0" class="empty-state">
                  <span>还没有笔记，写下你的学习心得吧</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useLearnStore } from '@/store/learn'
import { useWordDetailStore } from '@/store/wordDetail'
import { dialectApi } from '@/api'

const router = useRouter()
const learnStore = useLearnStore()
const detailStore = useWordDetailStore()

// 本地状态 - 直接引用 store 的响应式数据
const dialogVisible = computed(() => detailStore.dialogVisible)
const wordData = computed(() => detailStore.wordData)
const isFavorite = computed(() => learnStore.isFavorite(wordData.value?.id))

const activeTab = ref('video')
const selectedRegion = ref('')
const newNote = ref('')
const loadingDialects = ref(false)
const dialects = ref([])

const tabs = [
  { id: 'video', label: '视频演示' },
  { id: 'images', label: '图解' },
  { id: 'desc', label: '动作分解' },
  { id: 'dialect', label: '方言专区' },
  { id: 'notes', label: '学习笔记' }
]

const regions = [
  { label: '全部', value: '' },
  { label: '北京', value: '北京' },
  { label: '上海', value: '上海' },
  { label: '广东', value: '广东' },
  { label: '四川', value: '四川' },
  { label: '东北', value: '东北' }
]

const statusText = {
  approved: '已通过',
  pending: '审核中',
  rejected: '已驳回'
}

const notes = computed(() => {
  const wordId = wordData.value?.id
  if (!wordId) return []
  return learnStore.getNotes(String(wordId))
})

const filteredDialects = computed(() => {
  if (!selectedRegion.value) return dialects.value
  return dialects.value.filter(d => d.region === selectedRegion.value)
})

function getFullVideoUrl(url) {
  if (!url) return ''
  // 如果是相对路径，添加API基础URL
  if (url.startsWith('/')) {
    return `http://localhost:5001${url}`
  }
  return url
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

async function loadDialects() {
  const wordId = wordData.value?.id
  if (!wordId) {
    dialects.value = []
    return
  }

  loadingDialects.value = true
  try {
    const res = await dialectApi.getWordDialects(wordId)
    dialects.value = res.data || []
    console.log('[WordDetailDialog] Loaded dialects:', dialects.value)
  } catch (e) {
    console.error('[WordDetailDialog] Load dialects failed:', e)
    dialects.value = []
  } finally {
    loadingDialects.value = false
  }
}

watch(dialogVisible, (val) => {
  if (val) {
    activeTab.value = 'video'
    selectedRegion.value = ''
    newNote.value = ''
    dialects.value = []
  }
})

watch(activeTab, (newTab) => {
  // 当切换到方言 tab 时加载方言数据
  if (newTab === 'dialect' && dialects.value.length === 0) {
    loadDialects()
  }
})

function close() {
  detailStore.closeDialog()
}

function toggleFavorite() {
  if (wordData.value) learnStore.toggleFavorite(wordData.value.id)
}

function addNote() {
  if (!newNote.value.trim() || !wordData.value) return
  learnStore.addNote(String(wordData.value.id), newNote.value)
  newNote.value = ''
}

function goUpload() {
  close()
  router.push(`/upload?word_id=${wordData.value?.id}`)
}

function handleVideoError(event) {
  const video = event.target
  console.error('[Video Error] Error code:', video.error?.code)
  console.error('[Video Error] Error message:', video.error?.message)
  console.error('[Video Error] Video src:', video.src)
  console.error('[Video Error] Video networkState:', video.networkState)
  console.error('[Video Error] Video readyState:', video.readyState)
}
</script>

<style scoped>
/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-active .detail-panel,
.modal-leave-active .detail-panel {
  transition: transform 0.2s ease;
}
.modal-enter-from .detail-panel,
.modal-leave-to .detail-panel {
  transform: scale(0.95) translateY(10px);
}

/* Overlay */
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

/* Panel */
.detail-panel {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

/* Header */
.detail-header {
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.word-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.header-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #666;
}

.action-btn:hover {
  background: #f5f5f5;
}

.close-btn {
  padding: 6px;
  border: none;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

/* Tabs */
.tabs-nav {
  display: flex;
  padding: 0 24px;
  border-bottom: 1px solid #eee;
  gap: 4px;
}

.tab-btn {
  padding: 12px 16px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.tab-btn:hover {
  color: #333;
}

.tab-btn.active {
  color: #1a1a1a;
  border-bottom-color: #1a1a1a;
  font-weight: 500;
}

/* Content */
.tab-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.tab-pane {
  height: 100%;
  overflow-y: auto;
  padding: 16px 20px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #999;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

/* Video */
.video-wrapper {
  border-radius: 8px;
  overflow: hidden;
  background: #000;
}

.video-wrapper video {
  width: 100%;
  display: block;
}

/* Image Grid */
.image-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.image-item {
  flex: 1;
  min-width: 200px;
  border-radius: 8px;
  overflow: hidden;
  background: #f9f9f9;
}

.image-item img {
  width: 100%;
  height: auto;
  display: block;
}

/* Steps */
.steps-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #1a1a1a;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
}

.step-text {
  font-size: 15px;
  color: #333;
  line-height: 1.6;
}

/* Dialect */
.dialect-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
}

.region-filter {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 14px;
  border: 1px solid #ddd;
  border-radius: 16px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #666;
}

.filter-btn.active {
  background: #1a1a1a;
  color: #fff;
  border-color: #1a1a1a;
}

.dialect-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dialect-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.dialect-region {
  font-weight: 500;
  margin-bottom: 8px;
}

.dialect-video {
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}

.dialect-video video {
  width: 100%;
  display: block;
}

.dialect-pending {
  padding: 20px;
  text-align: center;
  color: #999;
  background: #fff;
  border-radius: 6px;
  margin-bottom: 8px;
}

.dialect-author {
  font-size: 12px;
  color: #999;
}

/* Notes */
.notes-header {
  font-weight: 500;
  margin-bottom: 12px;
}

.note-input {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.note-input textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  font-size: 14px;
  font-family: inherit;
}

.note-input textarea:focus {
  outline: none;
  border-color: #1a1a1a;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.note-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.note-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
}

.note-content {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

/* Primary Button */
.primary-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #1a1a1a;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
}

.primary-btn:hover {
  background: #333;
}
</style>
