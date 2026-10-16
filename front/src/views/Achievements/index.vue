<template>
  <div class="achievements-page">
    <div class="page-header">
      <h1>成就勋章</h1>
      <p class="subtitle">记录你的每一个进步，见证你的成长历程</p>
    </div>

    <!-- Stats Overview -->
    <div class="stats-overview">
      <div class="stat-item">
        <span class="stat-value">{{ unlockedCount }}</span>
        <span class="stat-label">已解锁</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-value">{{ totalCount }}</span>
        <span class="stat-label">全部成就</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-value">{{ completionRate }}%</span>
        <span class="stat-label">完成率</span>
      </div>
    </div>

    <!-- Achievement Tabs -->
    <div class="tabs-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部" name="all"></el-tab-pane>
        <el-tab-pane label="已解锁" name="unlocked"></el-tab-pane>
        <el-tab-pane label="进行中" name="in-progress"></el-tab-pane>
        <el-tab-pane label="未解锁" name="locked"></el-tab-pane>
      </el-tabs>
    </div>

    <!-- Achievement Grid -->
    <div class="achievement-grid">
      <div
        v-for="badge in filteredAchievements"
        :key="badge.id"
        class="achievement-card"
        :class="{ locked: !badge.unlocked, unlocked: badge.unlocked }"
        @click="viewBadge(badge)"
      >
        <div class="badge-icon">
          <img
            v-if="badge.unlocked"
            :src="badge.icon"
            :alt="badge.name"
          />
          <div v-else class="locked-icon">
            <el-icon><Lock /></el-icon>
          </div>
          <div v-if="badge.isNew" class="new-badge">
            <el-icon><Sunny /></el-icon>
            NEW
          </div>
        </div>
        <div class="badge-info">
          <h3>{{ badge.name }}</h3>
          <p>{{ badge.description }}</p>
        </div>
        <div v-if="badge.unlocked" class="badge-date">
          <el-icon><Calendar /></el-icon>
          {{ badge.unlockedAt }}
        </div>
        <div v-else class="badge-progress">
          <el-progress
            :percentage="badge.progress"
            :show-text="false"
            :stroke-width="4"
          />
          <span class="progress-text">{{ badge.progress }}%</span>
        </div>
      </div>
    </div>

    <!-- Badge Detail Dialog -->
    <el-dialog
      v-model="showBadgeDetail"
      :title="currentBadge?.name"
      width="500px"
      class="badge-dialog"
    >
      <div class="badge-detail">
        <div class="detail-icon">
          <img
            v-if="currentBadge?.unlocked"
            :src="currentBadge?.icon"
            :alt="currentBadge?.name"
          />
          <div v-else class="locked-large">
            <el-icon><Lock /></el-icon>
          </div>
        </div>

        <div class="detail-info">
          <h2>{{ currentBadge?.name }}</h2>
          <p class="detail-desc">{{ currentBadge?.description }}</p>
        </div>

        <div class="detail-requirements">
          <h3>获取条件</h3>
          <ul>
            <li v-for="(req, index) in currentBadge?.requirements" :key="index">
              <el-icon v-if="currentBadge?.unlocked" color="#67c23a"><Check /></el-icon>
              <el-icon v-else color="#8a8a8a"><CircleCheck /></el-icon>
              {{ req }}
            </li>
          </ul>
        </div>

        <div v-if="currentBadge?.unlocked" class="detail-date">
          <el-icon><Calendar /></el-icon>
          解锁时间：{{ currentBadge?.unlockedAt }}
        </div>

        <div v-else class="detail-progress">
          <el-progress
            type="circle"
            :percentage="currentBadge?.progress || 0"
            :width="100"
          />
          <p>继续加油，解锁进度 {{ currentBadge?.progress }}%</p>
        </div>

        <div class="detail-share" v-if="currentBadge?.unlocked">
          <el-button type="primary" @click="shareBadge">
            <el-icon><Share /></el-icon>
            分享成就
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Lock,
  Sunny,
  Calendar,
  Check,
  CircleCheck,
  Share
} from '@element-plus/icons-vue'

const activeTab = ref('all')
const showBadgeDetail = ref(false)
const currentBadge = ref(null)

const achievements = ref([
  {
    id: 1,
    name: '初学者',
    description: '完成首次手语学习',
    icon: 'https://picsum.photos/100/100?random=1',
    category: 'learning',
    unlocked: true,
    unlockedAt: '2026-03-15',
    isNew: false,
    progress: 100,
    requirements: ['完成第一个词汇的学习']
  },
  {
    id: 2,
    name: '坚持不懈',
    description: '连续学习7天',
    icon: 'https://picsum.photos/100/100?random=2',
    category: 'streak',
    unlocked: true,
    unlockedAt: '2026-03-22',
    isNew: false,
    progress: 100,
    requirements: ['连续签到学习7天']
  },
  {
    id: 3,
    name: '词汇达人',
    description: '学习100个手语词汇',
    icon: 'https://picsum.photos/100/100?random=3',
    category: 'learning',
    unlocked: true,
    unlockedAt: '2026-04-10',
    isNew: false,
    progress: 100,
    requirements: ['学习100个词汇']
  },
  {
    id: 4,
    name: '实践先锋',
    description: '完成50次摄像头练习',
    icon: 'https://picsum.photos/100/100?random=4',
    category: 'practice',
    unlocked: true,
    unlockedAt: '2026-04-18',
    isNew: false,
    progress: 100,
    requirements: ['完成50次摄像头练习']
  },
  {
    id: 5,
    name: '勤奋学者',
    description: '累计学习30天',
    icon: 'https://picsum.photos/100/100?random=5',
    category: 'streak',
    unlocked: false,
    unlockedAt: '',
    isNew: false,
    progress: 75,
    requirements: ['累计学习30天']
  },
  {
    id: 6,
    name: '手语专家',
    description: '学习500个手语词汇',
    icon: 'https://picsum.photos/100/100?random=6',
    category: 'learning',
    unlocked: false,
    unlockedAt: '',
    isNew: false,
    progress: 31,
    requirements: ['学习500个词汇']
  },
  {
    id: 7,
    name: '社区活跃',
    description: '发布20条动态',
    icon: 'https://picsum.photos/100/100?random=7',
    category: 'social',
    unlocked: false,
    unlockedAt: '',
    isNew: false,
    progress: 40,
    requirements: ['发布20条动态']
  },
  {
    id: 8,
    name: '人气之星',
    description: '获得100个赞',
    icon: 'https://picsum.photos/100/100?random=8',
    category: 'social',
    unlocked: false,
    unlockedAt: '',
    isNew: false,
    progress: 85,
    requirements: ['动态获得100个赞']
  },
  {
    id: 9,
    name: '全能选手',
    description: '解锁所有基础成就',
    icon: 'https://picsum.photos/100/100?random=9',
    category: 'special',
    unlocked: false,
    unlockedAt: '',
    isNew: false,
    progress: 60,
    requirements: ['解锁所有分类的基础成就']
  },
  {
    id: 10,
    name: '月度之星',
    description: '本月学习天数排名前10',
    icon: 'https://picsum.photos/100/100?random=10',
    category: 'special',
    unlocked: false,
    unlockedAt: '',
    isNew: true,
    progress: 0,
    requirements: ['本月学习天数达到30天']
  },
  {
    id: 11,
    name: '审核达人',
    description: '审核通过10个视频',
    icon: 'https://picsum.photos/100/100?random=11',
    category: 'contribution',
    unlocked: false,
    unlockedAt: '',
    isNew: false,
    progress: 30,
    requirements: ['提交并审核通过10个视频']
  },
  {
    id: 12,
    name: '传播大使',
    description: '邀请5位好友加入',
    icon: 'https://picsum.photos/100/100?random=12',
    category: 'social',
    unlocked: false,
    unlockedAt: '',
    isNew: false,
    progress: 20,
    requirements: ['成功邀请5位好友注册']
  }
])

const filteredAchievements = computed(() => {
  switch (activeTab.value) {
    case 'unlocked':
      return achievements.value.filter(a => a.unlocked)
    case 'in-progress':
      return achievements.value.filter(a => !a.unlocked && a.progress > 0)
    case 'locked':
      return achievements.value.filter(a => !a.unlocked && a.progress === 0)
    default:
      return achievements.value
  }
})

const unlockedCount = computed(() =>
  achievements.value.filter(a => a.unlocked).length
)

const totalCount = computed(() => achievements.value.length)

const completionRate = computed(() =>
  Math.round((unlockedCount.value / totalCount.value) * 100)
)

function viewBadge(badge) {
  currentBadge.value = badge
  showBadgeDetail.value = true
}

function shareBadge() {
  ElMessage.success('分享链接已复制到剪贴板')
}

async function loadAchievements() {
  try {
    const res = await achievementApi.getList()
    if (res.data) {
      achievements.value = res.data
    }
  } catch (error) {
    // Use mock data
  }
}

onMounted(() => {
  loadAchievements()
})
</script>

<style scoped>
.achievements-page {
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

/* Stats Overview */
.stats-overview {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 32px;
  margin-bottom: 32px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #0d0d0d;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #8a8a8a;
}

.stat-divider {
  width: 1px;
  height: 48px;
  background: #e8e8e8;
}

/* Tabs */
.tabs-container {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 0 24px;
  margin-bottom: 32px;
}

/* Achievement Grid */
.achievement-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.achievement-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 180ms ease;
}

.achievement-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.achievement-card.locked {
  background: #fafaf8;
}

.achievement-card.locked .badge-icon img {
  filter: grayscale(1);
  opacity: 0.3;
}

.achievement-card.unlocked:hover {
  border-color: #67c23a;
}

.badge-icon {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
}

.badge-icon img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.locked-icon {
  width: 100%;
  height: 100%;
  background: #e8e8e8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a8a8a;
  font-size: 32px;
}

.new-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 2px 6px;
  background: #f56c6c;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  border-radius: 10px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.badge-info {
  margin-bottom: 12px;
}

.badge-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 6px;
}

.badge-info p {
  font-size: 12px;
  color: #8a8a8a;
  line-height: 1.5;
}

.badge-date {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  color: #67c23a;
}

.badge-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.progress-text {
  font-size: 12px;
  color: #8a8a8a;
}

/* Badge Detail */
.badge-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
}

.detail-icon {
  width: 120px;
  height: 120px;
  margin-bottom: 24px;
}

.detail-icon img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #67c23a;
}

.locked-large {
  width: 100%;
  height: 100%;
  background: #e8e8e8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8a8a8a;
  font-size: 48px;
}

.detail-info {
  text-align: center;
  margin-bottom: 24px;
}

.detail-info h2 {
  font-size: 22px;
  font-weight: 700;
  color: #0d0d0d;
  margin-bottom: 8px;
}

.detail-desc {
  font-size: 14px;
  color: #8a8a8a;
}

.detail-requirements {
  width: 100%;
  background: #fafaf8;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 24px;
}

.detail-requirements h3 {
  font-size: 14px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 12px;
}

.detail-requirements ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.detail-requirements li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #0d0d0d;
  padding: 6px 0;
}

.detail-date {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #67c23a;
  margin-bottom: 24px;
}

.detail-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-progress p {
  font-size: 14px;
  color: #8a8a8a;
}

.detail-share {
  margin-top: 8px;
}

@media (max-width: 1024px) {
  .achievement-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .achievement-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-overview {
    gap: 24px;
  }

  .stat-value {
    font-size: 28px;
  }
}

@media (max-width: 480px) {
  .achievement-grid {
    grid-template-columns: 1fr;
  }
}
</style>
