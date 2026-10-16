<template>
  <div class="community-page">
    <div class="page-header">
      <h2>社区动态</h2>
      <el-button type="primary" @click="showPostDialog = true">
        <el-icon><Plus /></el-icon>
        发布动态
      </el-button>
    </div>
    
    <div class="filter-tabs">
      <el-radio-group v-model="activeFilter" @change="handleFilterChange">
        <el-radio-button label="latest">最新</el-radio-button>
        <el-radio-button label="hot">最热</el-radio-button>
        <el-radio-button label="following">关注</el-radio-button>
      </el-radio-group>
    </div>
    
    <div class="post-list">
      <div v-for="post in postList" :key="post.id" class="post-card">
        <div class="post-header">
          <img :src="post.avatar" alt="" class="avatar" @error="handleAvatarError" />
          <div class="user-info">
            <span class="username">{{ post.username }}</span>
            <span class="time">{{ post.createTime }}</span>
          </div>
          <el-button text @click="followUser(post.userId)">
            {{ post.isFollowing ? '已关注' : '关注' }}
          </el-button>
        </div>
        
        <div class="post-content" @click="goToDetail(post.id)">
          <p>{{ post.content }}</p>
          <div class="post-images" v-if="post.images && post.images.length">
            <img
              v-for="(img, index) in post.images"
              :key="index"
              :src="img"
              alt=""
              @error="handleImageError"
            />
          </div>
          <div class="post-video" v-if="post.video">
            <div class="video-placeholder">视频演示区域</div>
          </div>
        </div>
        
        <div class="post-actions">
          <span class="action-item" @click="likePost(post)">
            <el-icon :class="{ active: post.isLiked }"><Star /></el-icon>
            {{ post.likes }}
          </span>
          <span class="action-item" @click="showComment(post.id)">
            <el-icon><ChatLineSquare /></el-icon>
            {{ post.comments }}
          </span>
          <span class="action-item" @click="sharePost(post)">
            <el-icon><Share /></el-icon>
            分享
          </span>
        </div>
        
        <div class="post-comments" v-if="post.showComments">
          <div class="comment-list">
            <div v-for="comment in post.commentList" :key="comment.id" class="comment-item">
              <img :src="comment.avatar" alt="" class="comment-avatar" />
              <div class="comment-content">
                <span class="comment-user">{{ comment.username }}</span>
                <p>{{ comment.content }}</p>
              </div>
            </div>
          </div>
          <div class="comment-input">
            <el-input
              v-model="post.newComment"
              placeholder="写下你的评论..."
              @keyup.enter="addComment(post)"
            />
            <el-button type="primary" size="small" @click="addComment(post)">发送</el-button>
          </div>
        </div>
      </div>
      
      <div class="load-more" v-if="hasMore">
        <el-button @click="loadMore" :loading="loadingMore">加载更多</el-button>
      </div>
      
      <EmptyState v-if="postList.length === 0" text="暂无动态">
        <template #action>
          <el-button type="primary" @click="showPostDialog = true">发布第一条动态</el-button>
        </template>
      </EmptyState>
    </div>
    
    <el-dialog v-model="showPostDialog" title="发布动态" width="500px">
      <el-form :model="postForm" label-width="80px">
        <el-form-item label="内容">
          <el-input
            v-model="postForm.content"
            type="textarea"
            :rows="4"
            placeholder="分享你的手语学习心得..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="添加图片">
          <el-upload
            action="#"
            :auto-upload="false"
            :on-change="handleImageSelect"
            :file-list="postForm.images"
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="添加视频">
          <el-upload
            action="#"
            :auto-upload="false"
            :on-change="handleVideoSelect"
          >
            <el-button>选择视频</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPostDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPost" :loading="submitting">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus, Star, ChatLineSquare, Share } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { communityApi } from '@/api'
import EmptyState from '@/components/EmptyState/index.vue'

const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjM1IiByPSIyNSIgZmlsbD0iI2Q0ZDRkNCIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNzUiIHI9IjMwIiBmaWxsPSIjZDRkNGQ0Ii8+PC9zdmc+'

const activeFilter = ref('latest')
const showPostDialog = ref(false)
const loadingMore = ref(false)
const submitting = ref(false)
const hasMore = ref(true)

const postList = ref([
  {
    id: 1,
    userId: 1,
    username: '手语达人小王',
    avatar: defaultAvatar,
    content: '今天学习了十个常用手语词汇，感觉很有成就感！每天进步一点点。',
    images: [],
    video: '',
    likes: 128,
    comments: 23,
    createTime: '2小时前',
    isLiked: false,
    isFollowing: false,
    showComments: false,
    newComment: '',
    commentList: [
      { id: 1, username: '学习者', avatar: defaultAvatar, content: '太棒了，继续加油！' },
      { id: 2, username: '手语爱好者', avatar: defaultAvatar, content: '有什么技巧分享吗？' }
    ]
  },
  {
    id: 2,
    userId: 2,
    username: '聋人朋友',
    avatar: defaultAvatar,
    content: '分享一个学习手语的小技巧给大家',
    images: [],
    video: '',
    likes: 256,
    comments: 45,
    createTime: '5小时前',
    isLiked: true,
    isFollowing: true,
    showComments: false,
    newComment: '',
    commentList: []
  },
  {
    id: 3,
    userId: 3,
    username: '手语教师李老师',
    avatar: defaultAvatar,
    content: '新手入门必看！手语基础动作分解演示',
    images: [],
    video: '',
    likes: 512,
    comments: 89,
    createTime: '1天前',
    isLiked: false,
    isFollowing: false,
    showComments: false,
    newComment: '',
    commentList: []
  }
])

const postForm = ref({
  content: '',
  images: [],
  video: null
})

function handleFilterChange() {
  console.log('筛选:', activeFilter.value)
}

function handleAvatarError(e) {
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="35" r="25" fill="%23ddd"/><circle cx="50" cy="75" r="30" fill="%23ddd"/></svg>'
}

function handleImageError(e) {
  e.target.style.display = 'none'
}

function goToDetail(id) {
  console.log('查看详情:', id)
}

function likePost(post) {
  post.isLiked = !post.isLiked
  post.likes += post.isLiked ? 1 : -1
}

function followUser(userId) {
  const post = postList.value.find(p => p.userId === userId)
  if (post) {
    post.isFollowing = !post.isFollowing
    ElMessage.success(post.isFollowing ? '关注成功' : '取消关注')
  }
}

function showComment(postId) {
  const post = postList.value.find(p => p.id === postId)
  if (post) {
    post.showComments = !post.showComments
  }
}

function addComment(post) {
  if (!post.newComment.trim()) return
  post.commentList.push({
    id: Date.now(),
    username: '我',
    avatar: defaultAvatar,
    content: post.newComment
  })
  post.comments++
  post.newComment = ''
}

function sharePost(post) {
  ElMessage.success('分享链接已复制')
}

function handleImageSelect(file, fileList) {
  postForm.value.images = fileList
}

function handleVideoSelect(file) {
  postForm.value.video = file
}

async function submitPost() {
  if (!postForm.value.content.trim()) {
    ElMessage.warning('请输入内容')
    return
  }
  
  submitting.value = true
  await new Promise(r => setTimeout(r, 1000))
  submitting.value = false
  
  postList.value.unshift({
    id: Date.now(),
    userId: 0,
    username: '我',
    avatar: defaultAvatar,
    content: postForm.value.content,
    images: postForm.value.images.map(f => f.url),
    video: '',
    likes: 0,
    comments: 0,
    createTime: '刚刚',
    isLiked: false,
    isFollowing: false,
    showComments: false,
    newComment: '',
    commentList: []
  })
  
  showPostDialog.value = false
  postForm.value = { content: '', images: [], video: null }
  ElMessage.success('发布成功')
}

function loadMore() {
  loadingMore.value = true
  setTimeout(() => {
    loadingMore.value = false
    hasMore.value = false
  }, 1000)
}
</script>

<style scoped lang="scss">
.community-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  padding-bottom: 80px;
  background: #fff;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
      font-size: 24px;
      color: #333;
      margin: 0;
    }
  }
  
  .filter-tabs {
    margin-bottom: 20px;
  }
  
  .post-list {
    .post-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 16px;
      
      .post-header {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        
        .avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: #ddd;
          margin-right: 12px;
        }
        
        .user-info {
          flex: 1;
          display: flex;
          flex-direction: column;
          
          .username {
            font-weight: bold;
            color: #333;
          }
          
          .time {
            font-size: 12px;
            color: #999;
          }
        }
      }
      
      .post-content {
        margin-bottom: 12px;
        
        p {
          color: #333;
          line-height: 1.6;
          margin-bottom: 12px;
        }
        
        .post-images {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 8px;
          margin-bottom: 12px;
          
          img {
            width: 100%;
            aspect-ratio: 1;
            object-fit: cover;
            border-radius: 8px;
            cursor: pointer;
          }
        }
        
        .post-video {
          border-radius: 8px;
          overflow: hidden;
          
          .video-placeholder {
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 14px;
          }
        }
      }
      
      .post-actions {
        display: flex;
        gap: 24px;
        padding-top: 12px;
        border-top: 1px solid #f0f0f0;
        
        .action-item {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #999;
          cursor: pointer;
          font-size: 14px;
          
          &:hover {
            color: #667eea;
          }
          
          .el-icon.active {
            color: #667eea;
          }
        }
      }
      
      .post-comments {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #f0f0f0;
        
        .comment-list {
          margin-bottom: 16px;
          
          .comment-item {
            display: flex;
            gap: 10px;
            margin-bottom: 12px;
            
            .comment-avatar {
              width: 32px;
              height: 32px;
              border-radius: 50%;
              background: #ddd;
              flex-shrink: 0;
            }
            
            .comment-content {
              flex: 1;
              
              .comment-user {
                font-size: 13px;
                font-weight: bold;
                color: #333;
              }
              
              p {
                margin: 4px 0 0;
                font-size: 14px;
                color: #666;
              }
            }
          }
        }
        
        .comment-input {
          display: flex;
          gap: 8px;
          
          .el-input {
            flex: 1;
          }
        }
      }
    }
    
    .load-more {
      text-align: center;
      padding: 20px;
    }
  }
}

@media (max-width: 768px) {
  .community-page {
    .post-list .post-card .post-content .post-images {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}
</style>
