<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2>学习任务</h2>
      <p>艾宾浩斯复习法，科学对抗遗忘</p>
    </div>
    
    <div class="stats-overview">
      <div class="stat-card today">
        <div class="stat-main">
          <el-icon><Calendar /></el-icon>
          <div class="stat-info">
            <span class="stat-label">今日待复习</span>
            <span class="stat-value">{{ reviewWords.length }} 个</span>
          </div>
        </div>
        <el-button type="primary" size="large" @click="startReview" :disabled="reviewWords.length === 0">
          开始复习
        </el-button>
      </div>
      
      <div class="stat-row">
        <div class="mini-stat">
          <span class="value">{{ completedToday }}</span>
          <span class="label">今日完成</span>
        </div>
        <div class="mini-stat">
          <span class="value">{{ streakDays }}</span>
          <span class="label">连续天数</span>
        </div>
        <div class="mini-stat">
          <span class="value">{{ totalLearned }}</span>
          <span class="label">已学词汇</span>
        </div>
      </div>
    </div>
    
    <div class="review-section" v-if="reviewWords.length > 0">
      <h3>待复习词汇</h3>
      <div class="review-list">
        <div
          v-for="word in reviewWords"
          :key="word.id"
          class="review-item"
          @click="openWordDetail(word.id)"
        >
          <div class="word-info">
            <span class="word-text">{{ word.word }}</span>
            <span class="word-hint">{{ word.hint }}</span>
          </div>
          <div class="review-status" :class="{ done: word.reviewed }">
            <el-icon v-if="word.reviewed"><CircleCheck /></el-icon>
            <el-icon v-else><Clock /></el-icon>
          </div>
        </div>
      </div>
    </div>
    
    <div class="daily-tasks">
      <h3>每日任务</h3>
      <div class="task-list">
        <div
          v-for="task in dailyTasks"
          :key="task.id"
          class="task-item"
          :class="{ completed: task.completed }"
        >
          <div class="task-icon">
            <el-icon><component :is="task.icon" /></el-icon>
          </div>
          <div class="task-info">
            <span class="task-name">{{ task.name }}</span>
            <span class="task-desc">{{ task.desc }}</span>
          </div>
          <div class="task-action">
            <el-tag v-if="task.completed" type="success" size="small">已完成</el-tag>
            <el-button v-else type="primary" size="small" @click="doTask(task)">
              {{ task.actionText }}
            </el-button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="study-time">
      <h3>学习时长统计</h3>
      <div class="time-stats">
        <div class="time-item">
          <span class="time-value">{{ todayMinutes }}</span>
          <span class="time-label">今日(分钟)</span>
        </div>
        <div class="time-item">
          <span class="time-value">{{ weekMinutes }}</span>
          <span class="time-label">本周(分钟)</span>
        </div>
        <div class="time-item">
          <span class="time-value">{{ monthMinutes }}</span>
          <span class="time-label">本月(分钟)</span>
        </div>
      </div>
      <div class="time-chart">
        <div class="chart-bars">
          <div
            v-for="(day, index) in weekDays"
            :key="index"
            class="bar-item"
          >
            <div class="bar" :style="{ height: (day.minutes / maxMinutes * 100) + '%' }"></div>
            <span class="bar-label">{{ day.label }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <el-dialog v-model="reviewDialogVisible" title="复习确认" width="400px">
      <p>确定已完成今日复习吗？</p>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmReview">确认完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Calendar, CircleCheck, Clock } from '@element-plus/icons-vue'
import { useLearnStore } from '@/store'
import { useWordDetailStore } from '@/store'

const learnStore = useLearnStore()
const { openWordDetail } = useWordDetailStore()

const reviewDialogVisible = ref(false)

const reviewWords = ref([
  { id: 1, word: '你好', hint: '基础问候手势', reviewed: false },
  { id: 2, word: '谢谢', hint: '表示感谢', reviewed: false },
  { id: 3, word: '再见', hint: '告别手势', reviewed: false },
  { id: 4, word: '对不起', hint: '道歉手势', reviewed: false },
  { id: 5, word: '请', hint: '请求手势', reviewed: false }
])

const dailyTasks = ref([
  { id: 1, name: '每日一学', desc: '学习一个新词汇', icon: 'Plus', actionText: '去学习', completed: true },
  { id: 2, name: '复习巩固', desc: '完成今日复习任务', icon: 'Refresh', actionText: '去复习', completed: false },
  { id: 3, name: '练习打卡', desc: '完成一次练习', icon: 'Medal', actionText: '去练习', completed: false },
  { id: 4, name: '分享互动', desc: '点赞或评论社区动态', icon: 'ChatDotRound', actionText: '去社区', completed: true }
])

const weekDays = ref([
  { label: '一', minutes: 25 },
  { label: '二', minutes: 30 },
  { label: '三', minutes: 15 },
  { label: '四', minutes: 40 },
  { label: '五', minutes: 20 },
  { label: '六', minutes: 35 },
  { label: '日', minutes: 10 }
])

const completedToday = computed(() => dailyTasks.value.filter(t => t.completed).length)
const streakDays = ref(7)
const totalLearned = computed(() => learnStore.learnStats.length * 3)
const todayMinutes = computed(() => {
  const today = new Date().toLocaleDateString()
  const stat = learnStore.learnStats.find(s => s.date === today)
  return stat?.minutes || 0
})
const weekMinutes = computed(() => weekDays.value.reduce((sum, d) => sum + d.minutes, 0))
const monthMinutes = ref(320)
const maxMinutes = computed(() => Math.max(...weekDays.value.map(d => d.minutes)))

function startReview() {
  reviewWords.value.forEach(word => {
    word.reviewed = true
  })
  learnStore.recordLearnTime(reviewWords.value.length)
}

function doTask(task) {
  task.completed = true
  if (task.id === 1) {
    window.location.href = '/dictionary'
  } else if (task.id === 2) {
    window.location.href = '/tasks'
  } else if (task.id === 3) {
    window.location.href = '/practice'
  } else if (task.id === 4) {
    window.location.href = '/community'
  }
}

function confirmReview() {
  reviewWords.value.forEach(word => { word.reviewed = true })
  reviewDialogVisible.value = false
}
</script>

<style scoped lang="scss">
.tasks-page {
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
  
  .stats-overview {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 24px;
    color: #fff;
    margin-bottom: 24px;
    
    .stat-card.today {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      .stat-main {
        display: flex;
        align-items: center;
        gap: 16px;
        
        .el-icon {
          font-size: 40px;
        }
        
        .stat-info {
          display: flex;
          flex-direction: column;
          
          .stat-label {
            font-size: 14px;
            opacity: 0.9;
          }
          
          .stat-value {
            font-size: 28px;
            font-weight: bold;
          }
        }
      }
      
      .el-button {
        background: #fff;
        color: #667eea;
        border: none;
        
        &:hover {
          background: rgba(255,255,255,0.9);
        }
      }
    }
    
    .stat-row {
      display: flex;
      gap: 24px;
      
      .mini-stat {
        display: flex;
        flex-direction: column;
        
        .value {
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
  
  .review-section,
  .daily-tasks,
  .study-time {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    
    h3 {
      font-size: 16px;
      color: #333;
      margin-bottom: 16px;
    }
  }
  
  .review-section {
    .review-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      
      .review-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        background: #f9fafb;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.3s;
        
        &:hover {
          background: #f0f2f5;
        }
        
        .word-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
          
          .word-text {
            font-size: 16px;
            font-weight: bold;
            color: #333;
          }
          
          .word-hint {
            font-size: 12px;
            color: #999;
          }
        }
        
        .review-status {
          .el-icon {
            font-size: 24px;
            color: #f56c6c;
          }
          
          &.done .el-icon {
            color: #67c23a;
          }
        }
      }
    }
  }
  
  .daily-tasks {
    .task-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      
      .task-item {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        background: #f9fafb;
        border-radius: 8px;
        transition: all 0.3s;
        
        &.completed {
          opacity: 0.6;
        }
        
        .task-icon {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          
          .el-icon {
            font-size: 22px;
            color: #fff;
          }
        }
        
        .task-info {
          flex: 1;
          display: flex;
          flex-direction: column;
          
          .task-name {
            font-weight: bold;
            color: #333;
          }
          
          .task-desc {
            font-size: 12px;
            color: #999;
          }
        }
      }
    }
  }
  
  .study-time {
    .time-stats {
      display: flex;
      gap: 24px;
      margin-bottom: 24px;
      
      .time-item {
        flex: 1;
        text-align: center;
        padding: 16px;
        background: #f9fafb;
        border-radius: 8px;
        
        .time-value {
          font-size: 24px;
          font-weight: bold;
          color: #667eea;
          display: block;
        }
        
        .time-label {
          font-size: 12px;
          color: #999;
        }
      }
    }
    
    .time-chart {
      height: 150px;
      
      .chart-bars {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        height: 100%;
        padding-top: 20px;
        
        .bar-item {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          height: 100%;
          
          .bar {
            width: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px 4px 0 0;
            transition: height 0.3s;
            max-height: 100px;
          }
          
          .bar-label {
            font-size: 12px;
            color: #999;
            margin-top: 8px;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .tasks-page {
    .stats-overview {
      .stat-card.today {
        flex-direction: column;
        gap: 16px;
        text-align: center;
      }
      
      .stat-row {
        justify-content: space-around;
      }
    }
    
    .study-time .time-stats {
      flex-direction: column;
      gap: 12px;
    }
  }
}
</style>
