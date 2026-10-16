<template>
  <div class="upload-page">
    <div class="upload-container">
      <div class="page-header">
        <h2>上传方言手语</h2>
        <p>分享您所在地区的手语表达方式</p>
      </div>
      
      <el-form ref="formRef" :model="form" :rules="rules" class="upload-form">
        <el-form-item label="选择标准词条" prop="wordId">
          <el-select
            v-model="form.wordId"
            filterable
            placeholder="搜索并选择词条"
            @change="handleWordChange"
          >
            <el-option
              v-for="word in wordOptions"
              :key="word.id"
              :label="word.word"
              :value="word.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="选择地区" prop="region">
          <el-cascader
            v-model="form.region"
            :options="regionOptions"
            placeholder="选择省/市"
          />
        </el-form-item>
        
        <el-form-item label="视频上传" prop="videoFile">
          <div class="upload-area" @click="triggerUpload">
            <input
              type="file"
              ref="fileInput"
              accept="video/*"
              @change="handleFileChange"
              style="display: none"
            />
            
            <div v-if="!form.videoFile" class="upload-placeholder">
              <el-icon><UploadFilled /></el-icon>
              <p>点击上传视频</p>
              <span>支持 MP4、MOV 格式，时长不超过 30 秒</span>
            </div>
            
            <div v-else class="video-preview">
              <video :src="videoPreviewUrl" controls></video>
              <div class="preview-actions">
                <el-button size="small" @click.stop="triggerUpload">重新上传</el-button>
                <el-button size="small" type="danger" @click.stop="removeVideo">删除</el-button>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="补充说明">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="添加动作要点、注意事项等..."
          />
        </el-form-item>
        
        <div class="form-actions">
          <el-button @click="$router.back()">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            提交审核
          </el-button>
        </div>
      </el-form>
      
      <div class="upload-history">
        <h3>我的上传记录</h3>
        
        <el-tabs v-model="activeTab">
          <el-tab-pane label="审核中" name="pending">
            <div class="history-list">
              <div v-for="item in pendingList" :key="item.id" class="history-item">
                <div class="item-info">
                  <span class="word-name">{{ item.word }}</span>
                  <span class="region">{{ item.region }}</span>
                </div>
                <el-tag type="warning" size="small">审核中</el-tag>
              </div>
              <EmptyState v-if="pendingList.length === 0" text="暂无审核中的记录" />
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="已通过" name="approved">
            <div class="history-list">
              <div v-for="item in approvedList" :key="item.id" class="history-item">
                <div class="item-info">
                  <span class="word-name">{{ item.word }}</span>
                  <span class="region">{{ item.region }}</span>
                </div>
                <el-tag type="success" size="small">已通过</el-tag>
              </div>
              <EmptyState v-if="approvedList.length === 0" text="暂无已通过的记录" />
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="已驳回" name="rejected">
            <div class="history-list">
              <div v-for="item in rejectedList" :key="item.id" class="history-item">
                <div class="item-info">
                  <span class="word-name">{{ item.word }}</span>
                  <span class="region">{{ item.region }}</span>
                  <span class="reason">驳回原因：{{ item.reason }}</span>
                </div>
                <div class="item-actions">
                  <el-tag type="danger" size="small">已驳回</el-tag>
                  <el-button size="small" @click="editItem(item)">重新编辑</el-button>
                </div>
              </div>
              <EmptyState v-if="rejectedList.length === 0" text="暂无已驳回的记录" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { wordApi, uploadApi } from '@/api'
import EmptyState from '@/components/EmptyState/index.vue'

const formRef = ref(null)
const fileInput = ref(null)
const submitting = ref(false)
const activeTab = ref('pending')

const form = reactive({
  wordId: '',
  region: [],
  videoFile: null,
  description: ''
})

const videoPreviewUrl = ref('')
const wordOptions = ref([])

const pendingList = ref([
  { id: 1, word: '你好', region: '北京', reason: '', status: 'pending' }
])
const approvedList = ref([
  { id: 2, word: '谢谢', region: '上海', reason: '', status: 'approved' }
])
const rejectedList = ref([
  { id: 3, word: '再见', region: '四川', reason: '视频角度不正确', status: 'rejected' }
])

const regionOptions = [
  { value: '华北', label: '华北', children: [
    { value: '北京', label: '北京' },
    { value: '天津', label: '天津' }
  ]},
  { value: '华东', label: '华东', children: [
    { value: '上海', label: '上海' },
    { value: '江苏', label: '江苏' }
  ]},
  { value: '华南', label: '华南', children: [
    { value: '广东', label: '广东' },
    { value: '广西', label: '广西' }
  ]},
  { value: '西南', label: '西南', children: [
    { value: '四川', label: '四川' },
    { value: '重庆', label: '重庆' }
  ]},
  { value: '东北', label: '东北', children: [
    { value: '辽宁', label: '辽宁' },
    { value: '吉林', label: '吉林' }
  ]}
]

const rules = {
  wordId: [{ required: true, message: '请选择词条', trigger: 'change' }],
  region: [{ required: true, message: '请选择地区', trigger: 'change' }],
  videoFile: [{ required: true, message: '请上传视频', trigger: 'change' }]
}

async function fetchWords() {
  try {
    const res = await wordApi.getWords()
    wordOptions.value = res.data
  } catch (e) {
    console.error('获取词条列表失败', e)
  }
}

function handleWordChange() {
  console.log('选择词条:', form.wordId)
}

function triggerUpload() {
  fileInput.value.click()
}

function handleFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.warning('视频大小不能超过 50MB')
    return
  }
  
  form.videoFile = file
  videoPreviewUrl.value = URL.createObjectURL(file)
}

function removeVideo() {
  form.videoFile = null
  videoPreviewUrl.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('wordId', form.wordId)
    formData.append('region', form.region.join('/'))
    formData.append('video', form.videoFile)
    formData.append('description', form.description)
    
    await uploadApi.uploadDialect(formData)
    ElMessage.success('提交成功，等待审核')
    
    form.wordId = ''
    form.region = []
    form.videoFile = null
    form.description = ''
    removeVideo()
  } catch (e) {
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

function editItem(item) {
  ElMessage.info('重新编辑功能开发中')
}

fetchWords()
</script>

<style scoped lang="scss">
.upload-page {
  min-height: calc(100vh - 130px);
  padding: 20px;
  
  .upload-container {
    max-width: 800px;
    margin: 0 auto;
    
    .page-header {
      text-align: center;
      margin-bottom: 30px;
      
      h2 {
        font-size: 24px;
        color: #333;
        margin-bottom: 8px;
      }
      
      p {
        color: #666;
        font-size: 14px;
      }
    }
    
    .upload-form {
      background: #fff;
      border-radius: 12px;
      padding: 30px;
      margin-bottom: 30px;
      
      .upload-area {
        border: 2px dashed #dcdfe6;
        border-radius: 8px;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: border-color 0.3s;
        
        &:hover {
          border-color: #667eea;
        }
        
        .upload-placeholder {
          text-align: center;
          color: #999;
          
          .el-icon {
            font-size: 48px;
            margin-bottom: 12px;
          }
          
          p {
            font-size: 14px;
            color: #333;
            margin-bottom: 4px;
          }
          
          span {
            font-size: 12px;
          }
        }
        
        .video-preview {
          width: 100%;
          padding: 16px;
          
          video {
            width: 100%;
            max-height: 300px;
            border-radius: 8px;
          }
          
          .preview-actions {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 12px;
          }
        }
      }
      
      .form-actions {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-top: 24px;
      }
    }
    
    .upload-history {
      background: #fff;
      border-radius: 12px;
      padding: 30px;
      
      h3 {
        font-size: 18px;
        color: #333;
        margin-bottom: 20px;
      }
      
      .history-list {
        min-height: 200px;
        
        .history-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid #f0f0f0;
          
          &:last-child {
            border-bottom: none;
          }
          
          .item-info {
            display: flex;
            flex-direction: column;
            gap: 4px;
            
            .word-name {
              font-weight: bold;
              color: #333;
            }
            
            .region {
              font-size: 12px;
              color: #666;
            }
            
            .reason {
              font-size: 12px;
              color: #f56c6c;
            }
          }
          
          .item-actions {
            display: flex;
            align-items: center;
            gap: 12px;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .upload-page {
    .upload-container {
      .upload-form {
        padding: 20px;
      }
    }
  }
}
</style>
