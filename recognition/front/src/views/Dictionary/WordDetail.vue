<template>
  <div class="word-detail-page">
    <div v-if="loading" class="loading-wrapper">
      <Loading text="加载中..." />
    </div>
    
    <div v-else-if="wordData" class="detail-content">
      <div class="back-bar">
        <el-button @click="$router.back()" text>
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
      </div>
      
      <div class="main-section">
        <div class="word-header">
          <h1 class="word-title">{{ wordData.word }}</h1>
          <div class="word-actions">
            <el-button :type="isFavorite ? 'primary' : 'default'" @click="toggleFavorite">
              <el-icon><Star /></el-icon>
              {{ isFavorite ? '已收藏' : '收藏' }}
            </el-button>
            <el-button :type="isNewWord ? 'warning' : 'default'" @click="toggleNewWord">
              <el-icon><Collection /></el-icon>
              {{ isNewWord ? '已标记' : '标记生词' }}
            </el-button>
          </div>
        </div>
        
        <div class="video-section">
          <VideoPlayer :src="wordData.videoUrl" />
          <div class="video-tips">
            <el-icon><InfoFilled /></el-icon>
            <span>请仔细观察手势动作，注意手型、位置和运动方向</span>
          </div>
        </div>
        
        <div class="description-section">
          <h3>动作分解</h3>
          <div class="step-list">
            <div class="step-item">
              <div class="step-num">1</div>
              <div class="step-content">
                <div class="step-title">手型</div>
                <div class="step-desc">{{ wordData.handShape || '五指伸直，掌心朝外' }}</div>
              </div>
            </div>
            <div class="step-item">
              <div class="step-num">2</div>
              <div class="step-content">
                <div class="step-title">位置</div>
                <div class="step-desc">{{ wordData.position || '双手置于胸前' }}</div>
              </div>
            </div>
            <div class="step-item">
              <div class="step-num">3</div>
              <div class="step-content">
                <div class="step-title">动作</div>
                <div class="step-desc">{{ wordData.movement || '双手向外推出' }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="note-section">
          <h3>学习笔记</h3>
          <div class="note-list">
            <div v-for="note in notes" :key="note.id" class="note-item">
              <p>{{ note.content }}</p>
              <span class="note-time">{{ note.time }}</span>
              <el-button type="danger" size="small" text @click="deleteNote(note.id)">删除</el-button>
            </div>
          </div>
          <div class="add-note">
            <el-input
              v-model="newNote"
              type="textarea"
              :rows="2"
              placeholder="添加学习笔记..."
            />
            <el-button type="primary" @click="addNote" :disabled="!newNote.trim()">添加笔记</el-button>
          </div>
        </div>
      </div>
      
      <div class="dialect-section">
        <div class="section-header">
          <h3>方言手语</h3>
          <el-select v-model="selectedRegion" placeholder="选择地区" clearable>
            <el-option label="全国通用" value="" />
            <el-option label="北京" value="北京" />
            <el-option label="上海" value="上海" />
            <el-option label="广东" value="广东" />
            <el-option label="四川" value="四川" />
          </el-select>
        </div>
        
        <div v-if="filteredDialects.length === 0" class="no-dialect">
          <p>暂无该地区的方言手语视频</p>
          <el-button type="primary" @click="$router.push('/upload')">上传当地方言手语</el-button>
        </div>
        
        <div v-else class="dialect-list">
          <div v-for="dialect in filteredDialects" :key="dialect.id" class="dialect-item">
            <VideoPlayer :src="dialect.videoUrl" />
            <div class="dialect-info">
              <span class="region-tag">{{ dialect.region }}</span>
              <el-tag :type="getStatusType(dialect.status)" size="small">
                {{ getStatusText(dialect.status) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
      
      <div class="related-section">
        <h3>相关词汇</h3>
        <div class="related-list">
          <div
            v-for="item in relatedWords"
            :key="item.id"
            class="related-item"
            @click="$router.push(`/dictionary/${item.id}`)"
          >
            {{ item.word }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Star, Collection, InfoFilled } from '@element-plus/icons-vue'
import { wordApi } from '@/api'
import { useLearnStore } from '@/store'
import VideoPlayer from '@/components/VideoPlayer/index.vue'
import Loading from '@/components/Loading/index.vue'

const route = useRoute()
const learnStore = useLearnStore()

const loading = ref(false)
const wordData = ref(null)
const newNote = ref('')
const selectedRegion = ref('')

const isFavorite = computed(() => learnStore.isFavorite(route.params.id))
const isNewWord = computed(() => learnStore.isNewWord(route.params.id))
const notes = computed(() => learnStore.getNotes(route.params.id))
const relatedWords = ref([
  { id: 1, word: '你好' },
  { id: 2, word: '谢谢' },
  { id: 3, word: '再见' }
])

const filteredDialects = computed(() => {
  if (!wordData.value?.dialects) return []
  if (!selectedRegion.value) return wordData.value.dialects
  return wordData.value.dialects.filter(d => d.region === selectedRegion.value)
})

async function fetchWord() {
  loading.value = true
  try {
    const res = await wordApi.getWordById(route.params.id)
    wordData.value = res.data
  } catch (e) {
    console.error('获取词汇详情失败', e)
  } finally {
    loading.value = false
  }
}

function toggleFavorite() {
  learnStore.toggleFavorite(route.params.id)
}

function toggleNewWord() {
  learnStore.toggleNewWord(route.params.id)
}

function addNote() {
  if (!newNote.value.trim()) return
  learnStore.addNote(route.params.id, newNote.value)
  newNote.value = ''
}

function deleteNote(noteId) {
  learnStore.deleteNote(route.params.id, noteId)
}

function getStatusType(status) {
  const types = { approved: 'success', pending: 'warning', rejected: 'danger' }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = { approved: '已通过', pending: '审核中', rejected: '已驳回' }
  return texts[status] || '未知'
}

onMounted(fetchWord)
</script>

<style scoped lang="scss">
.word-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 130px);
  
  .loading-wrapper {
    padding: 100px;
  }
  
  .detail-content {
    .back-bar {
      margin-bottom: 20px;
      
      .el-button {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
    
    .main-section {
      background: #fff;
      border-radius: 12px;
      padding: 30px;
      margin-bottom: 20px;
      
      .word-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        
        .word-title {
          font-size: 32px;
          color: #333;
          margin: 0;
        }
        
        .word-actions {
          display: flex;
          gap: 12px;
        }
      }
      
      .video-section {
        margin-bottom: 30px;
        
        .video-tips {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 12px;
          padding: 12px;
          background: #f0f9ff;
          border-radius: 8px;
          font-size: 14px;
          color: #667eea;
        }
      }
      
      .description-section,
      .note-section {
        margin-bottom: 30px;
        
        h3 {
          font-size: 18px;
          color: #333;
          margin-bottom: 16px;
        }
      }
      
      .step-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
        
        .step-item {
          display: flex;
          gap: 16px;
          padding: 16px;
          background: #f9fafb;
          border-radius: 8px;
          
          .step-num {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
          }
          
          .step-content {
            .step-title {
              font-weight: bold;
              color: #333;
              margin-bottom: 4px;
            }
            
            .step-desc {
              color: #666;
              font-size: 14px;
            }
          }
        }
      }
      
      .note-list {
        margin-bottom: 16px;
        
        .note-item {
          padding: 12px;
          border-bottom: 1px solid #f0f0f0;
          position: relative;
          
          p {
            margin: 0 0 8px;
            color: #333;
          }
          
          .note-time {
            font-size: 12px;
            color: #999;
            margin-right: 60px;
          }
          
          .el-button {
            position: absolute;
            right: 0;
            bottom: 12px;
          }
        }
      }
      
      .add-note {
        display: flex;
        flex-direction: column;
        gap: 12px;
        
        .el-button {
          align-self: flex-end;
        }
      }
    }
    
    .dialect-section {
      background: #fff;
      border-radius: 12px;
      padding: 30px;
      margin-bottom: 20px;
      
      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        
        h3 {
          font-size: 18px;
          color: #333;
          margin: 0;
        }
      }
      
      .no-dialect {
        text-align: center;
        padding: 40px;
        color: #999;
        
        p {
          margin-bottom: 16px;
        }
      }
      
      .dialect-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        
        .dialect-item {
          border-radius: 8px;
          overflow: hidden;
          background: #f9fafb;
          
          .dialect-info {
            padding: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            
            .region-tag {
              color: #333;
              font-weight: bold;
            }
          }
        }
      }
    }
    
    .related-section {
      background: #fff;
      border-radius: 12px;
      padding: 30px;
      
      h3 {
        font-size: 18px;
        color: #333;
        margin-bottom: 16px;
      }
      
      .related-list {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        
        .related-item {
          padding: 10px 20px;
          background: #f9fafb;
          border-radius: 20px;
          cursor: pointer;
          transition: all 0.3s;
          
          &:hover {
            background: #667eea;
            color: #fff;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .word-detail-page {
    .detail-content {
      .main-section {
        padding: 20px;
        
        .word-header {
          flex-direction: column;
          gap: 16px;
          align-items: flex-start;
        }
      }
    }
  }
}
</style>
