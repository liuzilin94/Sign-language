<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="header-bg"></div>
      <div class="profile-info">
        <div class="avatar-section">
          <el-avatar
            :src="userInfo.avatar"
            :size="120"
            class="avatar"
          >
            {{ userInfo.name?.charAt(0) }}
          </el-avatar>
          <el-button
            v-if="isOwnProfile"
            size="small"
            class="edit-avatar-btn"
            @click="triggerAvatarUpload"
          >
            <el-icon><Camera /></el-icon>
          </el-button>
          <input
            ref="avatarInput"
            type="file"
            accept="image/*"
            style="display:none"
            @change="handleAvatarChange"
          />
        </div>
        <div class="info-content">
          <div class="name-row">
            <h1>{{ userInfo.name }}</h1>
            <el-tag v-if="userInfo.isVip" type="warning" size="small">
              <el-icon><Star /></el-icon>
              VIP
            </el-tag>
            <el-button
              v-if="!isOwnProfile"
              :type="isFollowing ? 'default' : 'primary'"
              size="small"
              @click="toggleFollow"
            >
              <el-icon v-if="isFollowing"><Check /></el-icon>
              <el-icon v-else><Plus /></el-icon>
              {{ isFollowing ? '已关注' : '关注' }}
            </el-button>
          </div>
          <p class="bio">{{ userInfo.bio || '这个人很懒，什么都没写' }}</p>
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.level }}</span>
              <span class="stat-label">等级</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.points }}</span>
              <span class="stat-label">积分</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.following }}</span>
              <span class="stat-label">关注</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.followers }}</span>
              <span class="stat-label">粉丝</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.likes }}</span>
              <span class="stat-label">获赞</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.learningDays }}</span>
              <span class="stat-label">学习天数</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="profile-tabs">
      <el-tabs v-model="activeTab">
        <el-tab-pane name="posts">
          <template #label>
            <span class="tab-label">
              <el-icon><Document /></el-icon>
              动态
              <span v-if="userInfo.postsCount > 0" class="tab-count">{{ userInfo.postsCount }}</span>
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="学习" name="learning">
          <template #label>
            <span class="tab-label">
              <el-icon><Reading /></el-icon>
              学习
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="收藏" name="favorites">
          <template #label>
            <span class="tab-label">
              <el-icon><Star /></el-icon>
              收藏
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Posts Tab -->
    <div v-if="activeTab === 'posts'" class="tab-content">
      <div v-if="posts.length > 0" class="post-list">
        <div
          v-for="post in posts"
          :key="post.id"
          class="post-card"
          @click="viewPost(post)"
        >
          <div class="post-header">
            <div class="post-user">
              <el-avatar :src="userInfo.avatar" :size="40">
                {{ userInfo.name?.charAt(0) }}
              </el-avatar>
              <div class="user-info">
                <span class="username">{{ userInfo.name }}</span>
                <span class="post-time">{{ formatTime(post.createdAt) }}</span>
              </div>
            </div>
            <el-dropdown trigger="click">
              <el-button text size="small">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="isOwnProfile" @click="editPost(post)">编辑</el-dropdown-item>
                  <el-dropdown-item v-if="isOwnProfile" @click="deletePost(post)" divided>删除</el-dropdown-item>
                  <el-dropdown-item @click="reportPost(post)">举报</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <div class="post-content">
            <p>{{ post.content }}</p>
          </div>

          <div v-if="post.images?.length > 0" class="post-images">
            <el-image
              v-for="(img, index) in post.images"
              :key="index"
              :src="img"
              :preview-src-list="post.images"
              fit="cover"
              class="post-image"
            />
          </div>

          <div v-if="post.videoUrl" class="post-video">
            <video :src="post.videoUrl" controls />
          </div>

          <div class="post-actions">
            <el-button
              :type="post.isLiked ? 'primary' : 'default'"
              text
              @click.stop="toggleLike(post)"
            >
              <el-icon><StarFilled /></el-icon>
              {{ post.likes }}
            </el-button>
            <el-button text @click.stop="openComments(post)">
              <el-icon><ChatDotSquare /></el-icon>
              {{ post.comments }}
            </el-button>
            <el-button text @click.stop="sharePost(post)">
              <el-icon><Share /></el-icon>
              分享
            </el-button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <el-icon><Document /></el-icon>
        <h3>暂无动态</h3>
        <p>{{ isOwnProfile ? '发布你的第一条动态吧' : '还没有发布任何动态' }}</p>
        <el-button v-if="isOwnProfile" type="primary" @click="createPost">
          <el-icon><Plus /></el-icon>
          发布动态
        </el-button>
      </div>
    </div>

    <!-- Learning Tab -->
    <div v-if="activeTab === 'learning'" class="tab-content">
      <div class="learning-stats">
        <div class="stat-card">
          <div class="stat-icon" style="background: #e8f5e9">
            <el-icon color="#4caf50"><Collection /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ learnedWords.length }}</span>
            <span class="stat-label">已学词汇</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: #e3f2fd">
            <el-icon color="#2196f3"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalPracticeTime }}</span>
            <span class="stat-label">累计练习(分钟)</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: #fff3e0">
            <el-icon color="#ff9800"><Trophy /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ achievementsCount }}</span>
            <span class="stat-label">获得成就</span>
          </div>
        </div>
      </div>

      <div class="section-title">
        <h3>已学词汇</h3>
        <el-select v-model="wordFilter" placeholder="筛选" clearable>
          <el-option label="全部" value="all" />
          <el-option label="入门" value="beginner" />
          <el-option label="基础" value="basic" />
          <el-option label="进阶" value="intermediate" />
          <el-option label="高级" value="advanced" />
        </el-select>
      </div>

      <div v-if="filteredLearnedWords.length > 0" class="word-list">
        <div
          v-for="word in filteredLearnedWords"
          :key="word.id"
          class="word-item"
          @click="viewWord(word)"
        >
          <div class="word-preview">
            <video v-if="word.videoUrl" :src="word.videoUrl" muted loop />
            <div v-else class="word-placeholder">
              <el-icon><VideoPlay /></el-icon>
            </div>
          </div>
          <div class="word-info">
            <h4>{{ word.title }}</h4>
            <div class="word-meta">
              <el-tag size="small" :type="getDifficultyType(word.difficulty)">
                {{ getDifficultyLabel(word.difficulty) }}
              </el-tag>
              <span class="learn-date">学习于 {{ word.learnDate }}</span>
            </div>
          </div>
          <div class="word-progress">
            <el-progress
              type="circle"
              :percentage="word.mastery"
              :width="40"
              :stroke-width="4"
            />
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <el-icon><Collection /></el-icon>
        <h3>暂无已学词汇</h3>
        <p>开始学习，记录你的成长</p>
        <el-button v-if="isOwnProfile" type="primary" @click="goToPractice">
          开始学习
        </el-button>
      </div>
    </div>

    <!-- Favorites Tab -->
    <div v-if="activeTab === 'favorites'" class="tab-content">
      <div v-if="favorites.length > 0" class="favorite-list">
        <div
          v-for="item in favorites"
          :key="item.id"
          class="favorite-item"
          @click="viewFavorite(item)"
        >
          <div class="favorite-preview">
            <video v-if="item.videoUrl" :src="item.videoUrl" muted loop />
            <el-image v-else-if="item.cover" :src="item.cover" fit="cover" />
            <div v-else class="favorite-placeholder">
              <el-icon><Star /></el-icon>
            </div>
          </div>
          <div class="favorite-info">
            <h4>{{ item.title }}</h4>
            <p class="favorite-desc">{{ item.description }}</p>
            <div class="favorite-meta">
              <span class="type-tag">{{ getTypeLabel(item.type) }}</span>
              <span class="favorite-time">{{ formatTime(item.createdAt) }}</span>
            </div>
          </div>
          <el-button
            class="unfavorite-btn"
            text
            @click.stop="removeFavorite(item)"
          >
            <el-icon><Star /></el-icon>
          </el-button>
        </div>
      </div>

      <div v-else class="empty-state">
        <el-icon><Star /></el-icon>
        <h3>暂无收藏</h3>
        <p>收藏你喜欢的词汇和内容</p>
        <el-button v-if="isOwnProfile" type="primary" @click="goToDictionary">
          去词库
        </el-button>
      </div>
    </div>

    <!-- Create Post Dialog -->
    <el-dialog
      v-model="showCreatePost"
      title="发布动态"
      width="600px"
    >
      <div class="create-post-form">
        <el-input
          v-model="newPostContent"
          type="textarea"
          :rows="4"
          placeholder="分享你的学习心得..."
          maxlength="500"
          show-word-limit
        />
        <div class="upload-section">
          <el-upload
            action="#"
            :auto-upload="false"
            :limit="9"
            list-type="picture-card"
            v-model:file-list="postImages"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </div>
      </div>
      <template #footer>
        <el-button @click="showCreatePost = false">取消</el-button>
        <el-button type="primary" @click="submitPost">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import { learningApi, authApi, userApi } from '@/api'
import {
  Camera,
  Star,
  Check,
  Plus,
  Document,
  Reading,
  MoreFilled,
  StarFilled,
  ChatDotSquare,
  Share,
  Collection,
  Timer,
  Trophy,
  VideoPlay
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// State
const activeTab = ref('posts')
const isOwnProfile = ref(true)
const isFollowing = ref(false)
const wordFilter = ref('all')

// User info - 从API获取
const userInfo = ref({
  id: null,
  name: '用户',
  avatar: '',
  bio: '这个人很懒，什么都没写',
  level: 1,
  points: 0,
  following: 0,
  followers: 0,
  likes: 0,
  learningDays: 0,
  postsCount: 0,
  isVip: false
})

// Posts
const posts = ref([])
const showCreatePost = ref(false)
const newPostContent = ref('')
const postImages = ref([])
const avatarInput = ref(null)

// Learned words - 从API获取
const learnedWords = ref([])
const totalPracticeTime = ref(0)
const achievementsCount = ref(0)

// Favorites
const favorites = ref([])

// Methods
function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

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

function getTypeLabel(type) {
  const labels = {
    word: '词汇',
    article: '文章',
    video: '视频'
  }
  return labels[type] || type
}

const filteredLearnedWords = computed(() => {
  if (!wordFilter.value || wordFilter.value === 'all') {
    return learnedWords.value
  }
  return learnedWords.value.filter(w => w.difficulty === wordFilter.value)
})

function triggerAvatarUpload() {
  avatarInput.value?.click()
}

async function handleAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return

  const formData = new FormData()
  formData.append('avatar', file)

  try {
    const res = await userApi.uploadAvatar(formData)
    if (res.data?.data?.avatar) {
      userInfo.value.avatar = res.data.data.avatar
      ElMessage.success('头像上传成功')
    }
  } catch (e) {
    console.error('头像上传失败:', e)
    ElMessage.error('头像上传失败')
  }

  e.target.value = ''
}

async function toggleFollow() {
  if (isFollowing.value) {
    isFollowing.value = false
    userInfo.value.followers--
    ElMessage.success('已取消关注')
  } else {
    isFollowing.value = true
    userInfo.value.followers++
    ElMessage.success('关注成功')
  }
}

function viewPost(post) {
  router.push(`/community/post/${post.id}`)
}

function editPost(post) {
  ElMessage.info('编辑功能开发中')
}

async function deletePost(post) {
  await ElMessageBox.confirm('确定要删除这条动态吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })

  const index = posts.value.findIndex(p => p.id === post.id)
  if (index > -1) {
    posts.value.splice(index, 1)
  }
  ElMessage.success('删除成功')
}

function reportPost(post) {
  ElMessage.info('举报功能开发中')
}

async function toggleLike(post) {
  post.isLiked = !post.isLiked
  post.likes += post.isLiked ? 1 : -1
}

function openComments(post) {
  router.push(`/community/post/${post.id}#comments`)
}

function sharePost(post) {
  ElMessage.success('分享链接已复制')
}

function createPost() {
  showCreatePost.value = true
}

async function submitPost() {
  if (!newPostContent.value.trim()) {
    ElMessage.warning('请输入内容')
    return
  }

  const newPost = {
    id: Date.now(),
    content: newPostContent.value,
    images: postImages.value.map(f => f.url),
    likes: 0,
    comments: 0,
    isLiked: false,
    createdAt: Date.now()
  }

  posts.value.unshift(newPost)
  showCreatePost.value = false
  newPostContent.value = ''
  postImages.value = []
  ElMessage.success('发布成功')
}

function viewWord(word) {
  router.push(`/dictionary/${word.id}`)
}

function viewFavorite(item) {
  if (item.type === 'word') {
    router.push(`/dictionary/${item.id}`)
  }
}

async function removeFavorite(item) {
  await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })

  const index = favorites.value.findIndex(f => f.id === item.id)
  if (index > -1) {
    favorites.value.splice(index, 1)
  }
  ElMessage.success('已取消收藏')
}

function goToPractice() {
  router.push('/practice')
}

function goToDictionary() {
  router.push('/dictionary')
}

async function loadUserProfile() {
  try {
    // 获取当前登录用户信息
    const res = await authApi.getMe()
    if (res.data) {
      const data = res.data.data || res.data
      userInfo.value = {
        id: data.id,
        name: data.username || data.name || '用户',
        avatar: data.avatar_url || '',
        bio: '这个人很懒，什么都没写',
        level: data.level || 1,
        points: data.points || 0,
        following: data.following || 0,
        followers: data.followers || 0,
        likes: data.total_likes || 0,
        learningDays: data.streak_days || 0,
        postsCount: data.posts_count || 0,
        isVip: data.role === 'vip'
      }
    }
  } catch (e) {
    console.error('获取用户信息失败:', e)
  }

  // 加载用户学习数据
  loadLearningData()
}

async function loadLearningData() {
  try {
    // 获取学习记录
    const recordsRes = await learningApi.getRecords()
    if (recordsRes.data) {
      const records = Array.isArray(recordsRes.data) ? recordsRes.data : (recordsRes.data.list || [])
      learnedWords.value = records.map(record => ({
        id: record.word_id || record.id,
        title: record.word || record.word_name || '未知词汇',
        difficulty: record.difficulty || 'basic',
        learnDate: record.learned_at ? new Date(record.learned_at).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }) : '',
        mastery: record.mastery || record.accuracy || 0,
        videoUrl: record.video_url || ''
      }))

      // 计算累计练习时间（估算）
      totalPracticeTime.value = records.length * 5

      // 计算成就数量（估算）
      achievementsCount.value = Math.floor(records.length / 10)
    }
  } catch (e) {
    console.error('获取学习记录失败:', e)
  }
}

onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
.profile-page {
  max-width: 900px;
  margin: 0 auto;
}

.profile-header {
  position: relative;
  margin-bottom: 24px;
}

.header-bg {
  height: 180px;
  background: #f0f0f0;
  border-radius: 16px 16px 0 0;
}

.profile-info {
  display: flex;
  gap: 32px;
  padding: 0 32px;
  margin-top: -60px;
}

.avatar-section {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  border: 4px solid #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.edit-avatar-btn {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 50%;
}

.info-content {
  padding-top: 72px;
  flex: 1;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.name-row h1 {
  font-size: 26px;
  font-weight: 700;
  color: #0d0d0d;
  letter-spacing: -0.5px;
}

.bio {
  font-size: 14px;
  color: #8a8a8a;
  margin-bottom: 20px;
}

.user-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-item .stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #0d0d0d;
}

.stat-item .stat-label {
  font-size: 12px;
  color: #8a8a8a;
}

.profile-tabs {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 0 24px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-count {
  font-size: 12px;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 4px;
}

.tab-content {
  margin-top: 24px;
}

/* Posts */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
  cursor: pointer;
  transition: all 180ms ease;
}

.post-card:hover {
  border-color: #0d0d0d;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.post-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 15px;
  font-weight: 600;
  color: #0d0d0d;
}

.post-time {
  font-size: 12px;
  color: #8a8a8a;
}

.post-content {
  margin-bottom: 16px;
}

.post-content p {
  font-size: 14px;
  color: #0d0d0d;
  line-height: 1.7;
  margin: 0;
}

.post-images {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.post-image {
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
}

.post-video {
  margin-bottom: 16px;
}

.post-video video {
  width: 100%;
  border-radius: 8px;
}

.post-actions {
  display: flex;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #e8e8e8;
}

/* Learning */
.learning-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.learning-stats .stat-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.learning-stats .stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.learning-stats .stat-info {
  display: flex;
  flex-direction: column;
}

.learning-stats .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #0d0d0d;
}

.learning-stats .stat-label {
  font-size: 12px;
  color: #8a8a8a;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #0d0d0d;
}

.word-list {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  overflow: hidden;
}

.word-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
  cursor: pointer;
  transition: background 180ms ease;
}

.word-item:last-child {
  border-bottom: none;
}

.word-item:hover {
  background: #fafaf8;
}

.word-preview {
  width: 80px;
  height: 60px;
  background: #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.word-preview video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.word-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a8a8a;
}

.word-info {
  flex: 1;
}

.word-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 6px;
}

.word-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.learn-date {
  font-size: 12px;
  color: #8a8a8a;
}

.word-progress {
  flex-shrink: 0;
}

/* Favorites */
.favorite-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.favorite-item {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 180ms ease;
}

.favorite-item:hover {
  border-color: #0d0d0d;
}

.favorite-preview {
  width: 100px;
  height: 70px;
  background: #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.favorite-preview video,
.favorite-preview .el-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.favorite-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a8a8a;
  font-size: 24px;
}

.favorite-info {
  flex: 1;
  min-width: 0;
}

.favorite-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 4px;
}

.favorite-desc {
  font-size: 13px;
  color: #8a8a8a;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.favorite-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-tag {
  font-size: 12px;
  padding: 2px 8px;
  background: #f0f7ff;
  color: #409eff;
  border-radius: 4px;
}

.favorite-time {
  font-size: 12px;
  color: #8a8a8a;
}

.unfavorite-btn {
  color: #e6a23c;
}

/* Empty State */
.empty-state {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 60px 24px;
  text-align: center;
}

.empty-state .el-icon {
  font-size: 64px;
  color: #dcdfe6;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 14px;
  color: #8a8a8a;
  margin-bottom: 20px;
}

/* Create Post */
.create-post-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-section {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .profile-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 0 16px;
  }

  .info-content {
    padding-top: 24px;
  }

  .user-stats {
    flex-wrap: wrap;
    justify-content: center;
    gap: 24px;
  }

  .learning-stats {
    grid-template-columns: 1fr;
  }

  .post-images {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
