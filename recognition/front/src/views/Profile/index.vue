<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="avatar-section">
        <div class="avatar-wrapper">
          <svg class="avatar-svg" viewBox="0 0 100 100"><circle cx="50" cy="35" r="25" fill="#ddd"/><circle cx="50" cy="75" r="30" fill="#ddd"/></svg>
          <el-button class="edit-avatar" text @click="showEditProfile">
            <el-icon><Camera /></el-icon>
          </el-button>
        </div>
        <div class="user-info">
          <h2>{{ userInfo.username }}</h2>
          <p>{{ userInfo.bio || '这个人很懒，什么都没写' }}</p>
          <div class="user-tags">
            <el-tag size="small">Lv.{{ userInfo.level || 5 }}</el-tag>
            <el-tag size="small" type="warning">{{ userInfo.points || 0 }} 积分</el-tag>
          </div>
        </div>
      </div>

      <div class="follow-stats">
        <div class="stat-item">
          <span class="value">{{ userInfo.following || 12 }}</span>
          <span class="label">关注</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ userInfo.followers || 256 }}</span>
          <span class="label">粉丝</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ userInfo.posts || 8 }}</span>
          <span class="label">动态</span>
        </div>
      </div>
    </div>

    <div class="learn-stats">
      <h3>学习数据概览</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="stat-content">
            <span class="value">{{ learnStats.wordsLearned || 48 }}</span>
            <span class="label">已学词汇</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-content">
            <span class="value">{{ learnStats.hoursLearned || 25.5 }}h</span>
            <span class="label">学习时长</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="stat-content">
            <span class="value">{{ learnStats.daysStreak || 15 }}</span>
            <span class="label">连续天数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <el-icon><Medal /></el-icon>
          </div>
          <div class="stat-content">
            <span class="value">{{ learnStats.achievements || 4 }}</span>
            <span class="label">获得成就</span>
          </div>
        </div>
      </div>
    </div>

    <div class="profile-tabs">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="收藏" name="favorites">
          <div class="word-list" v-if="favoriteWords.length > 0">
            <div
              v-for="word in favoriteWords"
              :key="word.id"
              class="word-item"
              @click="openWordDetail(word.id)"
            >
              <div class="word-main">{{ word.word }}</div>
              <div class="word-tags">
                <el-tag size="small">{{ word.category }}</el-tag>
              </div>
              <el-button type="danger" size="small" text @click.stop="removeFavorite(word.id)">
                取消收藏
              </el-button>
            </div>
          </div>
          <EmptyState v-else text="暂无收藏">
            <template #action>
              <el-button type="primary" @click="$router.push('/dictionary')">去词典看看</el-button>
            </template>
          </EmptyState>
        </el-tab-pane>

        <el-tab-pane label="生词本" name="newwords">
          <div class="word-list" v-if="newWordsList.length > 0">
            <div
              v-for="word in newWordsList"
              :key="word.id"
              class="word-item"
              @click="openWordDetail(word.id)"
            >
              <div class="word-main">{{ word.word }}</div>
              <div class="word-tags">
                <el-tag size="small" type="warning">生词</el-tag>
              </div>
              <el-button type="primary" size="small" @click.stop="openWordDetail(word.id)">
                学习
              </el-button>
              <el-button type="danger" size="small" text @click.stop="removeNewWord(word.id)">
                移除
              </el-button>
            </div>
          </div>
          <EmptyState v-else text="生词本为空">
            <template #action>
              <el-button type="primary" @click="$router.push('/dictionary')">开始学习</el-button>
            </template>
          </EmptyState>
        </el-tab-pane>

        <el-tab-pane label="学习笔记" name="notes">
          <div v-if="allNotes.length > 0" class="notes-list">
            <div v-for="note in allNotes" :key="note.wordId" class="note-section">
              <div class="note-header">
                <span class="word-name">{{ getWordName(note.wordId) }}</span>
                <el-button type="primary" size="small" @click="openWordDetail(note.wordId)">
                  查看详情
                </el-button>
              </div>
              <div class="note-items">
                <div v-for="item in note.notes" :key="item.id" class="note-item">
                  <p>{{ item.content }}</p>
                  <div class="note-meta">
                    <span class="note-time">{{ item.time }}</span>
                    <el-button type="danger" size="small" text @click="deleteNote(note.wordId, item.id)">
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <EmptyState v-else text="暂无笔记">
            <template #action>
              <el-button type="primary" @click="$router.push('/dictionary')">去添加笔记</el-button>
            </template>
          </EmptyState>
        </el-tab-pane>

        <el-tab-pane label="动态" name="posts">
          <div class="content-list">
            <div v-for="post in myPosts" :key="post.id" class="post-item">
              <p>{{ post.content }}</p>
              <div class="post-meta">
                <span>{{ post.time }}</span>
                <span>👍 {{ post.likes }}</span>
                <el-button type="danger" size="small" text @click="deletePost(post.id)">删除</el-button>
              </div>
            </div>
            <EmptyState v-if="myPosts.length === 0" text="暂无发布的动态" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="作品" name="works">
          <div class="content-list">
            <div v-for="work in myWorks" :key="work.id" class="work-item">
              <div class="work-content">{{ work.content }}</div>
              <div class="work-meta">
                <span>{{ work.type }}</span>
                <span>{{ work.time }}</span>
              </div>
            </div>
            <EmptyState v-if="myWorks.length === 0" text="暂无上传的作品" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="方言上传" name="dialects">
          <div class="content-list">
            <div v-for="item in myDialects" :key="item.id" class="dialect-item">
              <div class="item-info">
                <span class="word">{{ item.word }}</span>
                <span class="region">{{ item.region }}</span>
              </div>
              <el-tag :type="getStatusType(item.status)" size="small">
                {{ getStatusText(item.status) }}
              </el-tag>
            </div>
            <EmptyState v-if="myDialects.length === 0" text="暂无上传的方言" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <div class="quick-actions">
      <h3>快捷操作</h3>
      <div class="action-grid">
        <div class="action-item" @click="$router.push('/achievements')">
          <el-icon><Medal /></el-icon>
          <span>我的成就</span>
        </div>
        <div class="action-item" @click="$router.push('/audit')">
          <el-icon><Document /></el-icon>
          <span>审核状态</span>
        </div>
        <div class="action-item" @click="$router.push('/settings')">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </div>
        <div class="action-item" @click="logout">
          <el-icon><SwitchButton /></el-icon>
          <span>退出登录</span>
        </div>
      </div>
    </div>

    <el-dialog v-model="editProfileVisible" title="编辑资料" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="昵称">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="editForm.bio" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="editForm.gender">
            <el-option label="保密" value="secret" />
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editProfileVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Camera, Reading, Timer, Calendar, Medal, Document, Setting, SwitchButton, Star, Collection } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore, useLearnStore } from '@/store'
import { useWordDetailStore } from '@/store'
import EmptyState from '@/components/EmptyState/index.vue'

const router = useRouter()
const userStore = useUserStore()
const learnStore = useLearnStore()
const { openWordDetail } = useWordDetailStore()

const activeTab = ref('favorites')
const editProfileVisible = ref(false)

// 用户信息 - 优先从store读取，否则使用默认值
const userInfo = computed(() => ({
  username: userStore.userInfo?.username || '手语学习者',
  bio: userStore.userInfo?.bio || '学习手语，传递温暖',
  level: userStore.userInfo?.level || 5,
  points: userStore.userInfo?.points || 0,
  following: userStore.userInfo?.following || 0,
  followers: userStore.userInfo?.followers || 0,
  posts: userStore.userInfo?.posts || 0,
  gender: userStore.userInfo?.gender || 'secret',
  exp: userStore.userInfo?.exp || 0
}))

// 编辑表单
const editForm = reactive({
  username: '',
  bio: '',
  gender: 'secret'
})

// 学习统计 - 从learnStore读取
const learnStats = computed(() => ({
  wordsLearned: learnStore.favorites?.length + learnStore.newWords?.length || 0,
  hoursLearned: learnStore.learnStats?.reduce((sum, s) => sum + (s.minutes || 0), 0) / 60 || 0,
  daysStreak: calculateDaysStreak(),
  achievements: 0
}))

// 计算连续学习天数
function calculateDaysStreak() {
  if (!learnStore.learnStats || learnStore.learnStats.length === 0) return 0
  const stats = [...learnStore.learnStats].sort((a, b) => new Date(b.date) - new Date(a.date))
  let streak = 0
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  for (let i = 0; i < stats.length; i++) {
    const statDate = new Date(stats[i].date)
    statDate.setHours(0, 0, 0, 0)
    const expectedDate = new Date(today)
    expectedDate.setDate(expectedDate.getDate() - i)

    if (statDate.getTime() === expectedDate.getTime() && stats[i].minutes > 0) {
      streak++
    } else if (i === 0 && statDate.getTime() === expectedDate.getTime() - 86400000) {
      // 昨天也算连续
      streak++
    } else {
      break
    }
  }
  return streak
}

const allWords = [
  { id: 1, word: '你好', category: '基础' },
  { id: 2, word: '谢谢', category: '基础' },
  { id: 3, word: '再见', category: '基础' },
  { id: 4, word: '对不起', category: '基础' },
  { id: 5, word: '请', category: '基础' },
  { id: 6, word: '家庭', category: '生活' },
  { id: 7, word: '爸爸', category: '生活' },
  { id: 8, word: '妈妈', category: '生活' },
  { id: 9, word: '吃饭', category: '生活' },
  { id: 10, word: '喝水', category: '生活' },
  { id: 11, word: '工作', category: '社会' },
  { id: 12, word: '学习', category: '社会' },
  { id: 13, word: '医生', category: '社会' },
  { id: 14, word: '老师', category: '社会' },
  { id: 15, word: '朋友', category: '社交' },
  { id: 16, word: '帮助', category: '社交' },
  { id: 17, word: '喜欢', category: '情感' },
  { id: 18, word: '爱', category: '情感' },
  { id: 19, word: '快乐', category: '情感' },
  { id: 20, word: '电脑', category: '科技' }
]

const favorites = computed(() => learnStore.favorites)
const newWords = computed(() => learnStore.newWords)

const favoriteWords = computed(() => {
  return allWords.filter(w => favorites.value.includes(w.id))
})

const newWordsList = computed(() => {
  return allWords.filter(w => newWords.value.includes(w.id))
})

const allNotes = computed(() => {
  const notes = learnStore.notes
  return Object.entries(notes).map(([wordId, noteArr]) => ({
    wordId: Number(wordId),
    notes: noteArr
  }))
})

function getWordName(wordId) {
  const word = allWords.find(w => w.id === Number(wordId))
  return word ? word.word : '未知词汇'
}

const myPosts = ref([
  { id: 1, content: '今天学习了手语基础动作，感觉很有收获！', time: '2小时前', likes: 23 },
  { id: 2, content: '分享一个学习手语的小技巧给大家', time: '1天前', likes: 56 }
])

const myWorks = ref([
  { id: 1, content: '手语学习笔记整理', type: '文档', time: '3天前' },
  { id: 2, content: '常用手语动作演示视频', type: '视频', time: '1周前' }
])

const myDialects = ref([
  { id: 1, word: '你好', region: '北京', status: 'approved' },
  { id: 2, word: '谢谢', region: '上海', status: 'pending' },
  { id: 3, word: '再见', region: '四川', status: 'rejected' }
])

// 打开编辑资料弹窗，同步当前用户信息到表单
function showEditProfile() {
  editForm.username = userInfo.value.username
  editForm.bio = userInfo.value.bio
  editForm.gender = userInfo.value.gender
  editProfileVisible.value = true
}

function showEditAvatar() {
  ElMessage.info('头像上传功能开发中')
}

function getStatusType(status) {
  const types = { approved: 'success', pending: 'warning', rejected: 'danger' }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = { approved: '已通过', pending: '审核中', rejected: '已驳回' }
  return texts[status] || '未知'
}

function deletePost(id) {
  ElMessageBox.confirm('确定删除这条动态吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    myPosts.value = myPosts.value.filter(p => p.id !== id)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function removeFavorite(wordId) {
  learnStore.toggleFavorite(wordId)
}

function removeNewWord(wordId) {
  learnStore.toggleNewWord(wordId)
}

function deleteNote(wordId, noteId) {
  learnStore.deleteNote(wordId, noteId)
}

function saveProfile() {
  // 更新 store 中的用户信息
  userStore.setUserInfo({
    ...userStore.userInfo,
    username: editForm.username,
    bio: editForm.bio,
    gender: editForm.gender
  })
  editProfileVisible.value = false
  ElMessage.success('保存成功')
}

function logout() {
  ElMessageBox.confirm('确定退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  }).catch(() => {})
}
</script>

<style scoped lang="scss">
.profile-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 60px);
  padding-bottom: 20px;

  .profile-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 30px;
    color: #fff;
    margin-bottom: 20px;

    .avatar-section {
      display: flex;
      gap: 24px;
      margin-bottom: 24px;

      .avatar-wrapper {
        position: relative;

        .avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          border: 3px solid #fff;
        }

        .edit-avatar {
          position: absolute;
          bottom: 0;
          right: 0;
          background: rgba(255,255,255,0.9);
          border-radius: 50%;
          padding: 6px;
        }
      }

      .user-info {
        flex: 1;

        h2 {
          font-size: 24px;
          margin: 0 0 8px;
        }

        p {
          font-size: 14px;
          opacity: 0.9;
          margin: 0 0 12px;
        }

        .user-tags {
          display: flex;
          gap: 8px;
        }
      }
    }

    .follow-stats {
      display: flex;
      justify-content: space-around;

      .stat-item {
        text-align: center;

        .value {
          display: block;
          font-size: 24px;
          font-weight: bold;
        }

        .label {
          font-size: 12px;
          opacity: 0.8;
        }
      }
    }
  }

  .learn-stats {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;

    h3 {
      font-size: 16px;
      color: #333;
      margin-bottom: 16px;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;

      .stat-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px;
        background: #f9fafb;
        border-radius: 8px;

        .stat-icon {
          width: 44px;
          height: 44px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;

          .el-icon {
            font-size: 22px;
            color: #fff;
          }
        }

        .stat-content {
          display: flex;
          flex-direction: column;

          .value {
            font-size: 20px;
            font-weight: bold;
            color: #333;
          }

          .label {
            font-size: 12px;
            color: #999;
          }
        }
      }
    }
  }

  .profile-tabs {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;

    .word-list {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .word-item {
        display: flex;
        align-items: center;
        padding: 16px 20px;
        background: #f9fafb;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.3s;

        &:hover {
          background: #f0f2f5;
        }

        .word-main {
          font-size: 18px;
          font-weight: bold;
          color: #333;
          margin-right: auto;
        }

        .word-tags {
          margin-right: 16px;
        }
      }
    }

    .notes-list {
      .note-section {
        margin-bottom: 24px;
        padding-bottom: 24px;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
          margin-bottom: 0;
          padding-bottom: 0;
        }

        .note-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          .word-name {
            font-size: 18px;
            font-weight: bold;
            color: #333;
          }
        }

        .note-items {
          .note-item {
            padding: 12px 16px;
            background: #f9fafb;
            border-radius: 8px;
            margin-bottom: 8px;

            p {
              margin: 0 0 8px;
              color: #333;
            }

            .note-meta {
              display: flex;
              justify-content: space-between;
              align-items: center;

              .note-time {
                font-size: 12px;
                color: #999;
              }
            }
          }
        }
      }
    }

    .content-list {
      .post-item {
        padding: 16px;
        border-bottom: 1px solid #f0f0f0;

        p {
          color: #333;
          margin-bottom: 8px;
        }

        .post-meta {
          display: flex;
          align-items: center;
          gap: 16px;
          font-size: 12px;
          color: #999;
        }
      }

      .work-item {
        padding: 16px;
        background: #f9fafb;
        border-radius: 8px;
        margin-bottom: 12px;

        .work-content {
          color: #333;
          margin-bottom: 8px;
        }

        .work-meta {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #999;
        }
      }

      .dialect-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        background: #f9fafb;
        border-radius: 8px;
        margin-bottom: 12px;

        .item-info {
          display: flex;
          flex-direction: column;
          gap: 4px;

          .word {
            font-weight: bold;
            color: #333;
          }

          .region {
            font-size: 12px;
            color: #999;
          }
        }
      }
    }
  }

  .quick-actions {
    background: #fff;
    border-radius: 12px;
    padding: 24px;

    h3 {
      font-size: 16px;
      color: #333;
      margin-bottom: 16px;
    }

    .action-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;

      .action-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px;
        background: #f9fafb;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          background: #f0f2f5;
        }

        .el-icon {
          font-size: 24px;
          color: #667eea;
        }

        span {
          color: #333;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .profile-page {
    .profile-header .avatar-section {
      flex-direction: column;
      align-items: center;
      text-align: center;
    }
  }
}
</style>
