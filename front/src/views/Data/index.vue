<template>
  <div class="data-page">
    <div class="page-header">
      <h1>学习数据中心</h1>
      <p class="subtitle">全面了解你的学习情况，科学规划学习进度</p>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #e8f5e9">
          <el-icon color="#4caf50"><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalDays }}</span>
          <span class="stat-label">总学习天数</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #e3f2fd">
          <el-icon color="#2196f3"><Collection /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.learnedWords }}</span>
          <span class="stat-label">已学词汇</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #fff3e0">
          <el-icon color="#ff9800"><VideoCamera /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalPractice }}</span>
          <span class="stat-label">累计练习</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background: #fce4ec">
          <el-icon color="#e91e63"><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.streak }}</span>
          <span class="stat-label">连续天数</span>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <!-- 学习日历 (replaces 本周学习活动) -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>学习日历</h3>
          <div class="calendar-nav">
            <el-button
              :class="{ 'active-view': viewMode === 'month' }"
              size="small"
              @click="setViewMode('month')"
            >月</el-button>
            <el-button
              :class="{ 'active-view': viewMode === 'year' }"
              size="small"
              @click="setViewMode('year')"
            >年</el-button>
          </div>
        </div>
        <div class="chart-header calendar-month-nav">
          <el-button text size="small" @click="prevMonth">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <span class="month-label">{{ calendarYear }} 年 {{ calendarMonth + 1 }} 月</span>
          <el-button text size="small" @click="nextMonth">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="calendar-body">
          <div class="calendar-weekdays">
            <span v-for="d in weekdays" :key="d">{{ d }}</span>
          </div>
          <div class="calendar-days">
            <div
              v-for="cell in calendarCells"
              :key="cell.key"
              class="calendar-cell"
              :class="{
                'other-month': !cell.inMonth,
                'has-learning': cell.hasLearning,
                'is-today': cell.isToday
              }"
            >
              <span class="cell-day">{{ cell.day }}</span>
            </div>
          </div>
        </div>
        <div class="calendar-legend">
          <span class="legend-item">
            <span class="legend-block legend-block--empty"></span>
            无学习
          </span>
          <span class="legend-item">
            <span class="legend-block legend-block--active"></span>
            有学习
          </span>
        </div>
      </div>

      <!-- 学习时长趋势 (replaces 学习进度) -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>学习时长趋势（近 7 天）</h3>
        </div>
        <div class="chart-content">
          <div class="line-chart">
            <!-- Y axis -->
            <div class="y-axis">
              <span v-for="label in yAxisLabels" :key="label">{{ label }} 分</span>
            </div>
            <!-- Chart area -->
            <div class="chart-area">
              <!-- Grid lines -->
              <div class="grid-line" style="top: 0%"></div>
              <div class="grid-line" style="top: 33%"></div>
              <div class="grid-line" style="top: 66%"></div>
              <div class="grid-line" style="bottom: 0"></div>
              <!-- Data line -->
              <svg class="chart-svg" viewBox="0 0 700 160" preserveAspectRatio="none">
                <polyline
                  :points="chartLinePoints"
                  fill="none"
                  stroke="#333"
                  stroke-width="2"
                />
                <circle
                  v-for="(pt, i) in chartPoints"
                  :key="i"
                  :cx="pt.x"
                  :cy="pt.y"
                  r="4"
                  fill="#333"
                />
              </svg>
              <!-- Data labels -->
              <div
                v-for="(pt, i) in chartPoints"
                :key="'lbl' + i"
                class="data-label"
                :style="{ left: pt.labelLeft + '%', top: pt.labelTop + '%' }"
              >{{ pt.value }} 分</div>
            </div>
          </div>
          <!-- X axis labels (outside SVG to avoid layout issues) -->
          <div class="x-axis-labels">
            <span
              v-for="(day, i) in durationData"
              :key="i"
            >{{ day.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Ebbinghaus Calendar -->
    <div class="calendar-section">
      <div class="section-header">
        <h3>艾宾浩斯复习日历</h3>
        <div class="calendar-legend">
          <span class="legend-item">
            <span class="legend-dot" style="background: #67c23a"></span>
            已复习
          </span>
          <span class="legend-item">
            <span class="legend-dot" style="background: #e6a23c"></span>
            待复习
          </span>
          <span class="legend-item">
            <span class="legend-dot" style="background: #909399"></span>
            未到时间
          </span>
        </div>
      </div>
      <div class="calendar-grid">
        <div
          v-for="(day, index) in ebbinghausCalendar"
          :key="index"
          class="calendar-day"
          :class="day.status"
        >
          <span class="day-number">{{ day.day }}</span>
          <span class="day-words">{{ day.wordCount }}词</span>
        </div>
      </div>
      <div class="calendar-summary">
        <div class="summary-item">
          <span class="summary-label">今日待复习</span>
          <span class="summary-value">{{ todayReviewCount }} 个</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">本周复习</span>
          <span class="summary-value">{{ weekReviewCount }} 个</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">复习完成率</span>
          <span class="summary-value">{{ reviewCompletionRate }}%</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { statsApi } from '@/api'
import {
  Calendar,
  Collection,
  VideoCamera,
  TrendCharts,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue'

const barChartRef = ref(null)

// Stats - 从API获取
const stats = ref({
  totalDays: 0,
  learnedWords: 0,
  totalPractice: 0,
  streak: 0
})

// Weekly data - 从API获取
const weeklyData = ref([
  { label: '周一', words: 0, practice: 0 },
  { label: '周二', words: 0, practice: 0 },
  { label: '周三', words: 0, practice: 0 },
  { label: '周四', words: 0, practice: 0 },
  { label: '周五', words: 0, practice: 0 },
  { label: '周六', words: 0, practice: 0 },
  { label: '今天', words: 0, practice: 0 }
])

const maxWeeklyValue = computed(() => {
  const max = Math.max(...weeklyData.value.map(d => Math.max(d.words, d.practice)))
  return max || 20
})

// Progress - 从API获取
const progress = ref({
  vocabulary: 0,
  totalVocabulary: 0,
  mastery: 0,
  consistency: 0
})

// Ebbinghaus calendar - 从API获取
const ebbinghausCalendar = ref([])

const todayReviewCount = computed(() => {
  const today = new Date().getDate()
  const day = ebbinghausCalendar.value.find(d => d.day === today)
  return day?.wordCount || 0
})

const weekReviewCount = computed(() => {
  return ebbinghausCalendar.value
    .filter(d => d.day <= 7)
    .reduce((sum, d) => sum + d.wordCount, 0)
})

const reviewCompletionRate = computed(() => {
  const completed = ebbinghausCalendar.value.filter(d => d.status === 'completed').length
  const total = ebbinghausCalendar.value.filter(d => d.status !== 'future').length
  return total > 0 ? Math.round((completed / total) * 100) : 0
})

// Skills - 从API获取
// 已移除

// ============ 学习日历 ============
const today = new Date()
const calendarYear = ref(today.getFullYear())
const calendarMonth = ref(today.getMonth())
const viewMode = ref('month')
const calendarData = ref({}) // { "1": { hasLearning, wordsCount, minutes }, ... }

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

function prevMonth() {
  if (calendarMonth.value === 0) {
    calendarMonth.value = 11
    calendarYear.value--
  } else {
    calendarMonth.value--
  }
  loadCalendarData()
}

function nextMonth() {
  if (calendarMonth.value === 11) {
    calendarMonth.value = 0
    calendarYear.value++
  } else {
    calendarMonth.value++
  }
  loadCalendarData()
}

function setViewMode(mode) {
  viewMode.value = mode
}

async function loadCalendarData() {
  try {
    const res = await statsApi.getCalendar(calendarYear.value, calendarMonth.value + 1)
    if (res.data && res.data.days) {
      calendarData.value = res.data.days
    }
  } catch (e) {
    console.error('加载日历数据失败:', e)
  }
}

const calendarCells = computed(() => {
  const year = calendarYear.value
  const month = calendarMonth.value
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = []

  // Fill leading empty cells
  for (let i = 0; i < firstDay; i++) {
    const prevDate = new Date(year, month, -firstDay + i + 1)
    cells.push({
      key: `prev-${i}`,
      day: prevDate.getDate(),
      inMonth: false,
      hasLearning: false,
      isToday: false
    })
  }

  // Fill days of month
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const dayData = calendarData.value[String(d)] || {}
    cells.push({
      key: dateStr,
      day: d,
      inMonth: true,
      hasLearning: dayData.has_learning || false,
      isToday: dateStr === todayStr
    })
  }

  return cells
})

// ============ 学习时长趋势 ============
const durationData = ref([])

const maxDuration = computed(() => {
  const max = Math.max(...durationData.value.map(d => d.value), 0)
  if (max === 0) return 30
  if (max <= 15) return 15
  if (max <= 30) return 30
  if (max <= 60) return 60
  return Math.ceil(max / 30) * 30
})

const yAxisLabels = computed(() => {
  const max = maxDuration.value
  if (max <= 15) return [15, 10, 5, 0]
  if (max <= 30) return [30, 20, 10, 0]
  if (max <= 60) return [60, 45, 30, 15, 0]
  return [max, Math.round(max * 0.75), Math.round(max * 0.5), Math.round(max * 0.25), 0]
})

const chartPoints = computed(() => {
  const maxVal = maxDuration.value || 1
  const W = 700
  const H = 160
  return durationData.value.map((d, i) => {
    const pct = d.value / maxVal
    const x = (i / Math.max(durationData.value.length - 1, 1)) * W
    const y = H - (pct * H)
    return {
      x,
      y,
      labelLeft: (x / W) * 100,
      labelTop: Math.max((y / H) * 100 - 8, 0),
      value: d.value
    }
  })
})

const chartLinePoints = computed(() => {
  return chartPoints.value.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
})

async function loadData() {
  try {
    // 并行获取多个API数据
    const [overviewRes, chartRes] = await Promise.all([
      statsApi.getOverview(),
      statsApi.getChart('week')
    ])

    // 处理概览数据
    if (overviewRes.data) {
      const data = overviewRes.data
      stats.value = {
        totalDays: data.total_days || 0,
        learnedWords: data.learned_words || 0,
        totalPractice: data.total_practice || 0,
        streak: data.streak_days || 0
      }
      // vocabulary_progress 和 consistency 在 get_overview 中没有，用 learned_words 作为参考
      progress.value = {
        vocabulary: Math.round((data.learned_words / (data.total_words || 1)) * 100),
        totalVocabulary: data.total_words || 0,
        mastery: data.mastery_rate || 0,
        consistency: Math.min(Math.round((data.streak_days || 0) * 10), 100)
      }
    }

    // 处理图表数据（周趋势）
    if (chartRes.data) {
      const chartData = chartRes.data
      // 更新每周数据
      weeklyData.value = chartData.map((item, idx) => ({
        label: ['周一', '周二', '周三', '周四', '周五', '周六', '今天'][idx] || `第${idx + 1}天`,
        words: item.words_count || 0,
        practice: item.practice_count || 0
      }))
      // 更新时长趋势数据
      durationData.value = chartData.map(item => {
        const d = new Date(item.date)
        const mm = d.getMonth() + 1
        const dd = d.getDate()
        return {
          label: `${mm}/${dd}`,
          value: item.minutes || 0
        }
      })
    }

    // 加载学习日历数据
    await loadCalendarData()

  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败，请刷新重试')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px 80px;
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
  grid-template-columns: repeat(4, 1fr);
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

/* Charts Section */
.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #8a8a8a;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

/* Bar Chart */
.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 200px;
  padding-top: 20px;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.bars {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 150px;
}

.bar {
  width: 24px;
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: height 300ms ease;
}

.bar-learn {
  background: #333;
}

.bar-practice {
  background: #555;
}

.bar-value {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: #8a8a8a;
}

.bar-label {
  font-size: 12px;
  color: #8a8a8a;
}

/* Progress Charts */
.progress-charts {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.progress-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.progress-value {
  font-size: 24px;
  font-weight: 700;
  color: #0d0d0d;
  display: block;
}

.progress-label {
  font-size: 12px;
  color: #8a8a8a;
}

.progress-desc {
  font-size: 12px;
  color: #8a8a8a;
}

/* ============ 学习日历 ============ */
.calendar-nav {
  display: flex;
  gap: 4px;

  .el-button {
    border-color: #ccc;
    color: #333;
    font-size: 12px;
    padding: 4px 10px;

    &.active-view {
      background: #333;
      border-color: #333;
      color: #fff;
    }
  }
}

.calendar-month-nav {
  margin-bottom: 16px;
  margin-top: 8px;

  .el-button {
    color: #333;
    border: none;
    background: none;

    &:hover {
      color: #000;
    }
  }

  .month-label {
    font-size: 15px;
    font-weight: 600;
    color: #0d0d0d;
  }
}

.calendar-body {
  margin-bottom: 16px;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 8px;

  span {
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    color: #0d0d0d;
    padding: 4px 0;
  }
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: #fff;
  border: 1px solid #e0e0e0;

  &.other-month {
    .cell-day {
      color: #ccc;
    }
  }

  &.has-learning {
    background: #333;
    border-color: #333;

    .cell-day {
      color: #fff;
    }
  }

  &.is-today {
    border-color: #333;
    border-width: 2px;
  }
}

.cell-day {
  font-size: 13px;
  font-weight: 500;
  color: #0d0d0d;
}

.calendar-legend {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.legend-block {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid #e0e0e0;
  vertical-align: middle;
  margin-right: 6px;

  &.legend-block--empty {
    background: #fff;
  }

  &.legend-block--active {
    background: #333;
    border-color: #333;
  }
}

/* ============ 学习时长趋势 ============ */
.chart-content {
  display: flex;
  flex-direction: column;
}

.line-chart {
  position: relative;
  display: flex;
  padding-left: 36px;
  height: 180px;
}

.y-axis {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 24px;
  width: 36px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  padding-right: 8px;

  span {
    font-size: 11px;
    color: #555;
    line-height: 1;
  }
}

.chart-area {
  flex: 1;
  position: relative;
  border-left: 1px solid #aaa;
  border-bottom: 1px solid #aaa;
}

.grid-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  background: #e0e0e0;
  border-top: 1px dashed #e0e0e0;
}

.chart-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.data-label {
  position: absolute;
  transform: translateX(-50%);
  font-size: 10px;
  color: #0d0d0d;
  white-space: nowrap;
  pointer-events: none;
}

.x-axis-labels {
  display: flex;
  justify-content: space-between;
  padding-left: 36px;
  margin-top: 6px;

  span {
    font-size: 11px;
    color: #555;
  }
}

/* Calendar Section */
.calendar-section {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0d0d0d;
}

.calendar-legend {
  display: flex;
  gap: 16px;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 8px;
  margin-bottom: 24px;
}

.calendar-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border-radius: 8px;
  background: #fafaf8;
  transition: all 180ms ease;
}

.calendar-day.completed {
  background: #e8f5e9;
}

.calendar-day.pending {
  background: #fff3e0;
}

.calendar-day.future {
  background: #f5f5f5;
  opacity: 0.5;
}

.day-number {
  font-size: 14px;
  font-weight: 600;
  color: #0d0d0d;
  margin-bottom: 4px;
}

.day-words {
  font-size: 10px;
  color: #8a8a8a;
}

.calendar-summary {
  display: flex;
  justify-content: space-around;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-label {
  font-size: 12px;
  color: #8a8a8a;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #0d0d0d;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-section {
    grid-template-columns: 1fr;
  }

  .calendar-grid {
    grid-template-columns: repeat(7, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .calendar-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
