<template>
  <div class="messages-page">
    <div class="page-header">
      <h1>消息中心</h1>
      <p class="subtitle">查看互动、收到的赞和系统通知</p>
    </div>

    <!-- Tabs -->
    <div class="tabs-container">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="互动" name="interaction">
          <template #label>
            <span class="tab-label">
              <el-icon><ChatDotRound /></el-icon>
              互动
              <el-badge v-if="unreadInteraction > 0" :value="unreadInteraction" :max="99" />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="收到赞" name="likes">
          <template #label>
            <span class="tab-label">
              <el-icon><Star /></el-icon>
              收到赞
              <el-badge v-if="unreadLikes > 0" :value="unreadLikes" :max="99" />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="系统通知" name="system">
          <template #label>
            <span class="tab-label">
              <el-icon><Bell /></el-icon>
              系统通知
              <el-badge v-if="unreadSystem > 0" :value="unreadSystem" :max="99" />
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>

      <div class="tab-actions">
        <el-button
          v-if="selectedMessages.length > 0"
          type="danger"
          size="small"
          @click="batchDelete"
        >
          <el-icon><Delete /></el-icon>
          删除已选
        </el-button>
        <el-button size="small" @click="markAllAsRead" :disabled="totalUnread === 0">
          <el-icon><Check /></el-icon>
          全部标为已读
        </el-button>
      </div>
    </div>

    <!-- Message List -->
    <div class="message-list">
      <div
        v-for="message in currentMessages"
        :key="message.id"
        class="message-item"
        :class="{ unread: !message.isRead }"
        @click="openMessage(message)"
      >
        <div class="message-checkbox" @click.stop>
          <el-checkbox
            v-model="message.selected"
            @change="updateSelected"
          />
        </div>

        <div class="message-avatar">
          <el-avatar
            :src="message.fromUser?.avatar"
            :size="48"
          >
            {{ message.fromUser?.name?.charAt(0) }}
          </el-avatar>
        </div>

        <div class="message-content">
          <div class="message-header">
            <span class="from-name">{{ message.fromUser?.name || '系统通知' }}</span>
            <span class="message-time">{{ formatTime(message.createdAt) }}</span>
          </div>
          <div class="message-body">
            <p>{{ message.content }}</p>
          </div>
          <div v-if="message.type === 'comment'" class="message-preview">
            <span class="preview-label">评论了你的动态：</span>
            <span class="preview-text">{{ message.targetContent }}</span>
          </div>
          <div v-if="message.type === 'like'" class="message-preview">
            <span class="preview-label">赞了你的动态：</span>
            <span class="preview-text">{{ message.targetContent }}</span>
          </div>
        </div>

        <div class="message-actions" @click.stop>
          <el-button
            v-if="!message.isRead"
            size="small"
            text
            @click="markAsRead(message)"
          >
            标为已读
          </el-button>
          <el-dropdown trigger="click">
            <el-button size="small" text>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="markAsRead(message)">
                  <el-icon><FolderChecked /></el-icon>
                  标为已读
                </el-dropdown-item>
                <el-dropdown-item @click="deleteMessage(message)" divided>
                  <el-icon><Delete /></el-icon>
                  删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <div v-if="currentMessages.length === 0" class="empty-state">
        <el-icon><ChatLineSquare /></el-icon>
        <h3>暂无消息</h3>
        <p>你还没有任何{{ getTabLabel }}消息</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container" v-if="totalMessages > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="totalMessages"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>

    <!-- Message Detail Dialog -->
    <el-dialog
      v-model="showDetail"
      :title="currentMessage?.fromUser?.name || '消息详情'"
      width="500px"
    >
      <div class="message-detail">
        <div class="detail-header">
          <el-avatar
            :src="currentMessage?.fromUser?.avatar"
            :size="56"
          >
            {{ currentMessage?.fromUser?.name?.charAt(0) }}
          </el-avatar>
          <div class="detail-info">
            <h3>{{ currentMessage?.fromUser?.name }}</h3>
            <span class="detail-time">{{ formatFullTime(currentMessage?.createdAt) }}</span>
          </div>
        </div>
        <div class="detail-body">
          <p>{{ currentMessage?.content }}</p>
        </div>
        <div v-if="currentMessage?.images?.length > 0" class="detail-images">
          <el-image
            v-for="(img, index) in currentMessage.images"
            :key="index"
            :src="img"
            :preview-src-list="currentMessage.images"
            fit="cover"
          />
        </div>
        <div v-if="currentMessage?.type !== 'system'" class="detail-actions">
          <el-button type="primary" @click="viewPost(currentMessage)">
            查看动态
          </el-button>
          <el-button @click="followUser(currentMessage)">
            <el-icon><Plus /></el-icon>
            关注
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import {
  ChatDotRound,
  Star,
  Bell,
  Delete,
  Check,
  MoreFilled,
  FolderChecked,
  ChatLineSquare,
  Plus
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// State
const activeTab = ref('interaction')
const currentPage = ref(1)
const pageSize = ref(20)
const showDetail = ref(false)
const currentMessage = ref(null)

// Data
const messages = ref({
  interaction: [],
  likes: [],
  system: []
})

// Unread counts
const unreadCounts = ref({
  interaction: 0,
  likes: 0,
  system: 0
})

const unreadInteraction = computed(() => unreadCounts.value.interaction)
const unreadLikes = computed(() => unreadCounts.value.likes)
const unreadSystem = computed(() => unreadCounts.value.system)
const totalUnread = computed(() => unreadInteraction.value + unreadLikes.value + unreadSystem.value)

// Selected
const selectedMessages = computed(() => {
  const allMessages = [
    ...messages.value.interaction,
    ...messages.value.likes,
    ...messages.value.system
  ]
  return allMessages.filter(m => m.selected)
})

// Current messages based on tab
const currentMessages = computed(() => {
  const list = messages.value[activeTab.value] || []
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return list.slice(start, end)
})

const totalMessages = computed(() => {
  return messages.value[activeTab.value]?.length || 0
})

function getTabLabel() {
  const labels = {
    interaction: '互动',
    likes: '收到赞',
    system: '系统'
  }
  return labels[activeTab.value]
}

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

async function loadMessages() {
  try {
    const typeMap = {
      interaction: 'comment',
      likes: 'like',
      system: 'system'
    }
    const res = await messageApi.getList({
      type: typeMap[activeTab.value],
      page: currentPage.value,
      limit: pageSize.value
    })

    const list = res.data?.list || res.data || []
    if (activeTab.value === 'interaction') {
      messages.value.interaction = list
    } else if (activeTab.value === 'likes') {
      messages.value.likes = list
    } else {
      messages.value.system = list
    }
  } catch (error) {
    loadMockMessages()
  }
}

function loadMockMessages() {
  messages.value = {
    interaction: [
      {
        id: 1,
        type: 'comment',
        isRead: false,
        selected: false,
        fromUser: { id: 2, name: '李明', avatar: '' },
        content: '这个手势做得很标准！学习一下',
        targetContent: '分享一个今天学会的手语动作',
        createdAt: Date.now() - 1800000,
        images: []
      },
      {
        id: 2,
        type: 'comment',
        isRead: false,
        selected: false,
        fromUser: { id: 3, name: '王芳', avatar: '' },
        content: '请问这个动作有什么要点吗？',
        targetContent: '手语学习第三天',
        createdAt: Date.now() - 7200000,
        images: []
      },
      {
        id: 3,
        type: 'comment',
        isRead: true,
        selected: false,
        fromUser: { id: 4, name: '张伟', avatar: '' },
        content: '坚持练习，一定能学会的！',
        targetContent: '每天进步一点点',
        createdAt: Date.now() - 86400000,
        images: []
      }
    ],
    likes: [
      {
        id: 4,
        type: 'like',
        isRead: false,
        selected: false,
        fromUser: { id: 5, name: '陈静', avatar: '' },
        content: '觉得你的学习笔记很有帮助',
        targetContent: '手语学习心得分享',
        createdAt: Date.now() - 3600000,
        images: []
      },
      {
        id: 5,
        type: 'like',
        isRead: true,
        selected: false,
        fromUser: { id: 6, name: '刘洋', avatar: '' },
        content: '动作很标准，给你点赞！',
        targetContent: '日常问候手语',
        createdAt: Date.now() - 172800000,
        images: []
      }
    ],
    system: [
      {
        id: 6,
        type: 'system',
        isRead: false,
        selected: false,
        fromUser: null,
        content: '恭喜你完成了今日学习任务，连续学习7天，获得"坚持"勋章！',
        targetContent: '',
        createdAt: Date.now() - 600000,
        images: []
      },
      {
        id: 7,
        type: 'system',
        isRead: true,
        selected: false,
        fromUser: null,
        content: '你的练习视频已通过审核，获得10积分奖励！',
        targetContent: '',
        createdAt: Date.now() - 259200000,
        images: []
      },
      {
        id: 8,
        type: 'system',
        isRead: true,
        selected: false,
        fromUser: null,
        content: '发现新内容：数字手语专题课程已上线，快去看看吧！',
        targetContent: '',
        createdAt: Date.now() - 432000000,
        images: []
      }
    ]
  }

  unreadCounts.value = {
    interaction: messages.value.interaction.filter(m => !m.isRead).length,
    likes: messages.value.likes.filter(m => !m.isRead).length,
    system: messages.value.system.filter(m => !m.isRead).length
  }
}

async function handleTabChange(tab) {
  currentPage.value = 1
  await loadMessages()
}

async function handlePageChange(page) {
  currentPage.value = page
  await loadMessages()
}

function openMessage(message) {
  currentMessage.value = message
  showDetail.value = true
  if (!message.isRead) {
    markAsRead(message)
  }
}

async function markAsRead(message) {
  message.isRead = true
  unreadCounts.value[activeTab.value] = Math.max(0, unreadCounts.value[activeTab.value] - 1)

  try {
    await messageApi.markAsRead(message.id)
  } catch (error) {
    // Silent fail
  }
}

async function markAllAsRead() {
  ElMessageBox.confirm('确定要将所有消息标为已读吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    const list = messages.value[activeTab.value]
    list.forEach(m => m.isRead = true)
    unreadCounts.value[activeTab.value] = 0

    try {
      await messageApi.markAllAsRead(activeTab.value)
      ElMessage.success('已全部标为已读')
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

function updateSelected() {
  // Trigger reactivity
}

async function deleteMessage(message) {
  ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const list = messages.value[activeTab.value]
    const index = list.findIndex(m => m.id === message.id)
    if (index > -1) {
      list.splice(index, 1)
    }
    if (!message.isRead) {
      unreadCounts.value[activeTab.value] = Math.max(0, unreadCounts.value[activeTab.value] - 1)
    }

    try {
      await messageApi.delete(message.id)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

async function batchDelete() {
  if (selectedMessages.value.length === 0) return

  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedMessages.value.length} 条消息吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const ids = selectedMessages.value.map(m => m.id)
    const list = messages.value[activeTab.value]
    const toDelete = list.filter(m => ids.includes(m.id))
    toDelete.forEach(m => {
      const index = list.findIndex(l => l.id === m.id)
      if (index > -1) list.splice(index, 1)
      if (!m.isRead) {
        unreadCounts.value[activeTab.value] = Math.max(0, unreadCounts.value[activeTab.value] - 1)
      }
    })

    try {
      await messageApi.batchDelete(ids)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

function viewPost(message) {
  if (message.postId) {
    router.push(`/community/post/${message.postId}`)
  }
  showDetail.value = false
}

async function followUser(message) {
  if (!message.fromUser) return

  try {
    await messageApi.follow(message.fromUser.id)
    ElMessage.success(`已关注 ${message.fromUser.name}`)
  } catch (error) {
    ElMessage.error('关注失败')
  }
}

onMounted(() => {
  loadMockMessages()
})
</script>

<style scoped>
.messages-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 48px 32px 80px;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
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

.tabs-container {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
  margin-bottom: 24px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e8e8e8;
}

.message-list {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  overflow: hidden;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e8e8;
  cursor: pointer;
  transition: background 180ms ease;
}

.message-item:last-child {
  border-bottom: none;
}

.message-item:hover {
  background: #fafaf8;
}

.message-item.unread {
  background: #f0f7ff;
}

.message-item.unread:hover {
  background: #e6f0ff;
}

.message-checkbox {
  padding-top: 8px;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.from-name {
  font-size: 15px;
  font-weight: 600;
  color: #0d0d0d;
}

.message-time {
  font-size: 12px;
  color: #8a8a8a;
}

.message-body {
  margin-bottom: 8px;
}

.message-body p {
  font-size: 14px;
  color: #0d0d0d;
  line-height: 1.6;
  margin: 0;
}

.message-preview {
  font-size: 13px;
  color: #8a8a8a;
  padding: 8px 12px;
  background: #fafaf8;
  border-radius: 6px;
}

.preview-label {
  color: #8a8a8a;
}

.preview-text {
  color: #0d0d0d;
}

.message-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.empty-state {
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
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.message-detail {
  padding: 8px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 4px;
}

.detail-time {
  font-size: 13px;
  color: #8a8a8a;
}

.detail-body {
  margin-bottom: 24px;
}

.detail-body p {
  font-size: 15px;
  color: #0d0d0d;
  line-height: 1.8;
  margin: 0;
}

.detail-images {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 24px;
}

.detail-images .el-image {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
}

.detail-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
