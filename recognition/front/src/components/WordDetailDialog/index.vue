<template>
  <el-dialog
    v-model="wordDetailStore.dialogVisible"
    :title="wordDetailStore.wordData?.word || ''"
    width="720px"
    :close-on-click-modal="true"
    :lock-scroll="false"
    class="word-detail-dialog"
    :show-close="true"
    @closed="onDialogClosed"
  >
    <div v-if="wordDetailStore.loading" class="loading-wrapper">
      <el-icon class="is-loading" style="font-size:24px"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <div v-else-if="wordDetailStore.wordData" class="detail-content">
      <div class="word-header">
        <div class="word-tags">
          <el-tag size="small">{{ wordDetailStore.wordData.category }}</el-tag>
          <el-tag size="small" type="info">{{ wordDetailStore.wordData.scene }}</el-tag>
          <el-tag size="small" :type="getDifficultyType(wordDetailStore.wordData.difficulty)">
            {{ ['入门', '基础', '进阶'][wordDetailStore.wordData.difficulty - 1] }}
          </el-tag>
          <el-tag size="small" type="success">{{ wordDetailStore.wordData.region }}</el-tag>
        </div>
        <div class="word-actions">
          <el-button :type="wordDetailStore.isFavorite ? 'primary' : 'default'" size="small" @click="toggleFavorite">
            <el-icon><Star /></el-icon>
            {{ wordDetailStore.isFavorite ? '已收藏' : '收藏' }}
          </el-button>
          <el-button :type="wordDetailStore.isNewWord ? 'warning' : 'default'" size="small" @click="toggleNewWord">
            <el-icon><Collection /></el-icon>
            {{ wordDetailStore.isNewWord ? '已标记' : '标记生词' }}
          </el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="detail-tabs">
        <el-tab-pane label="视频演示" name="video">
          <div class="video-section">
            <VideoPlayer :src="wordDetailStore.wordData.videoUrl" />
            <div class="video-tip">
              <el-icon><InfoFilled /></el-icon>
              <span>请仔细观察手势动作，注意手型、位置和运动方向</span>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="图解" name="images">
          <div class="images-section">
            <div v-if="wordDetailStore.wordData.images && wordDetailStore.wordData.images.length" class="image-grid">
              <div v-for="(img, idx) in wordDetailStore.wordData.images" :key="idx" class="image-item">
                <img :src="img" :alt="`图解${idx + 1}`" />
              </div>
            </div>
            <div v-else class="no-images">
              <div style="font-size:40px;margin-bottom:8px;">🖐</div>
              <span>暂无图解</span>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="动作分解" name="desc">
          <div class="desc-section">
            <div class="step-item">
              <div class="step-icon">1</div>
              <div class="step-body">
                <div class="step-label">手型</div>
                <div class="step-text">{{ wordDetailStore.wordData.handShape }}</div>
              </div>
            </div>
            <div class="step-item">
              <div class="step-icon">2</div>
              <div class="step-body">
                <div class="step-label">位置</div>
                <div class="step-text">{{ wordDetailStore.wordData.position }}</div>
              </div>
            </div>
            <div class="step-item">
              <div class="step-icon">3</div>
              <div class="step-body">
                <div class="step-label">动作</div>
                <div class="step-text">{{ wordDetailStore.wordData.movement }}</div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="方言专区" name="dialect">
          <div class="dialect-section">
            <div class="dialect-header">
              <span>共创方言手语</span>
              <el-button type="primary" size="small" @click="goUpload">
                <el-icon><Upload /></el-icon>
                上传当地方言
              </el-button>
            </div>

            <div class="region-filter">
              <el-radio-group v-model="selectedRegion" size="small">
                <el-radio-button label="">全部</el-radio-button>
                <el-radio-button label="北京">北京</el-radio-button>
                <el-radio-button label="上海">上海</el-radio-button>
                <el-radio-button label="广东">广东</el-radio-button>
                <el-radio-button label="四川">四川</el-radio-button>
                <el-radio-button label="东北">东北</el-radio-button>
              </el-radio-group>
            </div>

            <div v-if="filteredDialects.length === 0" class="no-dialect">
              <span>暂无{{ selectedRegion ? selectedRegion + '地区' : '' }}方言手语，成为第一个贡献者！</span>
            </div>

            <div v-else class="dialect-list">
              <div v-for="dialect in filteredDialects" :key="dialect.id" class="dialect-item">
                <VideoPlayer :src="dialect.videoUrl" />
                <div class="dialect-footer">
                  <span class="region-tag">{{ dialect.region }}</span>
                  <el-tag :type="getStatusType(dialect.status)" size="small">
                    {{ getStatusText(dialect.status) }}
                  </el-tag>
                  <span class="author">@{{ dialect.author }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="学习笔记" name="notes">
          <div class="notes-section">
            <div class="notes-list">
              <div v-for="note in currentNotes" :key="note.id" class="note-item">
                <p>{{ note.content }}</p>
                <div class="note-footer">
                  <span>{{ note.time }}</span>
                  <el-button type="danger" size="small" text @click="deleteNote(note.id)">删除</el-button>
                </div>
              </div>
              <div v-if="currentNotes.length === 0" class="no-notes">暂无笔记，添加第一条吧</div>
            </div>
            <div class="add-note">
              <el-input
                v-model="newNote"
                type="textarea"
                :rows="2"
                placeholder="记录学习心得..."
                maxlength="200"
                show-word-limit
              />
              <el-button type="primary" size="small" :disabled="!newNote.trim()" @click="addNote">添加笔记</el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Star, Collection, InfoFilled, Upload, Loading } from '@element-plus/icons-vue'
import { useWordDetailStore, useLearnStore } from '@/store'
import VideoPlayer from '@/components/VideoPlayer/index.vue'

const wordDetailStore = useWordDetailStore()
const learnStore = useLearnStore()
const router = useRouter()

const activeTab = ref('video')
const selectedRegion = ref('')
const newNote = ref('')

const currentNotes = computed(() => {
  if (!wordDetailStore.currentWordId) return []
  return learnStore.getNotes(String(wordDetailStore.currentWordId))
})

const filteredDialects = computed(() => {
  if (!selectedRegion.value) return wordDetailStore.allDialects
  return wordDetailStore.allDialects.filter(d => d.region === selectedRegion.value)
})

watch(() => wordDetailStore.dialogVisible, (val) => {
  if (val) {
    activeTab.value = 'video'
    selectedRegion.value = ''
    newNote.value = ''
  }
})

function getDifficultyType(d) {
  return { 1: 'success', 2: 'warning', 3: 'danger' }[d] || 'info'
}

function getStatusType(status) {
  return { approved: 'success', pending: 'warning', rejected: 'danger' }[status] || 'info'
}

function getStatusText(status) {
  return { approved: '已通过', pending: '审核中', rejected: '已驳回' }[status] || '未知'
}

function toggleFavorite() {
  if (wordDetailStore.wordData) learnStore.toggleFavorite(wordDetailStore.wordData.id)
}

function toggleNewWord() {
  if (wordDetailStore.wordData) learnStore.toggleNewWord(wordDetailStore.wordData.id)
}

function addNote() {
  if (!newNote.value.trim() || !wordDetailStore.wordData) return
  learnStore.addNote(String(wordDetailStore.wordData.id), newNote.value)
  newNote.value = ''
}

function deleteNote(noteId) {
  if (wordDetailStore.wordData) learnStore.deleteNote(String(wordDetailStore.wordData.id), noteId)
}

function onDialogClosed() {
  wordDetailStore.wordData = null
  wordDetailStore.currentWordId = null
}

function goUpload() {
  wordDetailStore.dialogVisible = false
  router.push('/upload')
}
</script>

<style scoped lang="scss">
.word-detail-dialog {
  .loading-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 60px;
    color: #999;
    font-size: 14px;
  }

  .detail-content {
    .word-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;

      .word-tags { display: flex; gap: 8px; flex-wrap: wrap; }
      .word-actions { display: flex; gap: 8px; }
    }

    .detail-tabs {
      :deep(.el-tabs__header) { margin-bottom: 16px; }
    }

    .video-section {
      .video-tip {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 12px;
        padding: 10px 14px;
        background: #f0f9ff;
        border-radius: 8px;
        font-size: 13px;
        color: #667eea;
      }
    }

    .images-section {
      .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;

        .image-item {
          border-radius: 8px;
          overflow: hidden;
          background: #f9fafb;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 200px;

          img { width: 100%; height: 200px; object-fit: contain; }
        }
      }

      .no-images {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 60px;
        color: #999;
        background: #f9fafb;
        border-radius: 8px;
        font-size: 14px;
      }
    }

    .desc-section {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .step-item {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 14px 16px;
        background: #f9fafb;
        border-radius: 8px;

        .step-icon {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 13px;
          flex-shrink: 0;
        }

        .step-body {
          flex: 1;
          .step-label { font-weight: bold; color: #333; font-size: 14px; margin-bottom: 4px; }
          .step-text { color: #666; font-size: 13px; line-height: 1.6; }
        }
      }
    }

    .dialect-section {
      .dialect-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        font-weight: bold;
        color: #333;
      }

      .region-filter { margin-bottom: 16px; display: flex; flex-wrap: wrap; gap: 8px; }

      .no-dialect {
        text-align: center;
        padding: 40px;
        color: #999;
        font-size: 14px;
        background: #f9fafb;
        border-radius: 8px;
      }

      .dialect-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        max-height: 360px;
        overflow-y: auto;

        .dialect-item {
          border-radius: 8px;
          overflow: hidden;
          background: #f9fafb;

          .dialect-footer {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 14px;

            .region-tag { font-weight: bold; color: #333; font-size: 14px; }
            .author { margin-left: auto; font-size: 12px; color: #999; }
          }
        }
      }
    }

    .notes-section {
      .notes-list {
        margin-bottom: 16px;
        max-height: 280px;
        overflow-y: auto;

        .note-item {
          padding: 12px 14px;
          border-bottom: 1px solid #f0f0f0;
          p { margin: 0 0 8px; color: #333; font-size: 14px; }
          .note-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            span { font-size: 12px; color: #999; }
          }
        }

        .no-notes { text-align: center; padding: 32px; color: #999; font-size: 14px; }
      }

      .add-note {
        display: flex;
        flex-direction: column;
        gap: 10px;
        .el-button { align-self: flex-end; }
      }
    }
  }
}

:deep(.el-dialog__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  margin-right: 0;
  .el-dialog__title { font-size: 20px; font-weight: bold; }
}

:deep(.el-dialog__body) {
  padding: 20px;
  max-height: 75vh;
  overflow-y: auto;
}
</style>
