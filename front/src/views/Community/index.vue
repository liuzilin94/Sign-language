<template>
  <div class="community-page">
    <div class="page-header">
      <h1>社区动态</h1>
      <p class="subtitle">与手语学习者交流，分享学习心得</p>
    </div>

    <!-- Tabs -->
    <div class="tabs-bar">
      <button class="publish-btn-native" @click="handlePublishClick">
        <el-icon><Plus /></el-icon>
        发布
      </button>
    </div>

    <!-- Post List -->
    <div class="post-list">
      <div
        v-for="post in posts"
        :key="post.id"
        class="post-card"
      >
        <div class="post-user">
          <div class="user-info" @click="viewUser(post.user)">
            <el-avatar :src="post.user?.avatar" :size="48">
              {{ post.user?.name?.charAt(0) }}
            </el-avatar>
            <div class="user-detail">
              <span class="user-name">{{ post.user?.name }}</span>
              <span class="post-time">{{ formatTime(post.createdAt) }}</span>
            </div>
          </div>
        </div>

        <div class="post-content" @click="viewPost(post)">
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

        <div v-if="post.videoUrl" class="post-video" @click="viewPost(post)">
          <video :src="post.videoUrl" controls />
          <div class="video-overlay">
            <el-icon><VideoPlay /></el-icon>
          </div>
        </div>

        <div class="post-actions">
          <el-button
            :type="post.isLiked ? 'primary' : 'default'"
            text
            @click="toggleLike(post)"
          >
            <el-icon><StarFilled /></el-icon>
            {{ post.likes }}
          </el-button>
          <el-button text @click="viewPost(post)">
            <el-icon><ChatDotSquare /></el-icon>
            {{ post.comments }}
          </el-button>
          <el-button text @click="sharePost(post)">
            <el-icon><Share /></el-icon>
          </el-button>
        </div>

        <!-- Comments Preview -->
        <div v-if="post.commentsList?.length > 0" class="comments-preview">
          <div
            v-for="(comment, index) in post.commentsList.slice(0, 2)"
            :key="index"
            class="comment-item"
          >
            <span class="comment-user">{{ comment.user.name }}:</span>
            <span class="comment-text">{{ comment.content }}</span>
          </div>
          <div v-if="post.comments > 2" class="more-comments" @click="viewPost(post)">
            查看全部 {{ post.comments }} 条评论
          </div>
        </div>
      </div>

      <div v-if="posts.length === 0" class="empty-state">
        <el-icon><ChatLineSquare /></el-icon>
        <h3>暂无动态</h3>
        <p>成为第一个发布内容的人吧</p>
        <el-button type="primary" @click="showCreatePost = true">
          发布动态
        </el-button>
      </div>
    </div>

    <!-- Load More -->
    <div v-if="posts.length > 0" class="load-more">
      <el-button
        v-if="hasMore"
        :loading="loading"
        @click="loadMorePosts"
      >
        加载更多
      </el-button>
      <span v-else class="no-more">没有更多了</span>
    </div>

    <!-- Create Post Modal (Native) -->
    <div v-if="showCreatePost" class="custom-modal-overlay" @click.self="showCreatePost = false">
      <div class="custom-modal" @click.stop>
        <div class="custom-modal-header">
          <h3>发布动态</h3>
          <button class="close-btn" @click="showCreatePost = false">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M1 1L17 17M17 1L1 17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="custom-modal-body">
          <textarea
            v-model="newPostContent"
            class="post-textarea"
            placeholder="分享你的学习心得、提问或展示练习成果..."
            maxlength="500"
          ></textarea>
          <div class="textarea-footer">
            <span class="char-count">{{ newPostContent.length }} / 500</span>
          </div>
          <div class="upload-actions">
            <button class="upload-btn" @click="triggerImageUpload">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>图片</span>
            </button>
            <button class="upload-btn" @click="triggerVideoUpload">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="23 7 16 12 23 17 23 7"/>
                <rect x="1" y="5" width="15" height="14" rx="2"/>
              </svg>
              <span>视频</span>
            </button>
          </div>
          <div v-if="postImages.length > 0" class="preview-images">
            <div v-for="(img, idx) in postImages" :key="idx" class="preview-item">
              <img :src="img.url" alt="预览" />
              <button class="remove-btn" @click="removeImage(idx)">×</button>
            </div>
          </div>
        </div>
        <div class="custom-modal-footer">
          <el-button @click="showCreatePost = false">取消</el-button>
          <el-button type="primary" :loading="posting" @click="submitPost">发布</el-button>
        </div>
      </div>
      <input ref="imageInput" type="file" accept="image/*" multiple style="display:none" @change="handleImageChange" />
      <input ref="videoInput" type="file" accept="video/*" style="display:none" @change="handleVideoChange" />
    </div>

    <!-- Post Detail Dialog -->
    <el-dialog
      v-model="showPostDetail"
      :title="currentPost?.user?.name"
      width="700px"
      class="post-detail-dialog"
    >
      <div class="post-detail" v-if="currentPost">
        <div class="detail-header">
          <el-avatar :src="currentPost.user.avatar" :size="56">
            {{ currentPost.user.name?.charAt(0) }}
          </el-avatar>
          <div class="detail-user">
            <span class="detail-name">{{ currentPost.user.name }}</span>
            <span class="detail-time">{{ formatFullTime(currentPost.createdAt) }}</span>
          </div>
        </div>

        <div class="detail-content">
          <p>{{ currentPost.content }}</p>
        </div>

        <div v-if="currentPost.images?.length > 0" class="detail-images">
          <el-image
            v-for="(img, index) in currentPost.images"
            :key="index"
            :src="img"
            :preview-src-list="currentPost.images"
            fit="cover"
          />
        </div>

        <div v-if="currentPost.videoUrl" class="detail-video">
          <video :src="currentPost.videoUrl" controls />
        </div>

        <div class="detail-actions">
          <el-button
            :type="currentPost.isLiked ? 'primary' : 'default'"
            @click="toggleLike(currentPost)"
          >
            <el-icon><StarFilled /></el-icon>
            {{ currentPost.likes }}
          </el-button>
          <el-button>
            <el-icon><ChatDotSquare /></el-icon>
            {{ currentPost.comments }}
          </el-button>
        </div>

        <div class="detail-comments">
          <h3>评论 ({{ currentPost.comments }})</h3>
          <div class="comment-list">
            <div
              v-for="(comment, index) in currentPost.commentsList"
              :key="index"
              class="comment-item-full"
            >
              <el-avatar :src="comment.user.avatar" :size="36">
                {{ comment.user.name?.charAt(0) }}
              </el-avatar>
              <div class="comment-content">
                <div class="comment-header">
                  <span class="comment-user">{{ comment.user.name }}</span>
                  <span class="comment-time">{{ formatTime(comment.createdAt) }}</span>
                </div>
                <p class="comment-text">{{ comment.content }}</p>
                <div class="comment-actions">
                  <el-button text size="small" @click="likeComment(comment)">
                    <el-icon><StarFilled /></el-icon>
                    {{ comment.likes }}
                  </el-button>
                  <el-button text size="small" @click="replyComment(comment)">
                    回复
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <div class="add-comment">
            <el-input
              v-model="commentContent"
              placeholder="写下你的评论..."
              size="large"
            >
              <template #append>
                <el-button @click="submitComment">发送</el-button>
              </template>
            </el-input>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus,
  VideoPlay,
  StarFilled,
  ChatDotSquare,
  Share,
  ChatLineSquare,
  VideoCamera
} from '@element-plus/icons-vue'
import { communityApi } from '@/api'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

// State
const activeTab = ref('latest')
const showCreatePost = ref(false)
const showPostDetail = ref(false)
const loading = ref(false)
const posting = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)

// New post
const newPostContent = ref('')
const postImages = ref([])
const postVideo = ref([])
const commentContent = ref('')
const imageInput = ref(null)
const videoInput = ref(null)

// Current post
const currentPost = ref(null)

// Posts
const posts = ref([])

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

function formatFullTime(timestamp) {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadPosts() {
  loading.value = true
  try {
    const params = {
      tab: activeTab.value,
      page: currentPage.value,
      limit: 10
    }

    // 如果是"我的"帖子，需要传递当前用户ID
    if (activeTab.value === 'mine') {
      const currentUser = userStore.userInfo
      if (currentUser && currentUser.id) {
        params.user_id = currentUser.id
      }
    }

    const res = await communityApi.getPosts(params)
    // 处理分页格式: {items: [], page, page_size, total, total_pages}
    const data = res.data
    const newPosts = data?.items || data || []

    // 转换后端数据格式为前端期望格式
    const formattedPosts = newPosts.map(post => ({
      id: post.id,
      user: {
        id: post.user_id,
        name: post.username,
        avatar: post.avatar,
        isFollowing: false
      },
      content: post.content,
      images: post.images || [],
      videoUrl: post.video_url,
      likes: post.likes_count || 0,
      comments: post.comments_count || 0,
      commentsList: [],
      isLiked: false,
      createdAt: post.created_at
    }))

    if (currentPage.value === 1) {
      posts.value = formattedPosts
    } else {
      posts.value = [...posts.value, ...formattedPosts]
    }

    hasMore.value = newPosts.length >= 10

    // 加载评论预览
    loadCommentsPreview()

  } catch (error) {
    console.error('加载帖子失败:', error)
    posts.value = []
  }
  loading.value = false
}

// 加载评论预览
async function loadCommentsPreview() {
  // 复制当前帖子列表以便修改
  const updatedPosts = [...posts.value]

  for (let i = 0; i < updatedPosts.length; i++) {
    const post = updatedPosts[i]
    if (post.comments > 0 && post.commentsList.length === 0) {
      try {
        const res = await communityApi.getComments(post.id, { limit: 2 })
        const commentsList = res.data?.items || res.data || []
        updatedPosts[i] = {
          ...post,
          commentsList: commentsList.map(c => ({
            id: c.id,
            user: {
              id: c.user_id,
              name: c.username,
              avatar: c.avatar
            },
            content: c.content,
            likes: 0,
            createdAt: c.created_at
          }))
        }
      } catch (e) {
        console.error('加载评论失败:', e)
      }
    }
  }

  posts.value = updatedPosts
}

async function loadMorePosts() {
  currentPage.value++
  await loadPosts()
}

async function viewPost(post) {
  currentPost.value = { ...post }
  showPostDetail.value = true

  // 加载完整评论列表
  try {
    const res = await communityApi.getComments(post.id, { limit: 20 })
    const commentsList = res.data?.items || res.data || []
    currentPost.value.commentsList = commentsList.map(c => ({
      id: c.id,
      user: {
        id: c.user_id,
        name: c.username,
        avatar: c.avatar
      },
      content: c.content,
      likes: 0,
      createdAt: c.created_at
    }))
  } catch (e) {
    console.error('加载评论失败:', e)
  }
}

function viewUser(user) {
  router.push(`/profile/${user.id}`)
}

async function toggleLike(post) {
  try {
    await communityApi.likePost(post.id)
    post.isLiked = !post.isLiked
    post.likes += post.isLiked ? 1 : -1
  } catch (e) {
    console.error('点赞失败:', e)
  }
}

function sharePost(post) {
  navigator.clipboard.writeText(`${window.location.origin}/community/post/${post.id}`)
  ElMessage.success('分享链接已复制')
}

async function submitPost() {
  if (!newPostContent.value.trim()) {
    ElMessage.warning('请输入内容')
    return
  }

  posting.value = true
  try {
    // 构建 FormData（支持多图片）
    const formData = new FormData()
    formData.append('content', newPostContent.value)
    postImages.value.forEach((img, idx) => {
      formData.append('images', img.file)
    })
    if (postVideo.value.length > 0) {
      formData.append('video', postVideo.value[0].file)
    }

    await communityApi.createPost(formData, true)
    ElMessage.success('发布成功')
    showCreatePost.value = false
    newPostContent.value = ''
    postImages.value = []
    postVideo.value = []
    // 刷新列表
    currentPage.value = 1
    await loadPosts()
  } catch (error) {
    ElMessage.error('发布失败: ' + (error.message || ''))
  }
  posting.value = false
}

async function submitComment() {
  if (!commentContent.value.trim() || !currentPost.value) return

  try {
    await communityApi.createComment(currentPost.value.id, commentContent.value)
    // 刷新评论
    const commentsRes = await communityApi.getComments(currentPost.value.id, { limit: 20 })
    const commentsList = commentsRes.data?.list || []
    // 转换评论格式
    currentPost.value.commentsList = commentsList.map(c => ({
      id: c.id,
      user: {
        id: c.user_id,
        name: c.username,
        avatar: c.avatar
      },
      content: c.content,
      likes: 0,
      createdAt: c.created_at
    }))
    currentPost.value.comments++
    commentContent.value = ''
  } catch (e) {
    console.error('评论失败:', e)
  }
}

function likeComment(comment) {
  comment.likes++
}

function replyComment(comment) {
  commentContent.value = `@${comment.user.name} `
}

onMounted(() => {
  loadPosts()
})

function loadMockPosts() {
  posts.value = []
}

async function handleTabChange() {
  currentPage.value = 1
  hasMore.value = true
  await loadPosts()
}

function handlePublishClick() {
  showCreatePost.value = true
}

function triggerImageUpload() {
  imageInput.value?.click()
}

function triggerVideoUpload() {
  videoInput.value?.click()
}

function handleImageChange(e) {
  const files = e.target.files
  if (!files) return
  for (let i = 0; i < Math.min(files.length, 9 - postImages.value.length); i++) {
    const file = files[i]
    const reader = new FileReader()
    reader.onload = (ev) => {
      postImages.value.push({ url: ev.target.result, file })
    }
    reader.readAsDataURL(file)
  }
  e.target.value = ''
}

function handleVideoChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    postVideo.value = [{ url: ev.target.result, file }]
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

function removeImage(idx) {
  postImages.value.splice(idx, 1)
}

// 弹窗打开时禁止背景滚动
watch(showCreatePost, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
  if (val) {
    setTimeout(() => {
      const overlay = document.querySelector('.custom-modal-overlay')
      console.log('[modal] rendered:', overlay !== null)
    }, 200)
  }
})
</script>

<style scoped>
.community-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px 80px;
  position: relative;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #0d0d0d;
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #8a8a8a;
}

/* Tabs Bar */
.tabs-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 4px;

  :deep(.el-tabs) {
    flex: 1;
  }
}

.publish-btn-native {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: #6c63ff;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  flex-shrink: 0;

  &:hover {
    background: #5a52e0;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(108, 99, 255, 0.35);
  }

  &:active {
    transform: translateY(0);
  }
}

/* Post List */
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
  transition: all 180ms ease;
}

.post-card:hover {
  border-color: #0d0d0d;
}

.post-user {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.user-detail {
  display: flex;
  flex-direction: column;
}

.user-name {
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
  cursor: pointer;
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
  cursor: pointer;
}

.post-video {
  position: relative;
  margin-bottom: 16px;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
}

.post-video video {
  width: 100%;
  max-height: 400px;
}

.video-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 48px;
  opacity: 0;
  transition: opacity 180ms ease;
}

.post-video:hover .video-overlay {
  opacity: 1;
}

.post-actions {
  display: flex;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0ee;
}

.comments-preview {
  margin-top: 16px;
  padding: 16px;
  background: #fafaf8;
  border-radius: 8px;
}

.comment-item {
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.comment-item:last-child {
  margin-bottom: 0;
}

.comment-user {
  font-weight: 600;
  color: #0d0d0d;
}

.comment-text {
  color: #0d0d0d;
}

.more-comments {
  font-size: 13px;
  color: #8a8a8a;
  cursor: pointer;
  margin-top: 8px;
}

.more-comments:hover {
  color: #409eff;
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

/* Load More */
.load-more {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.no-more {
  font-size: 14px;
  color: #8a8a8a;
}

/* Create Post */
.create-post-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-options {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

/* Post Detail */
.post-detail {
  padding: 8px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.detail-user {
  display: flex;
  flex-direction: column;
}

.detail-name {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
}

.detail-time {
  font-size: 13px;
  color: #8a8a8a;
}

.detail-content {
  margin-bottom: 20px;
}

.detail-content p {
  font-size: 15px;
  color: #0d0d0d;
  line-height: 1.8;
}

.detail-images {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 20px;
}

.detail-images .el-image {
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
}

.detail-video {
  margin-bottom: 20px;
}

.detail-video video {
  width: 100%;
  border-radius: 10px;
}

.detail-actions {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  border-top: 1px solid #e8e8e8;
  border-bottom: 1px solid #e8e8e8;
  margin-bottom: 20px;
}

.detail-comments h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 16px;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
  max-height: 300px;
  overflow-y: auto;
}

.comment-item-full {
  display: flex;
  gap: 12px;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.comment-header .comment-user {
  font-size: 14px;
}

.comment-time {
  font-size: 12px;
  color: #8a8a8a;
}

.comment-content .comment-text {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.comment-actions {
  display: flex;
  gap: 16px;
}

.add-comment {
  padding-top: 16px;
  border-top: 1px solid #e8e8e8;
}

/* Custom Post Modal */
.custom-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
}

.custom-modal {
  background: #fff;
  border-radius: 16px;
  width: 560px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.custom-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e8e8;

  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
  }

  .close-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: #999;
    padding: 4px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;

    &:hover {
      background: #f0f0f0;
      color: #333;
    }
  }
}

.custom-modal-body {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.post-textarea {
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 15px;
  line-height: 1.6;
  resize: none;
  font-family: inherit;
  color: #333;
  box-sizing: border-box;
  min-height: 140px;
  outline: none;
  transition: border-color 0.2s;

  &:focus {
    border-color: #6c63ff;
  }

  &::placeholder {
    color: #b0b0b0;
  }
}

.textarea-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;

  .char-count {
    font-size: 12px;
    color: #b0b0b0;
  }
}

.upload-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #6c63ff;
    color: #6c63ff;
    background: #f8f6ff;
  }
}

.preview-images {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 16px;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .remove-btn {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 22px;
    height: 22px;
    background: rgba(0, 0, 0, 0.6);
    border: none;
    border-radius: 50%;
    color: #fff;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
  }
}

.custom-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e8e8e8;
}

@media (max-width: 768px) {
  .post-images {
    grid-template-columns: repeat(2, 1fr);
  }

  .detail-images {
    grid-template-columns: 1fr;
  }

  .custom-modal {
    width: 95vw;
  }
}
</style>
