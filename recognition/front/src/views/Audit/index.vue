<template>
  <div class="audit-page">
    <div class="page-header">
      <h2>内容审核状态</h2>
      <p>查看您上传的方言手语审核进度</p>
    </div>
    
    <div class="audit-stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.pending }}</div>
        <div class="stat-label">待审核</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.approved }}</div>
        <div class="stat-label">已通过</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.rejected }}</div>
        <div class="stat-label">已驳回</div>
      </div>
    </div>
    
    <div class="filter-tabs">
      <el-radio-group v-model="activeFilter" @change="handleFilterChange">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="pending">待审核</el-radio-button>
        <el-radio-button value="approved">已通过</el-radio-button>
        <el-radio-button value="rejected">已驳回</el-radio-button>
      </el-radio-group>
    </div>
    
    <div class="audit-list">
      <div v-for="item in filteredList" :key="item.id" class="audit-item">
        <div class="item-content">
          <div class="item-info">
            <span class="word-name">{{ item.word }}</span>
            <span class="region">{{ item.region }}</span>
          </div>
          <div class="item-preview">
            <video :src="item.videoUrl" v-if="item.videoUrl"></video>
            <div class="preview-placeholder" v-else>
              <el-icon><VideoPlay /></el-icon>
            </div>
          </div>
          <div class="item-meta">
            <span class="submit-time">提交于 {{ item.submitTime }}</span>
            <span class="video-duration" v-if="item.duration">{{ item.duration }}</span>
          </div>
        </div>
        
        <div class="item-status">
          <el-tag :type="getStatusType(item.status)" size="small">
            {{ getStatusText(item.status) }}
          </el-tag>
          
          <div class="status-actions">
            <el-button
              v-if="item.status === 'pending'"
              type="primary"
              size="small"
              text
              disabled
            >
              审核中...
            </el-button>
            
            <el-button
              v-if="item.status === 'rejected'"
              type="primary"
              size="small"
              @click="editItem(item)"
            >
              重新编辑
            </el-button>
            
            <el-button
              v-if="item.status === 'approved'"
              type="success"
              size="small"
              text
            >
              查看
            </el-button>
          </div>
        </div>
        
        <div class="rejection-reason" v-if="item.status === 'rejected'">
          <el-icon><Warning /></el-icon>
          <div class="reason-content">
            <span class="reason-label">驳回原因：</span>
            <span class="reason-text">{{ item.rejectionReason }}</span>
          </div>
        </div>
      </div>
      
      <EmptyState v-if="filteredList.length === 0" :text="emptyText" />
    </div>
    
    <el-dialog v-model="editDialogVisible" title="重新编辑" width="600px">
      <div class="edit-form">
        <el-form :model="editForm" label-width="100px">
          <el-form-item label="选择词条">
            <el-select v-model="editForm.wordId" filterable>
              <el-option
                v-for="word in wordOptions"
                :key="word.id"
                :label="word.word"
                :value="word.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="选择地区">
            <el-cascader v-model="editForm.region" :options="regionOptions" />
          </el-form-item>
          <el-form-item label="重新上传视频">
            <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              accept="video/*"
            >
              <el-button>选择视频</el-button>
            </el-upload>
          </el-form-item>
          <el-form-item label="补充说明">
            <el-input v-model="editForm.description" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="resubmit" :loading="submitting">重新提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { VideoPicture, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import EmptyState from '@/components/EmptyState/index.vue'

const activeFilter = ref('all')
const editDialogVisible = ref(false)
const submitting = ref(false)

const stats = ref({
  pending: 2,
  approved: 5,
  rejected: 1
})

const auditList = ref([
  {
    id: 1,
    word: '你好',
    wordId: 1,
    region: '北京',
    videoUrl: '',
    duration: '15秒',
    status: 'approved',
    submitTime: '3天前',
    rejectionReason: ''
  },
  {
    id: 2,
    word: '谢谢',
    wordId: 2,
    region: '上海',
    videoUrl: '',
    duration: '12秒',
    status: 'pending',
    submitTime: '1天前',
    rejectionReason: ''
  },
  {
    id: 3,
    word: '再见',
    wordId: 3,
    region: '四川',
    videoUrl: '',
    duration: '18秒',
    status: 'pending',
    submitTime: '2天前',
    rejectionReason: ''
  },
  {
    id: 4,
    word: '家庭',
    wordId: 6,
    region: '东北',
    videoUrl: '',
    duration: '20秒',
    status: 'rejected',
    submitTime: '5天前',
    rejectionReason: '视频角度不正，建议正面或侧面拍摄'
  }
])

const wordOptions = ref([
  { id: 1, word: '你好' },
  { id: 2, word: '谢谢' },
  { id: 3, word: '再见' },
  { id: 6, word: '家庭' }
])

const regionOptions = [
  { value: '华北', label: '华北', children: [{ value: '北京', label: '北京' }, { value: '天津', label: '天津' }] },
  { value: '华东', label: '华东', children: [{ value: '上海', label: '上海' }] },
  { value: '西南', label: '西南', children: [{ value: '四川', label: '四川' }, { value: '重庆', label: '重庆' }] }
]

const editForm = ref({
  wordId: '',
  region: [],
  videoFile: null,
  description: ''
})

const filteredList = computed(() => {
  if (activeFilter.value === 'all') return auditList.value
  return auditList.value.filter(item => item.status === activeFilter.value)
})

const emptyText = computed(() => {
  const texts = {
    all: '暂无上传记录',
    pending: '暂无待审核的记录',
    approved: '暂无已通过的记录',
    rejected: '暂无已驳回的记录'
  }
  return texts[activeFilter.value]
})

function getStatusType(status) {
  const types = { approved: 'success', pending: 'warning', rejected: 'danger' }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = { approved: '已通过', pending: '审核中', rejected: '已驳回' }
  return texts[status] || '未知'
}

function handleFilterChange() {
  console.log('筛选:', activeFilter.value)
}

function handleFileChange(file) {
  editForm.value.videoFile = file
}

function editItem(item) {
  editForm.value = {
    wordId: item.wordId,
    region: [item.region],
    videoFile: null,
    description: ''
  }
  editDialogVisible.value = true
}

async function resubmit() {
  if (!editForm.value.wordId || !editForm.value.region.length) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  submitting.value = true
  await new Promise(r => setTimeout(r, 1000))
  submitting.value = false
  
  const item = auditList.value.find(i => i.id === editForm.value.wordId)
  if (item) {
    item.status = 'pending'
  }
  
  editDialogVisible.value = false
  ElMessage.success('重新提交成功')
}
</script>

<style scoped lang="scss">
.audit-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 130px);
  
  .page-header {
    margin-bottom: 24px;
    
    h2 {
      font-size: 24px;
      color: #333;
      margin-bottom: 4px;
    }
    
    p {
      color: #999;
      font-size: 14px;
      margin: 0;
    }
  }
  
  .audit-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 24px;
    
    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      
      .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #667eea;
      }
      
      .stat-label {
        font-size: 14px;
        color: #999;
      }
    }
  }
  
  .filter-tabs {
    margin-bottom: 20px;
  }
  
  .audit-list {
    .audit-item {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 16px;
      
      .item-content {
        margin-bottom: 16px;
        
        .item-info {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
          
          .word-name {
            font-size: 18px;
            font-weight: bold;
            color: #333;
          }
          
          .region {
            font-size: 12px;
            color: #666;
            padding: 4px 8px;
            background: #f0f9ff;
            border-radius: 4px;
          }
        }
        
        .item-preview {
          margin-bottom: 12px;
          
          video {
            width: 100%;
            max-height: 200px;
            border-radius: 8px;
            background: #000;
          }
          
          .preview-placeholder {
            height: 150px;
            background: #f5f7fa;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            
            .el-icon {
              font-size: 48px;
              color: #dcdfe6;
            }
          }
        }
        
        .item-meta {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #999;
        }
      }
      
      .item-status {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 16px;
        border-top: 1px solid #f0f0f0;
        
        .status-actions {
          display: flex;
          gap: 8px;
        }
      }
      
      .rejection-reason {
        margin-top: 16px;
        padding: 12px;
        background: #fef0f0;
        border-radius: 8px;
        display: flex;
        gap: 12px;
        align-items: flex-start;
        
        .el-icon {
          color: #f56c6c;
          font-size: 20px;
          flex-shrink: 0;
        }
        
        .reason-content {
          .reason-label {
            color: #f56c6c;
            font-size: 13px;
          }
          
          .reason-text {
            color: #666;
            font-size: 14px;
          }
        }
      }
    }
  }
  
  .edit-form {
    .el-form-item {
      margin-bottom: 20px;
    }
  }
}

@media (max-width: 768px) {
  .audit-page .audit-stats {
    grid-template-columns: repeat(3, 1fr);
    
    .stat-card {
      padding: 12px;
      
      .stat-value {
        font-size: 24px;
      }
    }
  }
}
</style>
