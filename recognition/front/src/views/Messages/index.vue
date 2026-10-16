<template>
  <div class="messages-page">
    <div class="page-header">
      <h2>消息中心</h2>
      <el-button text @click="markAllRead" v-if="unreadCount > 0">
        <el-icon><Check /></el-icon>
        全部已读
      </el-button>
    </div>
    
    <div class="message-tabs">
      <el-radio-group v-model="activeTab" @change="handleTabChange">
        <el-radio-button value="all">
          全部
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" />
        </el-radio-button>
        <el-radio-button value="audit">审核通知</el-radio-button>
        <el-radio-button value="learn">学习提醒</el-radio-button>
        <el-radio-button value="community">社区互动</el-radio-button>
      </el-radio-group>
    </div>
    
    <div class="message-list">
      <div
        v-for="message in filteredMessages"
        :key="message.id"
        class="message-item"
        :class="{ unread: !message.read }"
        @click="handleMessageClick(message)"
      >
        <div class="message-icon">
          <el-icon :class="getIconClass(message.type)">
            <component :is="getIcon(message.type)" />
          </el-icon>
        </div>
        
        <div class="message-content">
          <div class="message-header">
            <span class="message-title">{{ message.title }}</span>
            <span class="message-time">{{ message.time }}</span>
          </div>
          <p class="message-text">{{ message.content }}</p>
        </div>
        
        <div class="message-actions">
          <el-button
            type="danger"
            size="small"
            text
            @click.stop="deleteMessage(message.id)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
      
      <EmptyState v-if="filteredMessages.length === 0" text="暂无消息" />
    </div>
    
    <div class="load-more" v-if="hasMore">
      <el-button @click="loadMore" :loading="loadingMore">加载更多</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Check, Delete, Bell, Reading, ChatDotRound, Trophy } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import EmptyState from '@/components/EmptyState/index.vue'

const router = useRouter()
const activeTab = ref('all')
const loadingMore = ref(false)
const hasMore = ref(false)

const messages = ref([
  {
    id: 1,
    type: 'audit',
    title: '方言审核通过',
    content: '您上传的"你好（北京）"方言手语视频已通过审核，感谢您的贡献！',
    time: '2小时前',
    read: false,
    link: '/dictionary/1'
  },
  {
    id: 2,
    type: 'learn',
    title: '复习提醒',
    content: '您有5个词汇需要复习，快来巩固一下吧！',
    time: '4小时前',
    read: false,
    link: '/tasks'
  },
  {
    id: 3,
    type: 'community',
    title: '有人点赞了您的动态',
    content: '手语达人小王赞了您的动态"今天学习了十个常用手语词汇"',
    time: '1天前',
    read: true,
    link: '/community'
  },
  {
    id: 4,
    type: 'community',
    title: '收到新评论',
    content: '用户"学习者"在您的动态下评论："太棒了，继续加油！"',
    time: '2天前',
    read: true,
    link: '/community'
  },
  {
    id: 5,
    type: 'learn',
    title: '学习成就解锁',
    content: '恭喜您解锁新成就"初学者"，继续努力！',
    time: '3天前',
    read: true,
    link: '/achievements'
  },
  {
    id: 6,
    type: 'audit',
    title: '审核意见反馈',
    content: '您上传的"家庭（东北）"视频未通过审核，建议：请重新拍摄正面角度。',
    time: '5天前',
    read: true,
    link: '/audit'
  },
  {
    id: 7,
    type: 'community',
    title: '新粉丝',
    content: '手语教师李老师关注了您',
    time: '1周前',
    read: true,
    link: '/profile'
  }
])

const unreadCount = computed(() => messages.value.filter(m => !m.read).length)

const filteredMessages = computed(() => {
  if (activeTab.value === 'all') return messages.value
  const typeMap = {
    audit: '审核通知',
    learn: '学习提醒',
    community: '社区互动'
  }
  return messages.value.filter(m => {
    const type = typeMap[activeTab.value]
    return m.type === activeTab.value || (m.title.includes(type) && m.title.includes('审核'))
  })
})

function getIcon(type) {
  const icons = {
    audit: Trophy,
    learn: Reading,
    community: ChatDotRound
  }
  return icons[type] || Bell
}

function getIconClass(type) {
  const classes = {
    audit: 'icon-audit',
    learn: 'icon-learn',
    community: 'icon-community'
  }
  return classes[type] || 'icon-default'
}

function handleTabChange() {
  console.log('切换标签:', activeTab.value)
}

function handleMessageClick(message) {
  message.read = true
  if (message.link) {
    router.push(message.link)
  }
}

function markAllRead() {
  messages.value.forEach(m => m.read = true)
  ElMessage.success('已全部标记为已读')
}

function deleteMessage(id) {
  ElMessageBox.confirm('确定删除这条消息吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    messages.value = messages.value.filter(m => m.id !== id)
    ElMessage.success('删除成功')
  }).catch(() => {})
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
.messages-page {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 130px);
  
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
  
  .message-tabs {
    margin-bottom: 20px;
    
    .el-radio-button {
      .el-badge {
        margin-left: 4px;
      }
    }
  }
  
  .message-list {
    .message-item {
      display: flex;
      align-items: flex-start;
      padding: 20px;
      background: #fff;
      border-radius: 12px;
      margin-bottom: 12px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        background: #f9fafb;
      }
      
      &.unread {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        
        .message-icon {
          background: #667eea;
          
          .el-icon {
            color: #fff;
          }
        }
        
        .message-title {
          font-weight: bold;
        }
      }
      
      .message-icon {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #f5f7fa;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        flex-shrink: 0;
        
        .el-icon {
          font-size: 22px;
          color: #666;
        }
        
        &.icon-audit {
          background: #fef0f0;
          .el-icon { color: #f56c6c; }
        }
        
        &.icon-learn {
          background: #f0f9ff;
          .el-icon { color: #409eff; }
        }
        
        &.icon-community {
          background: #f0fdf4;
          .el-icon { color: #67c23a; }
        }
      }
      
      .message-content {
        flex: 1;
        
        .message-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          
          .message-title {
            font-size: 15px;
            color: #333;
          }
          
          .message-time {
            font-size: 12px;
            color: #999;
          }
        }
        
        .message-text {
          font-size: 14px;
          color: #666;
          line-height: 1.5;
          margin: 0;
        }
      }
      
      .message-actions {
        margin-left: 12px;
        opacity: 0;
        transition: opacity 0.3s;
        
        .el-button {
          padding: 4px;
        }
      }
      
      &:hover .message-actions {
        opacity: 1;
      }
    }
  }
  
  .load-more {
    text-align: center;
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .messages-page {
    .message-list .message-item {
      .message-content .message-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
      }
    }
  }
}
</style>
