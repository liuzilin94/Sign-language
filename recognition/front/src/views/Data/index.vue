<template>
  <div class="data-page">
    <div class="page-header">
      <h2>学习数据中心</h2>
      <p>全面了解您的学习进度和效果</p>
    </div>
    
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ totalHours }}</span>
          <span class="stat-label">累计学习时长(小时)</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <el-icon><Reading /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ learnedWords }}</span>
          <span class="stat-label">已学词汇</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ masteryRate }}%</span>
          <span class="stat-label">掌握率</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
          <el-icon><Medal /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ currentLevel }}</span>
          <span class="stat-label">当前等级</span>
        </div>
      </div>
    </div>
    
    <div class="charts-grid">
      <div class="chart-card calendar">
        <h3>学习日历</h3>
        <div class="calendar-grid">
          <div class="calendar-header">
            <span v-for="day in weekDays" :key="day">{{ day }}</span>
          </div>
          <div class="calendar-body">
            <div
              v-for="(day, index) in calendarData"
              :key="index"
              class="calendar-day"
              :class="{ active: day.active, hasData: day.minutes > 0 }"
              :style="{ opacity: day.minutes > 0 ? (day.minutes / maxDayMinutes * 0.8 + 0.2) : 0.3 }"
            >
              {{ day.date }}
            </div>
          </div>
        </div>
        <div class="calendar-legend">
          <span class="legend-item">
            <span class="legend-dot light"></span>
            无学习
          </span>
          <span class="legend-item">
            <span class="legend-dot dark"></span>
            有学习
          </span>
        </div>
      </div>

      <div class="chart-card line-chart">
        <h3>学习时长趋势</h3>
        <div class="chart-container">
          <div class="line-chart-visual">
            <svg viewBox="0 0 400 150" class="chart-svg">
              <polyline
                :points="linePoints"
                fill="none"
                stroke="#667eea"
                stroke-width="2"
              />
              <circle
                v-for="(point, index) in linePointsArray"
                :key="index"
                :cx="point.x"
                :cy="point.y"
                r="4"
                fill="#667eea"
              />
            </svg>
            <div class="x-labels">
              <span v-for="label in monthLabels" :key="label">{{ label }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card radar-chart">
        <h3>综合能力雷达图</h3>
        <div class="chart-container">
          <div class="radar-chart-visual">
            <svg viewBox="0 0 200 200" class="radar-svg">
              <polygon
                points="100,20 180,80 150,170 50,170 20,80"
                fill="none"
                stroke="#e4e7ed"
                stroke-width="1"
              />
              <polygon
                points="100,56 140,92 125,152 75,152 60,92"
                fill="none"
                stroke="#e4e7ed"
                stroke-width="1"
              />
              <polygon
                points="100,92 100,92 100,134 100,134 100,92"
                fill="none"
                stroke="#e4e7ed"
                stroke-width="1"
              />
              <polygon
                :points="radarPoints"
                fill="rgba(102, 126, 234, 0.3)"
                stroke="#667eea"
                stroke-width="2"
              />
            </svg>
            <div class="radar-labels">
              <span>日常</span>
              <span>社会</span>
              <span>情感</span>
              <span>生活</span>
              <span>科技</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card pie-chart">
        <h3>词汇掌握情况</h3>
        <div class="chart-container">
          <div class="ring-chart">
            <svg viewBox="0 0 200 200" class="ring-svg">
              <circle cx="100" cy="100" r="70" fill="none" stroke="#f5f7fa" stroke-width="20" />
              <circle
                cx="100" cy="100" r="70"
                fill="none"
                stroke="#667eea"
                stroke-width="20"
                :stroke-dasharray="`${masteryRate * 4.4} 440`"
                transform="rotate(-90 100 100)"
              />
              <circle
                cx="100" cy="100" r="70"
                fill="none"
                stroke="#f093fb"
                stroke-width="20"
                :stroke-dasharray="`${(100 - masteryRate) * 4.4} 440`"
                :stroke-dashoffset="`${-masteryRate * 4.4}`"
                transform="rotate(-90 100 100)"
              />
            </svg>
            <div class="ring-center">
              <span class="percent">{{ masteryRate }}%</span>
              <span class="label">掌握率</span>
            </div>
          </div>
          <div class="ring-legend">
            <div class="legend-item">
              <span class="dot" style="background: #667eea;"></span>
              <span>已掌握</span>
              <span class="value">{{ learnedWords * masteryRate / 100 }}</span>
            </div>
            <div class="legend-item">
              <span class="dot" style="background: #f093fb;"></span>
              <span>学习中</span>
              <span class="value">{{ learnedWords * (100 - masteryRate) / 100 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="ranking-section">
      <h3>学习排行榜</h3>
      <div class="ranking-list">
        <div
          v-for="(user, index) in rankingList"
          :key="index"
          class="ranking-item"
          :class="{ highlight: user.isMe }"
        >
          <span class="rank" :class="{ top: index < 3 }">{{ index + 1 }}</span>
          <img :src="user.avatar" alt="" class="avatar" />
          <span class="name">{{ user.name }}</span>
          <span class="hours">{{ user.hours }} 小时</span>
          <span class="badge">{{ user.badge }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Timer, Reading, Star, Medal } from '@element-plus/icons-vue'
import { useLearnStore } from '@/store'

const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjM1IiByPSIyNSIgZmlsbD0iI2Q0ZDRkNCIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNzUiIHI9IjMwIiBmaWxsPSIjZDRkNGQ0Ii8+PC9zdmc+'

const learnStore = useLearnStore()

const totalHours = ref(25.5)
const learnedWords = ref(48)
const masteryRate = ref(65)
const currentLevel = ref(5)
const maxDayMinutes = ref(60)

const weekDays = ['日', '一', '二', '三', '四', '五', '六']

const calendarData = computed(() => {
  const days = []
  const today = new Date()
  for (let i = 29; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    days.push({
      date: date.getDate(),
      minutes: Math.random() > 0.3 ? Math.floor(Math.random() * 60) : 0,
      active: i === 0
    })
  }
  return days
})

const monthLabels = ['1日', '5日', '10日', '15日', '20日', '25日', '30日']

const linePointsArray = computed(() => {
  const points = []
  for (let i = 0; i < 7; i++) {
    const x = 50 + i * 50
    const y = 130 - Math.random() * 100
    points.push({ x, y })
  }
  return points
})

const linePoints = computed(() => {
  return linePointsArray.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ')
})

const radarPoints = computed(() => {
  return '100,35 155,85 130,160 70,160 45,85'
})

const rankingList = ref([
  { name: '手语达人小王', avatar: defaultAvatar, hours: 128, badge: '学习之星', isMe: false },
  { name: '聋人朋友', avatar: defaultAvatar, hours: 95, badge: '手语专家', isMe: false },
  { name: '学习小能手', avatar: defaultAvatar, hours: 78, badge: '进步达人', isMe: true },
  { name: '手语教师', avatar: defaultAvatar, hours: 65, badge: '坚持不懈', isMe: false },
  { name: '新学者', avatar: defaultAvatar, hours: 52, badge: '初露锋芒', isMe: false }
])
</script>

<style scoped lang="scss">
.data-page {
  max-width: 1200px;
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
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
    
    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      
      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        
        .el-icon {
          font-size: 28px;
          color: #fff;
        }
      }
      
      .stat-info {
        display: flex;
        flex-direction: column;
        
        .stat-value {
          font-size: 28px;
          font-weight: bold;
          color: #333;
        }
        
        .stat-label {
          font-size: 14px;
          color: #999;
        }
      }
    }
  }
  
  .charts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 24px;

    .chart-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;

      h3 {
        font-size: 15px;
        color: #333;
        margin-bottom: 16px;
      }

      &.calendar {
        .calendar-grid {
          .calendar-header {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 2px;
            margin-bottom: 6px;

            span {
              text-align: center;
              font-size: 11px;
              color: #999;
            }
          }

          .calendar-body {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 2px;

            .calendar-day {
              aspect-ratio: 1;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 10px;
              border-radius: 2px;
              background: #f5f7fa;
              color: #666;

              &.active {
                background: #667eea;
                color: #fff;
              }

              &.hasData {
                background: #667eea;
                color: #fff;
              }
            }
          }
        }

        .calendar-legend {
          display: flex;
          gap: 16px;
          margin-top: 12px;

          .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: #999;

            .legend-dot {
              width: 10px;
              height: 10px;
              border-radius: 2px;

              &.light {
                background: #f5f7fa;
              }

              &.dark {
                background: #667eea;
              }
            }
          }
        }
      }

      &.line-chart,
      &.pie-chart,
      &.radar-chart {
        .chart-container {
          height: 180px;
        }
      }
    }
  }
  
  .line-chart-visual {
    width: 100%;
    height: 100%;
    position: relative;
    
    .chart-svg {
      width: 100%;
      height: 150px;
    }
    
    .x-labels {
      display: flex;
      justify-content: space-between;
      padding: 0 20px;
      
      span {
        font-size: 12px;
        color: #999;
      }
    }
  }
  
  .ring-chart {
    position: relative;
    width: 200px;
    height: 200px;
    margin: 0 auto;
    
    .ring-svg {
      width: 100%;
      height: 100%;
    }
    
    .ring-center {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      
      .percent {
        display: block;
        font-size: 24px;
        font-weight: bold;
        color: #333;
      }
      
      .label {
        font-size: 12px;
        color: #999;
      }
    }
  }
  
  .ring-legend {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      font-size: 14px;
      
      .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
      }
      
      .value {
        margin-left: auto;
        font-weight: bold;
        color: #333;
      }
    }
  }
  
  .radar-chart-visual {
    position: relative;
    width: 200px;
    height: 200px;
    margin: 0 auto;
    
    .radar-svg {
      width: 100%;
      height: 100%;
    }
    
    .radar-labels {
      position: absolute;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      justify-content: space-between;
      width: 180px;
      
      span {
        font-size: 12px;
        color: #666;
        
        &:nth-child(2) {
          position: absolute;
          right: -10px;
          top: 50%;
        }
        
        &:nth-child(3) {
          position: absolute;
          right: 0;
          bottom: 10px;
        }
        
        &:nth-child(4) {
          position: absolute;
          left: 0;
          bottom: 10px;
        }
        
        &:nth-child(5) {
          position: absolute;
          left: -10px;
          top: 50%;
        }
      }
    }
  }
  
  .ranking-section {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    
    h3 {
      font-size: 16px;
      color: #333;
      margin-bottom: 20px;
    }
    
    .ranking-list {
      .ranking-item {
        display: flex;
        align-items: center;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        background: #f9fafb;
        
        &.highlight {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: #fff;
        }
        
        .rank {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background: #e4e7ed;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          margin-right: 12px;
          
          &.top {
            background: #f56c6c;
            color: #fff;
          }
        }
        
        .avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #ddd;
          margin-right: 12px;
        }
        
        .name {
          flex: 1;
          font-weight: bold;
        }
        
        .hours {
          margin-right: 16px;
          color: inherit;
          opacity: 0.8;
        }
        
        .badge {
          padding: 4px 12px;
          background: rgba(255,255,255,0.2);
          border-radius: 12px;
          font-size: 12px;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .data-page {
    .charts-grid {
      grid-template-columns: 1fr;
      
      .chart-card.calendar {
        grid-column: span 1;
      }
    }
  }
}
</style>
