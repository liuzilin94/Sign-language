<template>
  <div class="upload-page">
    <div class="upload-container">
      <div class="page-header">
        <h2>上传方言视频</h2>
        <p>分享你所在地区的手语表达方式</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="upload-form">
        <el-form-item label="选择词汇" prop="wordId">
          <el-select
            v-model="form.wordId"
            filterable
            placeholder="请选择词汇"
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
            placeholder="请选择地区"
          />
        </el-form-item>

        <el-form-item label="上传视频" prop="videoFile">
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
              <span>支持 MP4/MOV 格式，单个文件不超过 50MB</span>
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

        <el-form-item label="视频说明">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请简要说明这个手语动作的特点..."
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
        <h3>上传历史</h3>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="待审核" name="pending">
            <div class="history-list">
              <div v-for="item in pendingList" :key="item.id" class="history-item">
                <div class="item-info">
                  <span class="word-name">{{ item.word }}</span>
                  <span class="region">{{ item.region }}</span>
                </div>
                <el-tag type="warning" size="small">待审核</el-tag>
              </div>
              <EmptyState v-if="pendingList.length === 0" text="暂无待审核记录" />
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
              <EmptyState v-if="approvedList.length === 0" text="暂无已通过记录" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="已驳回" name="rejected">
            <div class="history-list">
              <div v-for="item in rejectedList" :key="item.id" class="history-item">
                <div class="item-info">
                  <span class="word-name">{{ item.word }}</span>
                  <span class="region">{{ item.region }}</span>
                  <span class="reason">驳回原因：{{ item.reject_reason || item.reason || '无' }}</span>
                </div>
                <div class="item-actions">
                  <el-tag type="danger" size="small">已驳回</el-tag>
                  <el-button size="small" @click="editItem(item)">重新编辑</el-button>
                </div>
              </div>
              <EmptyState v-if="rejectedList.length === 0" text="暂无已驳回记录" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { wordApi, dialectApi } from '@/api'
import EmptyState from '@/components/EmptyState/index.vue'

const route = useRoute()
const formRef = ref(null)
const fileInput = ref(null)
const submitting = ref(false)
const loading = ref(false)
const activeTab = ref('pending')

const form = reactive({
  wordId: '',
  region: [],
  videoFile: null,
  description: ''
})

const videoPreviewUrl = ref('')
const wordOptions = ref([])

const pendingList = ref([])
const approvedList = ref([])
const rejectedList = ref([])

const regionOptions = [
  { value: '华北', label: '华北', children: [
    { value: '北京', label: '北京' },
    { value: '天津', label: '天津' },
    { value: '河北', label: '河北' },
    { value: '山西', label: '山西' }
  ]},
  { value: '东北', label: '东北', children: [
    { value: '辽宁', label: '辽宁' },
    { value: '吉林', label: '吉林' },
    { value: '黑龙江', label: '黑龙江' }
  ]},
  { value: '华东', label: '华东', children: [
    { value: '上海', label: '上海' },
    { value: '江苏', label: '江苏' },
    { value: '浙江', label: '浙江' },
    { value: '安徽', label: '安徽' }
  ]},
  { value: '华中', label: '华中', children: [
    { value: '湖北', label: '湖北' },
    { value: '湖南', label: '湖南' },
    { value: '河南', label: '河南' }
  ]},
  { value: '华南', label: '华南', children: [
    { value: '广东', label: '广东' },
    { value: '广西', label: '广西' },
    { value: '海南', label: '海南' }
  ]},
  { value: '西南', label: '西南', children: [
    { value: '四川', label: '四川' },
    { value: '重庆', label: '重庆' },
    { value: '云南', label: '云南' }
  ]},
  { value: '西北', label: '西北', children: [
    { value: '陕西', label: '陕西' },
    { value: '甘肃', label: '甘肃' },
    { value: '青海', label: '青海' }
  ]}
]

const rules = {
  wordId: [{ required: true, message: '请选择词汇', trigger: 'change' }],
  region: [{ required: true, message: '请选择地区', trigger: 'change' }],
  videoFile: [{ required: true, message: '请上传视频', trigger: 'change' }]
}

onMounted(async () => {
  await Promise.all([fetchWords(), loadMyDialects()])

  // 检查 URL 参数中的 word_id
  const wordIdFromUrl = route.query.word_id
  if (wordIdFromUrl) {
    // 等待词汇列表加载完成后自动选择
    setTimeout(() => {
      const wordIdNum = parseInt(wordIdFromUrl)
      if (wordOptions.value.some(w => w.id === wordIdNum)) {
        form.wordId = wordIdNum
        handleWordChange()
        ElMessage.success('已自动选择词汇：' + wordOptions.value.find(w => w.id === wordIdNum)?.word)
      }
    }, 100)
  }
})

async function fetchWords() {
  loading.value = true
  try {
    const res = await wordApi.getList({ page: 1, page_size: 200 })
    wordOptions.value = res.items || res.data?.items || []
  } catch (e) {
    console.error('加载词汇失败', e)
    ElMessage.error('加载词汇列表失败')
  } finally {
    loading.value = false
  }
}

async function loadMyDialects() {
  try {
    const res = await dialectApi.getMyUploads()
    const items = res.data || res || []
    pendingList.value = items.filter(i => i.status === 'pending')
    approvedList.value = items.filter(i => i.status === 'approved')
    rejectedList.value = items.filter(i => i.status === 'rejected')
  } catch (e) {
    console.error('加载上传记录失败', e)
  }
}

function handleWordChange() {
  const selected = wordOptions.value.find(w => w.id === form.wordId)
  console.log('选择词汇:', selected?.word)
}

function triggerUpload() {
  fileInput.value.click()
}

function handleFileChange(e) {
  const file = e.target.files[0]
  if (!file) return

  if (file.size > 50 * 1024 * 1024) {
    ElMessage.warning('文件大小不能超过 50MB')
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
    const fd = new FormData()
    fd.append('word_id', form.wordId)
    fd.append('region', form.region.join('/'))
    fd.append('video', form.videoFile)
    if (form.description) {
      fd.append('description', form.description)
    }

    await dialectApi.upload(fd)
    ElMessage.success('上传成功，等待审核')

    form.wordId = ''
    form.region = []
    form.videoFile = null
    form.description = ''
    removeVideo()

    await loadMyDialects()
  } catch (e) {
    console.error('上传失败', e)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

function editItem(item) {
  form.wordId = item.word_id
  form.region = item.region.split('/')
  form.description = item.description || ''
  ElMessage.info('已加载历史记录，请修改后重新提交')
}
</script>

<style scoped lang="scss">
.upload-page {
  min-height: calc(100vh - 60px);
  padding: 48px 32px 80px;

  .upload-container {
    max-width: 800px;
    margin: 0 auto;

    .page-header {
      text-align: center;
      margin-bottom: 36px;

      h2 {
        font-size: 26px;
        font-weight: 700;
        color: #0d0d0d;
        margin: 0 0 8px;
        letter-spacing: -0.5px;
      }

      p {
        color: #8a8a8a;
        font-size: 14px;
        margin: 0;
      }
    }

    .upload-form {
      background: #fff;
      border: 1px solid #e8e8e8;
      border-radius: 10px;
      padding: 32px;
      margin-bottom: 24px;

      .upload-area {
        border: 2px dashed #e8e8e8;
        border-radius: 8px;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: border-color 180ms ease;

        &:hover {
          border-color: #c8c8c8;
        }

        .upload-placeholder {
          text-align: center;
          color: #8a8a8a;
          padding: 20px;

          .el-icon {
            font-size: 48px;
            margin-bottom: 12px;
            color: #c8c8c8;
          }

          p {
            font-size: 14px;
            color: #3a3a3a;
            margin: 0 0 6px;
            font-weight: 500;
          }

          span {
            font-size: 12px;
            color: #8a8a8a;
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
        gap: 12px;
        margin-top: 24px;
      }
    }

    .upload-history {
      background: #fff;
      border: 1px solid #e8e8e8;
      border-radius: 10px;
      padding: 32px;

      h3 {
        font-size: 17px;
        font-weight: 600;
        color: #0d0d0d;
        margin: 0 0 20px;
      }

      .history-list {
        min-height: 120px;

        .history-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 14px 0;
          border-bottom: 1px solid #e8e8e8;

          &:last-child {
            border-bottom: none;
          }

          .item-info {
            display: flex;
            flex-direction: column;
            gap: 4px;

            .word-name {
              font-weight: 600;
              color: #0d0d0d;
              font-size: 14px;
            }

            .region {
              font-size: 12px;
              color: #8a8a8a;
            }

            .reason {
              font-size: 12px;
              color: #c0392b;
            }
          }

          .item-actions {
            display: flex;
            align-items: center;
            gap: 10px;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .upload-page {
    padding: 32px 16px 60px;

    .upload-container {
      .upload-form {
        padding: 20px;
        border-radius: 8px;
      }

      .upload-history {
        padding: 20px;
        border-radius: 8px;
      }
    }
  }
}
</style>
