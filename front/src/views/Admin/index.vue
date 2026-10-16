<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>管理后台</h1>
      <p class="subtitle">系统管理，内容审核，用户管理</p>
    </div>

    <!-- Stats Overview -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #e3f2fd">
          <el-icon color="#2196f3"><User /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalUsers }}</span>
          <span class="stat-label">用户总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #e8f5e9">
          <el-icon color="#4caf50"><Collection /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalWords }}</span>
          <span class="stat-label">词汇总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fff3e0">
          <el-icon color="#ff9800"><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.pendingReview }}</span>
          <span class="stat-label">待审核</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fce4ec">
          <el-icon color="#e91e63"><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.approved }}</span>
          <span class="stat-label">已通过</span>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="用户管理" name="users">
          <template #label>
            <span class="tab-label">
              <el-icon><User /></el-icon>
              用户管理
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="内容管理" name="content">
          <template #label>
            <span class="tab-label">
              <el-icon><Document /></el-icon>
              内容管理
              <el-badge v-if="stats.pendingReview > 0" :value="stats.pendingReview" />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="词汇管理" name="words">
          <template #label>
            <span class="tab-label">
              <el-icon><Collection /></el-icon>
              词汇管理
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Users Tab -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <div class="toolbar">
        <el-input
          v-model="userSearch"
          placeholder="搜索用户名、邮箱"
          clearable
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="userFilter" placeholder="筛选用户" clearable>
          <el-option label="全部" value="all" />
          <el-option label="普通用户" value="user" />
          <el-option label="VIP用户" value="vip" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-button type="primary" @click="addUser">
          <el-icon><Plus /></el-icon>
          添加用户
        </el-button>
      </div>

      <el-table :data="filteredUsers" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="用户" min-width="200">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :src="row.avatar" :size="40">
                {{ row.name?.charAt(0) }}
              </el-avatar>
              <div class="user-info">
                <span class="user-name">{{ row.name }}</span>
                <span class="user-email">{{ row.email }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)" size="small">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级" width="80" />
        <el-table-column prop="points" label="积分" width="100" />
        <el-table-column prop="createdAt" label="注册时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click="editUser(row)">编辑</el-button>
            <el-dropdown trigger="click">
              <el-button size="small" text>
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="toggleUserRole(row)">
                    设为{{ row.role === 'admin' ? '普通用户' : '管理员' }}
                  </el-dropdown-item>
                  <el-dropdown-item @click="toggleUserStatus(row)">
                    {{ row.status === 'active' ? '禁用账号' : '启用账号' }}
                  </el-dropdown-item>
                  <el-dropdown-item @click="resetUserPassword(row)" divided>重置密码</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Content Tab -->
    <div v-if="activeTab === 'content'" class="tab-content">
      <div class="toolbar">
        <el-select v-model="contentFilter" placeholder="筛选内容" clearable>
          <el-option label="全部" value="all" />
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-button type="primary" @click="batchApprove" :disabled="selectedContents.length === 0">
          <el-icon><Check /></el-icon>
          批量通过
        </el-button>
      </div>

      <el-table
        :data="filteredContents"
        stripe
        @selection-change="handleSelectionChange"
        style="width: 100%"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="内容" min-width="300">
          <template #default="{ row }">
            <div class="content-cell">
              <div class="content-preview">
                <video v-if="row.type === 'video'" :src="row.url" muted />
                <img v-else :src="row.url" alt="预览" />
              </div>
              <div class="content-info">
                <span class="content-title">{{ row.title }}</span>
                <span class="content-type">
                  <el-tag size="small" :type="row.type === 'video' ? 'primary' : 'success'">
                    {{ row.type === 'video' ? '视频' : '图片' }}
                  </el-tag>
                </span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="作者" width="150">
          <template #default="{ row }">
            <span>{{ row.author }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getContentStatusType(row.status)" size="small">
              {{ getContentStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="提交时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              @click="approveContent(row)"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="danger"
              size="small"
              @click="rejectContent(row)"
            >
              驳回
            </el-button>
            <el-button
              v-if="row.status !== 'pending'"
              size="small"
              @click="viewContent(row)"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Words Tab -->
    <div v-if="activeTab === 'words'" class="tab-content">
      <div class="toolbar">
        <el-input
          v-model="wordSearch"
          placeholder="搜索词汇"
          clearable
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="wordCategoryFilter" placeholder="选择分类" clearable>
          <el-option label="日常用语" value="daily" />
          <el-option label="数字" value="numbers" />
          <el-option label="问候" value="greetings" />
          <el-option label="情感表达" value="emotions" />
        </el-select>
        <el-button type="primary" @click="addWord">
          <el-icon><Plus /></el-icon>
          添加词汇
        </el-button>
      </div>

      <el-table :data="filteredWords" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="词汇" min-width="150">
          <template #default="{ row }">
            <span class="word-title">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="100">
          <template #default="{ row }">
            <el-tag :type="getDifficultyType(row.difficulty)" size="small">
              {{ getDifficultyLabel(row.difficulty) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="learnCount" label="学习次数" width="100" />
        <el-table-column prop="createdAt" label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click="editWord(row)">编辑</el-button>
            <el-button size="small" text @click="viewWordDetail(row)">详情</el-button>
            <el-button size="small" text type="danger" @click="deleteWord(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Reject Dialog -->
    <el-dialog v-model="showRejectDialog" title="驳回原因" width="400px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="3"
        placeholder="请输入驳回原因"
      />
      <template #footer>
        <el-button @click="showRejectDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>

    <!-- User Edit Dialog -->
    <el-dialog v-model="showUserDialog" :title="editingUser?.id ? '编辑用户' : '添加用户'" width="500px">
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.name" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role">
            <el-option label="普通用户" value="user" />
            <el-option label="VIP用户" value="vip" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级">
          <el-input-number v-model="userForm.level" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="积分">
          <el-input-number v-model="userForm.points" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUserDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api'
import {
  User,
  Collection,
  Clock,
  CircleCheck,
  Document,
  Search,
  Plus,
  MoreFilled,
  Check
} from '@element-plus/icons-vue'

const activeTab = ref('users')

// Stats
const stats = ref({
  totalUsers: 1256,
  totalWords: 458,
  pendingReview: 8,
  approved: 342
})

// Users
const users = ref([])
const userSearch = ref('')
const userFilter = ref('all')
const showUserDialog = ref(false)
const editingUser = ref(null)
const userForm = ref({
  name: '',
  email: '',
  role: 'user',
  level: 1,
  points: 0
})

const filteredUsers = computed(() => {
  let result = users.value

  if (userSearch.value) {
    const keyword = userSearch.value.toLowerCase()
    result = result.filter(u =>
      u.name.toLowerCase().includes(keyword) ||
      u.email.toLowerCase().includes(keyword)
    )
  }

  if (userFilter.value !== 'all') {
    result = result.filter(u => u.role === userFilter.value)
  }

  return result
})

// Content
const contents = ref([])
const contentFilter = ref('pending')
const selectedContents = ref([])
const showRejectDialog = ref(false)
const currentRejectContent = ref(null)
const rejectReason = ref('')

const filteredContents = computed(() => {
  if (contentFilter.value === 'all') return contents.value
  return contents.value.filter(c => c.status === contentFilter.value)
})

// Words
const words = ref([])
const wordSearch = ref('')
const wordCategoryFilter = ref('')

const filteredWords = computed(() => {
  let result = words.value

  if (wordSearch.value) {
    result = result.filter(w =>
      w.title.toLowerCase().includes(wordSearch.value.toLowerCase())
    )
  }

  if (wordCategoryFilter.value) {
    result = result.filter(w => w.category === wordCategoryFilter.value)
  }

  return result
})

// Methods
function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function getRoleType(role) {
  const types = { admin: 'danger', vip: 'warning', user: '' }
  return types[role] || ''
}

function getRoleLabel(role) {
  const labels = { admin: '管理员', vip: 'VIP', user: '普通用户' }
  return labels[role] || role
}

function getContentStatusType(status) {
  const types = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return types[status] || ''
}

function getContentStatusLabel(status) {
  const labels = { pending: '待审核', approved: '已通过', rejected: '已驳回' }
  return labels[status] || status
}

function getDifficultyType(difficulty) {
  const types = {
    beginner: 'success',
    basic: 'primary',
    intermediate: 'warning',
    advanced: 'danger'
  }
  return types[difficulty] || ''
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

function loadMockData() {
  users.value = [
    { id: 1, name: '张三', email: 'zhangsan@example.com', avatar: '', role: 'user', level: 5, points: 1200, status: 'active', createdAt: '2026-01-15' },
    { id: 2, name: '李四', email: 'lisi@example.com', avatar: '', role: 'vip', level: 8, points: 3500, status: 'active', createdAt: '2026-02-20' },
    { id: 3, name: '王五', email: 'wangwu@example.com', avatar: '', role: 'admin', level: 10, points: 5000, status: 'active', createdAt: '2025-12-01' },
    { id: 4, name: '赵六', email: 'zhaoliu@example.com', avatar: '', role: 'user', level: 3, points: 800, status: 'disabled', createdAt: '2026-03-10' }
  ]

  contents.value = [
    { id: 1, title: '手语"谢谢"演示', type: 'video', url: '', status: 'pending', author: '张三', createdAt: '2026-04-23' },
    { id: 2, title: '你好手势教程', type: 'video', url: '', status: 'pending', author: '李四', createdAt: '2026-04-22' },
    { id: 3, title: '再见手语练习', type: 'video', url: '', status: 'approved', author: '王五', createdAt: '2026-04-20' },
    { id: 4, title: '对不起手语', type: 'video', url: '', status: 'rejected', author: '赵六', createdAt: '2026-04-18' }
  ]

  words.value = [
    { id: 1, title: '你好', category: '问候', difficulty: 'beginner', learnCount: 156, createdAt: '2026-01-01' },
    { id: 2, title: '谢谢', category: '礼貌', difficulty: 'beginner', learnCount: 142, createdAt: '2026-01-01' },
    { id: 3, title: '再见', category: '日常', difficulty: 'beginner', learnCount: 128, createdAt: '2026-01-02' },
    { id: 4, title: '对不起', category: '礼貌', difficulty: 'basic', learnCount: 95, createdAt: '2026-01-03' },
    { id: 5, title: '请', category: '礼貌', difficulty: 'basic', learnCount: 87, createdAt: '2026-01-04' }
  ]
}

// User actions
function addUser() {
  editingUser.value = null
  userForm.value = { name: '', email: '', role: 'user', level: 1, points: 0 }
  showUserDialog.value = true
}

function editUser(user) {
  editingUser.value = user
  userForm.value = { ...user }
  showUserDialog.value = true
}

async function saveUser() {
  if (editingUser.value) {
    Object.assign(editingUser.value, userForm.value)
    ElMessage.success('用户更新成功')
  } else {
    users.value.push({
      id: Date.now(),
      ...userForm.value,
      avatar: '',
      status: 'active',
      createdAt: new Date().toISOString().split('T')[0]
    })
    ElMessage.success('用户添加成功')
  }
  showUserDialog.value = false
}

async function toggleUserRole(user) {
  const newRole = user.role === 'admin' ? 'user' : 'admin'
  await ElMessageBox.confirm(`确定要将 ${user.name} 设为${newRole === 'admin' ? '管理员' : '普通用户'}吗？`, '提示')
  user.role = newRole
  ElMessage.success('角色更新成功')
}

async function toggleUserStatus(user) {
  const newStatus = user.status === 'active' ? 'disabled' : 'active'
  await ElMessageBox.confirm(`确定要${newStatus === 'disabled' ? '禁用' : '启用'} ${user.name} 吗？`, '提示')
  user.status = newStatus
  ElMessage.success('状态更新成功')
}

async function resetUserPassword(user) {
  await ElMessageBox.confirm(`确定要重置 ${user.name} 的密码吗？`, '提示')
  ElMessage.success('密码已重置为默认密码')
}

// Content actions
function handleSelectionChange(selection) {
  selectedContents.value = selection
}

async function approveContent(content) {
  await ElMessageBox.confirm(`确定要通过 "${content.title}" 吗？`, '提示')
  content.status = 'approved'
  stats.value.approved++
  stats.value.pendingReview--
  ElMessage.success('已通过')
}

function rejectContent(content) {
  currentRejectContent.value = content
  rejectReason.value = ''
  showRejectDialog.value = true
}

async function confirmReject() {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请输入驳回原因')
    return
  }
  currentRejectContent.value.status = 'rejected'
  currentRejectContent.value.rejectReason = rejectReason.value
  stats.value.pendingReview--
  showRejectDialog.value = false
  ElMessage.success('已驳回')
}

async function batchApprove() {
  await ElMessageBox.confirm(`确定要通过选中的 ${selectedContents.value.length} 条内容吗？`, '提示')
  selectedContents.value.forEach(c => {
    c.status = 'approved'
    stats.value.approved++
    stats.value.pendingReview--
  })
  selectedContents.value = []
  ElMessage.success('批量通过成功')
}

function viewContent(content) {
  ElMessage.info('查看内容详情')
}

// Word actions
function addWord() {
  ElMessage.info('添加词汇功能')
}

function editWord(word) {
  ElMessage.info(`编辑词汇: ${word.title}`)
}

function viewWordDetail(word) {
  ElMessage.info(`查看词汇详情: ${word.title}`)
}

async function deleteWord(word) {
  await ElMessageBox.confirm(`确定要删除词汇 "${word.title}" 吗？`, '警告', { type: 'warning' })
  const index = words.value.findIndex(w => w.id === word.id)
  if (index > -1) {
    words.value.splice(index, 1)
  }
  ElMessage.success('删除成功')
}

onMounted(() => {
  loadMockData()
})
</script>

<style scoped>
.admin-page {
  max-width: 1400px;
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #0d0d0d;
}

.stat-label {
  font-size: 13px;
  color: #8a8a8a;
}

/* Tabs */
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

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

/* User Cell */
.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  color: #0d0d0d;
}

.user-email {
  font-size: 12px;
  color: #8a8a8a;
}

/* Content Cell */
.content-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.content-preview {
  width: 80px;
  height: 50px;
  background: #e8e8e8;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.content-preview video,
.content-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.content-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.content-title {
  font-weight: 500;
  color: #0d0d0d;
}

.word-title {
  font-weight: 600;
  color: #0d0d0d;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .toolbar {
    flex-wrap: wrap;
  }

  .search-input {
    width: 100%;
  }
}
</style>
