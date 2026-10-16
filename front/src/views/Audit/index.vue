<template>
  <div class="audit-page">
    <div class="page-header">
      <h1>审核状态</h1>
      <p class="subtitle">查看你的内容审核进度和结果</p>
    </div>

    <!-- Stats Overview -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon pending">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.pending }}</span>
          <span class="stat-label">待审核</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon approved">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.approved }}</span>
          <span class="stat-label">已通过</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon rejected">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.rejected }}</span>
          <span class="stat-label">已驳回</span>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-container">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane>
          <template #label>
            <span class="tab-label">
              <el-icon><Clock /></el-icon>
              待审核
              <el-badge v-if="stats.pending > 0" :value="stats.pending" />
            </span>
          </template>
          <span>待审核</span>
        </el-tab-pane>
        <el-tab-pane label="已通过" name="approved">
          <template #label>
            <span class="tab-label">
              <el-icon><CircleCheck /></el-icon>
              已通过
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="已驳回" name="rejected">
          <template #label>
            <span class="tab-label">
              <el-icon><CircleClose /></el-icon>
              已驳回
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Upload List -->
    <div class="upload-list">
      <div
        v-for="item in filteredUploads"
        :key="item.id"
        class="upload-item"
      >
        <div class="upload-preview">
          <video v-if="item.type === 'video'" :src="item.url" muted />
          <img v-else :src="item.url" alt="预览" />
          <div class="preview-overlay">
            <el-icon @click="previewItem(item)"><FullScreen /></el-icon>
          </div>
        </div>

        <div class="upload-info">
          <h3>{{ item.title }}</h3>
          <div class="upload-meta">
            <el-tag :type="getTypeTag(item.type)" size="small">
              {{ getTypeLabel(item.type) }}
            </el-tag>
            <span class="upload-time">{{ formatTime(item.createdAt) }}</span>
          </div>
          <p class="upload-desc">{{ item.description }}</p>
          <div class="upload-tags" v-if="item.tags?.length > 0">
            <el-tag
              v-for="tag in item.tags"
              :key="tag"
              size="small"
              type="info"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <div class="upload-status">
          <el-tag
            v-if="item.status === 'pending'"
            type="warning"
            size="large"
          >
            <el-icon><Clock /></el-icon>
            审核中
          </el-tag>
          <el-tag
            v-else-if="item.status === 'approved'"
            type="success"
            size="large"
          >
            <el-icon><CircleCheck /></el-icon>
            已通过
          </el-tag>
          <el-tag
            v-else
            type="danger"
            size="large"
          >
            <el-icon><CircleClose /></el-icon>
            已驳回
          </el-tag>

          <div v-if="item.status === 'pending'" class="status-progress">
            <el-progress
              :percentage="item.progress || 0"
              :show-text="false"
              :stroke-width="4"
            />
            <span>排队中...</span>
          </div>

          <div v-if="item.status === 'rejected' && item.rejectReason" class="reject-reason">
            <el-icon><Warning /></el-icon>
            <span>{{ item.rejectReason }}</span>
          </div>
        </div>

        <div class="upload-actions">
          <el-button size="small" @click="viewDetail(item)">
            查看详情
          </el-button>
          <el-button
            v-if="item.status === 'rejected'"
            type="primary"
            size="small"
            @click="resubmit(item)"
          >
            重新提交
          </el-button>
          <el-button
            v-if="item.status === 'approved'"
            type="success"
            size="small"
            @click="publish(item)"
          >
            发布
          </el-button>
          <el-dropdown trigger="click">
            <el-button size="small" text>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="editItem(item)">编辑</el-dropdown-item>
                <el-dropdown-item @click="deleteItem(item)" divided>删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <div v-if="filteredUploads.length === 0" class="empty-state">
        <el-icon><Files /></el-icon>
        <h3>暂无内容</h3>
        <p>{{ getEmptyMessage() }}</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalItems > pageSize" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="totalItems"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>

    <!-- Preview Dialog -->
    <el-dialog
      v-model="showPreview"
      :title="previewItemData?.title"
      width="800px"
    >
      <div class="preview-content">
        <video
          v-if="previewItemData?.type === 'video'"
          :src="previewItemData?.url"
          controls
        />
        <img v-else :src="previewItemData?.url" alt="预览" />
      </div>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="showDetail"
      :title="detailItem?.title"
      width="600px"
    >
      <div class="detail-content" v-if="detailItem">
        <div class="detail-preview">
          <video v-if="detailItem.type === 'video'" :src="detailItem.url" controls />
          <img v-else :src="detailItem.url" alt="预览" />
        </div>

        <div class="detail-info">
          <div class="info-item">
            <span class="label">状态</span>
            <el-tag
              :type="detailItem.status === 'approved' ? 'success' : detailItem.status === 'rejected' ? 'danger' : 'warning'"
            >
              {{ getStatusLabel(detailItem.status) }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="label">类型</span>
            <span class="value">{{ getTypeLabel(detailItem.type) }}</span>
          </div>
          <div class="info-item">
            <span class="label">提交时间</span>
            <span class="value">{{ formatFullTime(detailItem.createdAt) }}</span>
          </div>
          <div class="info-item">
            <span class="label">审核时间</span>
            <span class="value">{{ detailItem.reviewedAt ? formatFullTime(detailItem.reviewedAt) : '待审核' }}</span>
          </div>
          <div v-if="detailItem.rejectReason" class="info-item reject">
            <span class="label">驳回原因</span>
            <span class="value">{{ detailItem.rejectReason }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadApi } from '@/api'
import {
  Clock,
  CircleCheck,
  CircleClose,
  FullScreen,
  Warning,
  MoreFilled,
  Files
} from '@element-plus/icons-vue'

const activeTab = ref('pending')
const currentPage = ref(1)
const pageSize = ref(10)
const showPreview = ref(false)
const showDetail = ref(false)
const previewItemData = ref(null)
const detailItem = ref(null)

// Stats
const stats = ref({
  pending: 3,
  approved: 12,
  rejected: 2
})

// Uploads
const uploads = ref([
  {
    id: 1,
    title: '手语"谢谢"标准演示',
    type: 'video',
    url: '',
    description: '这是"谢谢"手语的标准化演示视频',
    tags: ['谢谢', '基础'],
    status: 'pending',
    progress: 30,
    createdAt: Date.now() - 3600000
  },
  {
    id: 2,
    title: '日常问候手语练习',
    type: 'video',
    url: '',
    description: '记录我的日常问候语练习过程',
    tags: ['问候', '练习'],
    status: 'pending',
    progress: 10,
    createdAt: Date.now() - 7200000
  },
  {
    id: 3,
    title: '数字手语1-10',
    type: 'video',
    url: '',
    description: '完整的数字1到10的手语表达',
    tags: ['数字', '入门'],
    status: 'pending',
    progress: 5,
    createdAt: Date.now() - 86400000
  },
  {
    id: 4,
    title: '"你好"手语正确示范',
    type: 'video',
    url: '',
    description: '标准的"你好"手语动作演示',
    tags: ['你好', '问候'],
    status: 'approved',
    reviewedAt: Date.now() - 172800000,
    createdAt: Date.now() - 259200000
  },
  {
    id: 5,
    title: '再见手势分解动作',
    type: 'video',
    url: '',
    description: '"再见"手势的分解动作教学',
    tags: ['再见', '动作'],
    status: 'approved',
    reviewedAt: Date.now() - 345600000,
    createdAt: Date.now() - 432000000
  },
  {
    id: 6,
    title: '对不起手势示范',
    type: 'video',
    url: '',
    description: '道歉用语"对不起"的标准手势',
    tags: ['对不起', '礼貌'],
    status: 'rejected',
    rejectReason: '视频画面模糊，建议重新录制',
    reviewedAt: Date.now() - 518400000,
    createdAt: Date.now() - 604800000
  },
  {
    id: 7,
    title: '早上好手语教程',
    type: 'video',
    url: '',
    description: '完整的"早上好"手语教程',
    tags: ['问候', '时间'],
    status: 'approved',
    reviewedAt: Date.now() - 86400000,
    createdAt: Date.now() - 172800000
  }
])

const filteredUploads = computed(() => {
  return uploads.value.filter(u => u.status === activeTab.value)
})

const totalItems = computed(() => filteredUploads.value.length)

// Methods
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

function getTypeLabel(type) {
  const labels = { video: '视频', image: '图片' }
  return labels[type] || type
}

function getTypeTag(type) {
  return type === 'video' ? 'primary' : 'success'
}

function getStatusLabel(status) {
  const labels = {
    pending: '审核中',
    approved: '已通过',
    rejected: '已驳回'
  }
  return labels[status] || status
}

function getEmptyMessage() {
  const messages = {
    pending: '暂无待审核内容',
    approved: '暂无已通过内容',
    rejected: '暂无驳回内容'
  }
  return messages[activeTab.value] || '暂无内容'
}

async function handleTabChange() {
  currentPage.value = 1
}

async function handlePageChange() {
  // Load more items
}

function previewItem(item) {
  previewItemData.value = item
  showPreview.value = true
}

function viewDetail(item) {
  detailItem.value = item
  showDetail.value = true
}

async function resubmit(item) {
  ElMessageBox.confirm('确定要重新提交吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    item.status = 'pending'
    item.progress = 0
    item.rejectReason = ''
    ElMessage.success('已重新提交')
  }).catch(() => {})
}

async function publish(item) {
  ElMessageBox.confirm('确定要发布到社区吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    ElMessage.success('已发布到社区')
  }).catch(() => {})
}

function editItem(item) {
  ElMessage.info('编辑功能开发中')
}

async function deleteItem(item) {
  await ElMessageBox.confirm('确定要删除这条内容吗？此操作不可恢复', '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = uploads.value.findIndex(u => u.id === item.id)
    if (index > -1) {
      uploads.value.splice(index, 1)
      stats.value[item.status]--
    }
    ElMessage.success('删除成功')
  }).catch(() => {})
}

onMounted(() => {
  // Load data
})
</script>

<style scoped>
.audit-page {
  max-width: 1000px;
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
  grid-template-columns: repeat(3, 1fr);
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

.stat-icon.pending {
  background: #fff3e0;
  color: #ff9800;
}

.stat-icon.approved {
  background: #e8f5e9;
  color: #4caf50;
}

.stat-icon.rejected {
  background: #ffebee;
  color: #f44336;
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

/* Upload List */
.upload-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 20px;
  transition: all 180ms ease;
}

.upload-item:hover {
  border-color: #0d0d0d;
}

.upload-preview {
  position: relative;
  width: 160px;
  height: 100px;
  background: #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.upload-preview video,
.upload-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
  opacity: 0;
  transition: opacity 180ms ease;
  cursor: pointer;
}

.upload-preview:hover .preview-overlay {
  opacity: 1;
}

.upload-info {
  flex: 1;
  min-width: 0;
}

.upload-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 8px;
}

.upload-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.upload-time {
  font-size: 12px;
  color: #8a8a8a;
}

.upload-desc {
  font-size: 13px;
  color: #8a8a8a;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.upload-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  min-width: 120px;
}

.status-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.status-progress span {
  font-size: 12px;
  color: #8a8a8a;
}

.reject-reason {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 8px 12px;
  background: #fef0f0;
  border-radius: 6px;
  font-size: 12px;
  color: #f56c6c;
}

.reject-reason .el-icon {
  flex-shrink: 0;
}

.upload-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 100px;
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
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* Preview Dialog */
.preview-content {
  background: #0d0d0d;
  border-radius: 10px;
  overflow: hidden;
}

.preview-content video,
.preview-content img {
  width: 100%;
  max-height: 500px;
  object-fit: contain;
}

/* Detail Content */
.detail-content {
  padding: 8px 0;
}

.detail-preview {
  width: 100%;
  height: 300px;
  background: #e8e8e8;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 24px;
}

.detail-preview video,
.detail-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.info-item .label {
  font-size: 14px;
  color: #8a8a8a;
  min-width: 80px;
}

.info-item .value {
  font-size: 14px;
  color: #0d0d0d;
}

.info-item.reject {
  flex-direction: column;
  align-items: flex-start;
  padding: 12px;
  background: #fef0f0;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .upload-item {
    flex-direction: column;
  }

  .upload-preview {
    width: 100%;
    height: 200px;
  }

  .upload-status,
  .upload-actions {
    flex-direction: row;
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
