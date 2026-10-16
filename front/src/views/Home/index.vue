<template>
  <div class="home-page">

    <!-- Hero Banner Carousel -->
    <section class="hero-carousel">
      <el-carousel height="380px" trigger="hover" indicator-position="outside" :interval="6000">
        <el-carousel-item v-for="(banner, idx) in banners" :key="idx" :style="{ background: banner.bg }">
          <div class="banner-inner">
            <div class="banner-content">
              <span class="banner-tag">{{ banner.tag }}</span>
              <h2 class="banner-title">{{ banner.title }}</h2>
              <p class="banner-desc">{{ banner.desc }}</p>
              <el-button size="large" @click="banner.action">
                {{ banner.cta }}
              </el-button>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </section>

    <div class="home-body">
      <!-- Daily Word -->
      <section class="daily-section">
        <div class="section-header">
          <h2 class="section-title">每日一词</h2>
          <button class="section-refresh" @click="refreshDaily">
            <el-icon><RefreshRight /></el-icon>
            换一换
          </button>
        </div>
        <div class="daily-card-wrapper">
          <div class="daily-card" @click="openWordDetail(dailyWord.id)">
            <div class="daily-word">{{ dailyWord.word }}</div>
            <div class="daily-meta">
              <el-tag size="small">{{ dailyWord.category }}</el-tag>
              <el-tag size="small" type="info">{{ ['入门', '基础', '进阶'][dailyWord.difficulty - 1] }}</el-tag>
            </div>
            <p class="daily-hint">点击查看详细手语演示</p>
          </div>
        </div>
      </section>

      <!-- Science Section -->
      <section class="science-section">
        <div class="section-header">
          <h2 class="section-title">手语科普</h2>
          <router-link to="/science" class="section-link">
            了解更多 <el-icon><ArrowRight /></el-icon>
          </router-link>
        </div>
        <div class="science-grid">
        <div
          v-for="(item, idx) in scienceItems"
          :key="item.title"
          class="science-card"
          @click="idx === 1 ? router.push('/science/7') : router.push('/science')"
        >
            <el-icon class="science-icon"><component :is="item.icon" /></el-icon>
            <div class="science-info">
              <h4>{{ item.title }}</h4>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  RefreshRight,
  Operation, TrendCharts, Document
} from '@element-plus/icons-vue'
import { wordApi } from '@/api'
import { useUserStore } from '@/store/user'
import { useWordDetailStore } from '@/store'

const router = useRouter()
const userStore = useUserStore()
const wordDetailStore = useWordDetailStore()
const { openWordDetail } = wordDetailStore


// Banners
const banners = ref([
  {
    tag: 'INTRODUCTION',
    title: '学习手语，感受无声世界的温暖',
    desc: '让沟通无障碍',
    cta: '开始学习',
    bg: 'linear-gradient(135deg, rgba(13,13,13,0.85), rgba(30,30,30,0.75)), url(/images/cover.jpg) center/cover no-repeat',
    action: () => router.push('/dictionary')
  },
  {
    tag: 'DAILY',
    title: '每日一词，积累点滴进步',
    desc: '科学复习，让手语成为你的第二语言',
    cta: '查看今日',
    bg: 'linear-gradient(135deg, rgba(13,13,13,0.85), rgba(30,30,30,0.75)), url(/images/插图2.png) center/cover no-repeat',
    action: () => document.querySelector('.daily-card')?.scrollIntoView({ behavior: 'smooth' })
  },
  {
    tag: 'COMMUNITY',
    title: '共创方言手语库',
    desc: '汇集全国各地手语差异，贡献你的力量',
    cta: '参与贡献',
    bg: 'linear-gradient(135deg, rgba(13,13,13,0.85), rgba(30,30,30,0.75)), url(/images/插图3.png) center/cover no-repeat',
    action: () => router.push(userStore.isLoggedIn ? '/upload' : '/login')
  }
])

const dailyWord = ref({ word: '你好', category: '基础', difficulty: 1, id: 1 })

const scienceItems = [
  { title: '中国手语发展史', desc: '从民国时期到现代的发展历程', icon: Operation },
  { title: '听障口语者VS手语者', desc: '聋人文化与听障群体的正确理解', icon: TrendCharts },
  { title: '国家通用手语', desc: '国家语言文字规范与推广', icon: Document },
]

onMounted(async () => {
  await loadDailyWord()
})

async function loadDailyWord() {
  try {
    const res = await wordApi.getWords({ page: 1, page_size: 30 })
    if (res.data?.items?.length > 0) {
      const idx = Math.floor(Math.random() * Math.min(res.data.items.length, 8))
      dailyWord.value = res.data.items[idx]
    }
  } catch (e) { console.error(e)   }
}

function refreshDaily() {
  loadDailyWord()
}
</script>

<style scoped lang="scss">
.home-page {
  background: #fafaf8;
}

// ==================== CAROUSEL ====================
.hero-carousel {
  :deep(.el-carousel) {
    .el-carousel__container {
      .el-carousel__item {
        .banner-inner {
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 32px;

          .banner-content {
            max-width: 600px;
            text-align: center;

            .banner-tag {
              font-size: 11px;
              font-weight: 500;
              letter-spacing: 2px;
              color: rgba(255, 255, 255, 0.4);
              text-transform: uppercase;
              display: block;
              margin-bottom: 16px;
            }

            .banner-title {
              font-size: 32px;
              font-weight: 700;
              color: #fff;
              line-height: 1.25;
              letter-spacing: -0.5px;
              margin: 0 0 12px;
            }

            .banner-desc {
              font-size: 15px;
              color: rgba(255, 255, 255, 0.45);
              margin: 0 0 28px;
              line-height: 1.6;
            }

            .el-button {
              background: transparent;
              border: 1px solid rgba(255, 255, 255, 0.25);
              color: #fff;
              border-radius: 6px;
              padding: 10px 28px;
              font-size: 14px;
              font-weight: 450;
              letter-spacing: 0.3px;
              transition: all 180ms ease;

              &:hover {
                background: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.4);
              }
            }
          }
        }
      }
    }

    .el-carousel__indicator {
      padding: 0 4px;

      button {
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
      }

      &.is-active button {
        width: 20px;
        border-radius: 2px;
        background: #fff;
      }
    }
  }
}

// ==================== STATS ====================
.stats-strip {
  padding: 32px 0;
  border-bottom: 1px solid #e8e8e8;

  .stats-inner {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 32px;
    display: flex;
    gap: 48px;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    gap: 3px;

    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: #0d0d0d;
      letter-spacing: -0.5px;
    }

    .stat-label {
      font-size: 13px;
      color: #8a8a8a;
    }
  }
}

// ==================== BODY ====================
.home-body {
  max-width: 1100px;
  margin: 0 auto;
  padding: 48px 32px 80px;
  display: flex;
  flex-direction: column;
  gap: 48px;
}

// ==================== SECTION SHARED ====================
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #0d0d0d;
    letter-spacing: -0.2px;
    margin: 0;
  }

  .section-refresh {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: #8a8a8a;
    transition: color 180ms ease;

    &:hover {
      color: #0d0d0d;
    }
  }

  .section-link {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: #8a8a8a;
    text-decoration: none;
    transition: color 180ms ease;

    &:hover {
      color: #0d0d0d;
    }
  }
}

// ==================== DAILY ====================
.daily-section {
  .daily-card-wrapper {
    display: flex;
    justify-content: center;
  }
}

.daily-card {
  width: 520px;
  padding: 40px 48px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  cursor: pointer;
  transition: all 200ms ease;
  text-align: center;

  &:hover {
    border-color: #c8c8c8;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  }

  .daily-word {
    font-size: 52px;
    font-weight: 700;
    color: #0d0d0d;
    letter-spacing: 8px;
    margin-bottom: 14px;
    text-indent: 8px;
  }

  .daily-meta {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .daily-hint {
    font-size: 12px;
    color: #c8c8c8;
    margin: 0;
  }
}

// ==================== FEATURED ====================
.featured-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.featured-card {
  padding: 24px 20px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 200ms ease;

  &:hover {
    border-color: #c8c8c8;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  }

  .featured-word {
    font-size: 22px;
    font-weight: 600;
    color: #0d0d0d;
    margin-bottom: 10px;
  }

  .featured-tags {
    display: flex;
    gap: 6px;
  }
}

// ==================== SCIENCE ====================
.science-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.science-card {
  padding: 24px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 200ms ease;
  display: flex;
  align-items: flex-start;
  gap: 16px;

  &:hover {
    border-color: #c8c8c8;
    transform: translateY(-1px);
  }

  .science-icon {
    font-size: 22px;
    color: #8a8a8a;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .science-info {
    h4 {
      font-size: 15px;
      font-weight: 600;
      color: #0d0d0d;
      margin: 0 0 5px;
    }

    p {
      font-size: 13px;
      color: #8a8a8a;
      margin: 0;
      line-height: 1.5;
    }
  }
}

// ==================== RESPONSIVE ====================
@media (max-width: 768px) {
  .hero-carousel {
    :deep(.el-carousel) {
      .el-carousel__container {
        .el-carousel__item {
          .banner-inner {
            padding: 0 20px;

            .banner-content {
              .banner-title {
                font-size: 22px;
              }

              .banner-desc {
                font-size: 13px;
              }
            }
          }
        }
      }
    }
  }

  .stats-strip {
    .stats-inner {
      padding: 0 20px;
      gap: 32px;
      flex-wrap: wrap;
    }
  }

  .home-body {
    padding: 32px 20px 60px;
    gap: 40px;
  }

  .featured-grid,
  .science-grid {
    grid-template-columns: 1fr;
  }
}
</style>
