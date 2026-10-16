<template>
  <div class="word-detail-page">
    <!-- Header -->
    <div class="page-header">
      <el-button text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <div class="content-wrapper">
      <!-- Main Content -->
      <div class="main-content">
        <!-- Title Section -->
        <div class="title-section">
          <div class="title-row">
            <h1>{{ word.title }}</h1>
            <div class="title-actions">
              <el-button
                :type="isFavorite ? 'warning' : 'default'"
                @click="toggleFavorite"
              >
                <el-icon><Star /></el-icon>
                {{ isFavorite ? '已收藏' : '收藏' }}
              </el-button>
              <el-button
                :type="isNewWord ? 'success' : 'default'"
                @click="toggleNewWord"
              >
                <el-icon><Collection /></el-icon>
                {{ isNewWord ? '已标记' : '标记新词' }}
              </el-button>
            </div>
          </div>
          <div class="word-meta">
            <el-tag>{{ word.category }}</el-tag>
            <el-tag :type="getDifficultyType(word.difficulty)">
              {{ getDifficultyLabel(word.difficulty) }}
            </el-tag>
            <span class="learn-count">{{ word.learnCount || 0 }} 人学习</span>
          </div>
        </div>

        <!-- Tabs -->
        <div class="tabs-container">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="视频演示" name="video">
              <template #label>
                <span class="tab-label">
                  <el-icon><VideoPlay /></el-icon>
                  视频演示
                </span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="图片示意" name="image">
              <template #label>
                <span class="tab-label">
                  <el-icon><Picture /></el-icon>
                  图片示意
                </span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="动作分解" name="steps">
              <template #label>
                <span class="tab-label">
                  <el-icon><List /></el-icon>
                  动作分解
                </span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="方言" name="dialect">
              <template #label>
                <span class="tab-label">
                  <el-icon><ChatLineSquare /></el-icon>
                  方言
                </span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="笔记" name="notes">
              <template #label>
                <span class="tab-label">
                  <el-icon><Document /></el-icon>
                  笔记
                </span>
              </template>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- Tab Content -->
        <div class="tab-content">
          <!-- Video Tab -->
          <div v-if="activeTab === 'video'" class="video-content">
            <div class="video-player">
              <video
                v-if="word.videoUrl"
                :src="word.videoUrl"
                controls
                autoplay
                muted
                playsinline
                @error="handleVideoError"
              />
              <div v-else class="video-placeholder">
                <el-icon><VideoPlay /></el-icon>
                <span>暂无视频</span>
              </div>
            </div>
            <div class="video-controls">
              <div class="speed-control">
                <span>播放速度</span>
                <el-slider
                  v-model="playbackSpeed"
                  :min="0.25"
                  :max="2"
                  :step="0.25"
                  :marks="speedMarks"
                  show-stops
                />
                <span class="speed-value">{{ playbackSpeed }}x</span>
              </div>
              <el-button type="primary" @click="practiceNow">
                <el-icon><VideoCamera /></el-icon>
                立即练习
              </el-button>
            </div>
          </div>

          <!-- Image Tab -->
          <div v-if="activeTab === 'image'" class="image-content">
            <div class="image-gallery">
              <el-image
                v-for="(img, index) in word.images"
                :key="index"
                :src="img"
                :preview-src-list="word.images"
                fit="contain"
                class="gallery-image"
              />
              <div v-if="!word.images?.length" class="image-placeholder">
                <el-icon><Picture /></el-icon>
                <span>暂无图片</span>
              </div>
            </div>
          </div>

          <!-- Steps Tab -->
          <div v-if="activeTab === 'steps'" class="steps-content">
            <div
              v-for="(step, index) in word.steps"
              :key="index"
              class="step-item"
            >
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-details">
                <h3>{{ step.title }}</h3>
                <p>{{ step.description }}</p>
                <div v-if="step.image" class="step-image">
                  <img :src="step.image" :alt="step.title" />
                </div>
              </div>
            </div>

            <div v-if="!word.steps?.length" class="empty-state">
              <el-icon><List /></el-icon>
              <span>暂无动作分解</span>
            </div>
          </div>

          <!-- Dialect Tab -->
          <div v-if="activeTab === 'dialect'" class="dialect-content">
            <div class="dialect-header">
              <span>共创方言手语</span>
              <el-button type="primary" @click="goUpload">
                <el-icon><Upload /></el-icon>
                上传方言
              </el-button>
            </div>

            <div class="dialect-filter">
              <el-select v-model="selectedDialect" placeholder="选择地区">
                <el-option label="全部地区" value="" />
                <el-option label="全国通用" value="全国通用" />
                <el-option label="北京" value="北京" />
                <el-option label="上海" value="上海" />
                <el-option label="广东" value="广东" />
                <el-option label="四川" value="四川" />
                <el-option label="东北" value="东北" />
              </el-select>
            </div>

            <div v-if="loadingDialects" class="loading-state">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>

            <div v-else class="dialect-list">
              <div
                v-for="dialect in filteredDialects"
                :key="dialect.id"
                class="dialect-item"
              >
                <div class="dialect-region">
                  <el-tag>{{ dialect.region }}</el-tag>
                </div>
                <div class="dialect-video">
                  <video v-if="dialect.video_url" :src="getFullVideoUrl(dialect.video_url)" controls />
                  <div v-else class="dialect-placeholder">
                    <el-icon><VideoPlay /></el-icon>
                  </div>
                </div>
                <p class="dialect-desc">{{ dialect.description || '暂无说明' }}</p>
                <div class="dialect-meta">
                  <span v-if="dialect.author">上传者：{{ dialect.author }}</span>
                  <span v-if="dialect.created_at">{{ formatTime(dialect.created_at) }}</span>
                  <el-tag :type="getStatusType(dialect.status)" size="small">
                    {{ getStatusText(dialect.status) }}
                  </el-tag>
                </div>
              </div>
            </div>

            <div v-if="!loadingDialects && filteredDialects.length === 0" class="empty-state">
              <el-icon><ChatLineSquare /></el-icon>
              <span>暂无方言版本，成为第一个上传者吧</span>
            </div>
          </div>

          <!-- Notes Tab -->
          <div v-if="activeTab === 'notes'" class="notes-content">
            <div class="add-note">
              <el-input
                v-model="newNote"
                type="textarea"
                :rows="3"
                placeholder="添加学习笔记..."
              />
              <el-button type="primary" @click="addNote">
                <el-icon><Plus /></el-icon>
                添加笔记
              </el-button>
            </div>

            <div class="notes-list">
              <div
                v-for="note in notes"
                :key="note.id"
                class="note-item"
              >
                <div class="note-header">
                  <span class="note-author">{{ note.author }}</span>
                  <span class="note-time">{{ formatTime(note.createdAt) }}</span>
                </div>
                <p class="note-content">{{ note.content }}</p>
                <div class="note-actions">
                  <el-button text size="small" @click="likeNote(note)">
                    <el-icon><StarFilled /></el-icon>
                    {{ note.likes }}
                  </el-button>
                  <el-button
                    v-if="note.authorId === currentUserId"
                    text
                    size="small"
                    type="danger"
                    @click="deleteNote(note)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </div>

            <div v-if="!notes.length" class="empty-state">
              <el-icon><Document /></el-icon>
              <span>暂无笔记，成为第一个添加笔记的人吧</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="sidebar">
        <!-- Related Words -->
        <div class="sidebar-card">
          <h3>相关词汇</h3>
          <div class="related-list">
            <div
              v-for="related in relatedWords"
              :key="related.id"
              class="related-item"
              @click="viewWord(related)"
            >
              <div class="related-preview">
                <video v-if="related.videoUrl" :src="related.videoUrl" muted />
                <div v-else class="related-placeholder">
                  <el-icon><VideoPlay /></el-icon>
                </div>
              </div>
              <div class="related-info">
                <span class="related-title">{{ related.title }}</span>
                <span class="related-category">{{ related.category }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Practice Stats -->
        <div class="sidebar-card">
          <h3>学习统计</h3>
          <div class="stats-list">
            <div class="stat-item">
              <span class="stat-label">学习次数</span>
              <span class="stat-value">{{ practiceStats.learnCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">掌握程度</span>
              <el-progress
                :percentage="practiceStats.mastery"
                :stroke-width="8"
                :show-text="false"
              />
              <span class="stat-value">{{ practiceStats.mastery }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最近练习</span>
              <span class="stat-value">{{ practiceStats.lastPractice }}</span>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="sidebar-card">
          <h3>快捷操作</h3>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="practiceNow">
              <el-icon><VideoCamera /></el-icon>
              立即练习
            </el-button>
            <el-button size="large" @click="addToReview">
              <el-icon><Refresh /></el-icon>
              加入复习
            </el-button>
            <el-button size="large" @click="shareWord">
              <el-icon><Share /></el-icon>
              分享
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import { wordApi } from '@/api'
import {
  ArrowLeft,
  Star,
  Collection,
  VideoPlay,
  Picture,
  List,
  ChatLineSquare,
  Document,
  Plus,
  StarFilled,
  VideoCamera,
  Refresh,
  Share,
  Upload,
  Loading
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const currentUserId = computed(() => userStore.userInfo?.id)

// State
const activeTab = ref('video')
const playbackSpeed = ref(1)
const isFavorite = ref(false)
const isNewWord = ref(false)
const selectedDialect = ref('')
const newNote = ref('')
const loadingDialects = ref(false)
const dialects = ref([])

// Speed marks
const speedMarks = {
  0.25: '0.25x',
  0.5: '0.5x',
  1: '1x',
  1.5: '1.5x',
  2: '2x'
}

// Word data
const word = ref({
  id: 1,
  title: '你好',
  category: '问候',
  difficulty: 'beginner',
  videoUrl: '',
  images: ['https://picsum.photos/400/300?random=1'],
  learnCount: 156,
  steps: [
    { title: '准备姿势', description: '手掌伸直，五指并拢', image: '' },
    { title: '向前伸出', description: '手臂向前伸直', image: '' },
    { title: '轻轻挥动', description: '手腕轻轻左右摆动', image: '' }
  ]
})

// Notes
const notes = ref([
  { id: 1, authorId: 1, author: '张三', content: '这是最基础的手语，学好这个很重要！', createdAt: Date.now() - 86400000, likes: 5 },
  { id: 2, authorId: 2, author: '李四', content: '注意手腕不要僵硬，要放松', createdAt: Date.now() - 172800000, likes: 3 }
])

// Related words
const relatedWords = ref([
  { id: 2, title: '谢谢', category: '礼貌', videoUrl: '' },
  { id: 3, title: '再见', category: '日常', videoUrl: '' },
  { id: 4, title: '早上好', category: '问候', videoUrl: '' },
  { id: 5, title: '晚上好', category: '问候', videoUrl: '' }
])

// Practice stats
const practiceStats = ref({
  learnCount: 12,
  mastery: 65,
  lastPractice: '2小时前'
})

// Computed
const filteredDialects = computed(() => {
  if (!selectedDialect.value) return dialects.value
  return dialects.value.filter(d => d.region === selectedDialect.value)
})

function getFullVideoUrl(url) {
  if (!url) return ''
  if (url.startsWith('/')) {
    return `http://localhost:5001${url}`
  }
  return url
}

function getStatusType(status) {
  const types = {
    approved: 'success',
    pending: 'warning',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = {
    approved: '已通过',
    pending: '待审核',
    rejected: '已驳回'
  }
  return texts[status] || '待审核'
}

async function loadDialects() {
  const wordId = word.value?.id
  if (!wordId) {
    dialects.value = []
    return
  }

  loadingDialects.value = true
  try {
    const res = await wordApi.getDialects(wordId)
    dialects.value = res.data || []
    console.log('[WordDetail] Loaded dialects:', dialects.value)
  } catch (e) {
    console.error('[WordDetail] Load dialects failed:', e)
    dialects.value = []
  } finally {
    loadingDialects.value = false
  }
}

function goUpload() {
  router.push(`/upload?word_id=${word.value?.id}`)
}

// Methods
function getDifficultyType(difficulty) {
  const types = {
    beginner: 'success',
    basic: 'primary',
    intermediate: 'warning',
    advanced: 'danger'
  }
  return types[difficulty] || 'info'
}

function getDifficultyLabel(difficulty) {
  const labels = {
    beginner: '入门',
    basic: '基础',
    intermediate: '进阶',
    advanced: '高级'
  }
  return labels[difficulty] || difficulty
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (hours < 1) return '刚刚'
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function goBack() {
  router.back()
}

function toggleFavorite() {
  isFavorite.value = !isFavorite.value
  if (isFavorite.value) {
    ElMessage.success('已添加到收藏')
  } else {
    ElMessage.success('已取消收藏')
  }
}

function toggleNewWord() {
  isNewWord.value = !isNewWord.value
  if (isNewWord.value) {
    ElMessage.success('已标记为新词')
  } else {
    ElMessage.success('已取消标记')
  }
}

function practiceNow() {
  router.push('/practice')
}

function addToReview() {
  ElMessage.success('已加入复习计划')
}

function shareWord() {
  navigator.clipboard.writeText(window.location.href)
  ElMessage.success('分享链接已复制')
}

function viewWord(related) {
  router.push(`/dictionary/${related.id}`)
}

function addNote() {
  if (!newNote.value.trim()) {
    ElMessage.warning('请输入笔记内容')
    return
  }

  notes.value.unshift({
    id: Date.now(),
    authorId: currentUserId.value,
    author: '我',
    content: newNote.value,
    createdAt: Date.now(),
    likes: 0
  })

  newNote.value = ''
  ElMessage.success('笔记添加成功')
}

function likeNote(note) {
  note.likes++
}

async function deleteNote(note) {
  await ElMessageBox.confirm('确定要删除这条笔记吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })

  const index = notes.value.findIndex(n => n.id === note.id)
  if (index > -1) {
    notes.value.splice(index, 1)
  }
  ElMessage.success('笔记已删除')
}

async function loadWord() {
  const wordId = route.params.id || route.query.id
  if (wordId) {
    try {
      const res = await wordApi.getWordById(wordId)
      if (res.data) {
        word.value = {
          ...word.value,
          ...res.data,
          videoUrl: res.data.demo_video_url || res.data.videoUrl || ''
        }
        console.log('[WordDetail] Loaded videoUrl:', word.value.videoUrl)
      }
    } catch (e) {
      console.error('加载词汇详情失败', e)
    }
  }
}

watch(activeTab, (newTab) => {
  if (newTab === 'dialect' && dialects.value.length === 0) {
    loadDialects()
  }
})

function handleVideoError(event) {
  const video = event.target
  console.error('[Video Error] Error code:', video.error?.code)
  console.error('[Video Error] Error message:', video.error?.message)
  console.error('[Video Error] Video src:', video.src)
  console.error('[Video Error] Video networkState:', video.networkState)
  console.error('[Video Error] Video readyState:', video.readyState)
  ElMessage.error('视频加载失败，请稍后重试')
}

onMounted(() => {
  loadWord()
})
</script>

<style scoped>
.word-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 32px 80px;
}

.page-header {
  margin-bottom: 24px;
}

.content-wrapper {
  display: flex;
  gap: 24px;
}

/* Main Content */
.main-content {
  flex: 1;
  min-width: 0;
}

/* Title Section */
.title-section {
  margin-bottom: 24px;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.title-row h1 {
  font-size: 28px;
  font-weight: 700;
  color: #0d0d0d;
  letter-spacing: -0.5px;
}

.title-actions {
  display: flex;
  gap: 8px;
}

.word-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.learn-count {
  font-size: 13px;
  color: #8a8a8a;
}

/* Tabs Container */
.tabs-container {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 0 24px;
  margin-bottom: 24px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Tab Content */
.tab-content {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
}

/* Video Content */
.video-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.video-player {
  width: 100%;
  background: #0d0d0d;
  border-radius: 10px;
  overflow: hidden;
}

.video-player video {
  width: 100%;
  max-height: 450px;
}

.video-placeholder {
  height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8a8a8a;
  gap: 12px;
  font-size: 16px;
}

.video-placeholder .el-icon {
  font-size: 48px;
}

.video-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #fafaf8;
  border-radius: 10px;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  max-width: 400px;
}

.speed-control span {
  font-size: 14px;
  color: #8a8a8a;
}

.speed-value {
  font-weight: 600;
  color: #0d0d0d;
  min-width: 40px;
}

/* Image Content */
.image-content {
  padding: 20px 0;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.gallery-image {
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
}

.image-placeholder {
  grid-column: 1 / -1;
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fafaf8;
  border-radius: 10px;
  color: #8a8a8a;
  gap: 12px;
}

.image-placeholder .el-icon {
  font-size: 48px;
}

/* Steps Content */
.steps-content {
  padding: 20px 0;
}

.step-item {
  display: flex;
  gap: 20px;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0ee;
}

.step-item:last-child {
  border-bottom: none;
}

.step-number {
  width: 40px;
  height: 40px;
  background: #0d0d0d;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-details {
  flex: 1;
}

.step-details h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 8px;
}

.step-details p {
  font-size: 14px;
  color: #8a8a8a;
  line-height: 1.6;
}

.step-image {
  margin-top: 12px;
}

.step-image img {
  max-width: 200px;
  border-radius: 8px;
}

/* Dialect Content */
.dialect-content {
  padding: 20px 0;
}

.dialect-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dialect-filter {
  margin-bottom: 24px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: #8a8a8a;
}

.dialect-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.dialect-item {
  background: #fafaf8;
  border-radius: 10px;
  padding: 16px;
}

.dialect-region {
  margin-bottom: 12px;
}

.dialect-video {
  width: 100%;
  height: 150px;
  background: #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
}

.dialect-video video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dialect-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a8a8a;
  font-size: 32px;
}

.dialect-desc {
  font-size: 13px;
  color: #8a8a8a;
  margin: 0 0 8px;
}

.dialect-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #999;
}

/* Notes Content */
.notes-content {
  padding: 20px 0;
}

.add-note {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.add-note .el-button {
  align-self: flex-end;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.note-item {
  padding: 16px;
  background: #fafaf8;
  border-radius: 10px;
}

.note-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.note-author {
  font-size: 14px;
  font-weight: 600;
  color: #0d0d0d;
}

.note-time {
  font-size: 12px;
  color: #8a8a8a;
}

.note-content {
  font-size: 14px;
  color: #0d0d0d;
  line-height: 1.6;
  margin-bottom: 12px;
}

.note-actions {
  display: flex;
  gap: 16px;
}

/* Empty State */
.empty-state {
  padding: 60px 24px;
  text-align: center;
  color: #8a8a8a;
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

/* Sidebar */
.sidebar {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 20px;
}

.sidebar-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 16px;
}

/* Related Words */
.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: #fafaf8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 180ms ease;
}

.related-item:hover {
  background: #f0f0ee;
}

.related-preview {
  width: 60px;
  height: 45px;
  background: #e8e8e8;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.related-preview video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a8a8a;
  font-size: 16px;
}

.related-info {
  display: flex;
  flex-direction: column;
}

.related-title {
  font-size: 14px;
  font-weight: 600;
  color: #0d0d0d;
}

.related-category {
  font-size: 12px;
  color: #8a8a8a;
}

/* Stats */
.stats-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 13px;
  color: #8a8a8a;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-actions .el-button {
  width: 100%;
  justify-content: center;
}

@media (max-width: 1024px) {
  .content-wrapper {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .sidebar-card {
    flex: 1;
    min-width: 280px;
  }
}

@media (max-width: 768px) {
  .image-gallery {
    grid-template-columns: repeat(2, 1fr);
  }

  .dialect-list {
    grid-template-columns: 1fr;
  }

  .title-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
