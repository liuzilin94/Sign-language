<template>
  <div class="home-page">
    <!-- 轮播图区域 -->
    <div class="carousel-section">
      <el-carousel height="380px" trigger="hover" indicator-position="outside" :interval="5000">
        <el-carousel-item v-for="(banner, idx) in banners" :key="idx" :style="{ background: banner.bg }">
          <div class="banner-content">
            <div class="banner-text">
              <h2>{{ banner.title }}</h2>
              <p>{{ banner.subtitle }}</p>
              <el-button type="primary" round @click="handleBannerClick(banner)">
                {{ banner.cta }}
              </el-button>
            </div>
            <div class="banner-illustration">
              <span class="banner-icon">{{ banner.icon }}</span>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>

    <div class="main-content">
      <!-- 每日一词 -->
      <div class="daily-section">
        <div class="section-header">
          <h3>每日一词</h3>
          <span class="refresh-btn" @click="refreshDaily">换一换</span>
        </div>
        <div class="daily-card">
          <div class="daily-word">{{ dailyWord.word }}</div>
          <div class="daily-tags">
            <el-tag size="small">{{ dailyWord.category }}</el-tag>
            <el-tag size="small" type="info">{{ ['入门', '基础', '进阶'][dailyWord.difficulty - 1] }}</el-tag>
          </div>
          <p class="daily-hint">点击下方卡片查看详细手语演示</p>
          <div class="daily-actions">
            <el-button type="primary" @click="openWordDetail(dailyWord.id)">查看详情</el-button>
            <el-button @click="$router.push('/dictionary')">进入词典</el-button>
          </div>
        </div>
      </div>

      <!-- 精选词条轮播 -->
      <div class="featured-section">
        <div class="section-header">
          <h3>精选词条</h3>
          <el-button text @click="$router.push('/dictionary')">查看更多 →</el-button>
        </div>
        <div class="featured-carousel">
          <el-carousel :interval="4000" type="card" height="220px">
            <el-carousel-item v-for="word in featuredWords" :key="word.id">
              <div class="featured-card" @click="openWordDetail(word.id)">
                <div class="featured-word">{{ word.word }}</div>
                <div class="featured-tags">
                  <el-tag size="small" type="warning">{{ word.category }}</el-tag>
                  <el-tag size="small">{{ word.scene }}</el-tag>
                </div>
                <div class="featured-meta">
                  <span class="difficulty">
                    <el-icon><Star /></el-icon>
                    {{ ['入门', '基础', '进阶'][word.difficulty - 1] }}
                  </span>
                </div>
              </div>
            </el-carousel-item>
          </el-carousel>
        </div>
      </div>

      <!-- 手语���普 -->
      <div class="science-section">
        <div class="section-header">
          <h3>手语科普</h3>
          <el-button text @click="$router.push('/science')">了解更多 →</el-button>
        </div>
        <div class="science-grid">
          <div
            v-for="item in scienceItems"
            :key="item.title"
            class="science-card"
            @click="$router.push('/science')"
          >
            <div class="science-icon" :style="{ background: item.color }">{{ item.icon }}</div>
            <div class="science-info">
              <h4>{{ item.title }}</h4>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Star } from '@element-plus/icons-vue'
import { wordApi } from '@/api'
import { useWordDetailStore } from '@/store'

const router = useRouter()
const wordDetailStore = useWordDetailStore()
const { openWordDetail } = wordDetailStore

const banners = ref([
  {
    title: '学习手语，感受无声世界的温暖',
    subtitle: '掌言手语 — 专业的中国手语学习平台',
    cta: '开始学习',
    icon: '🖐',
    bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    action: () => router.push('/dictionary')
  },
  {
    title: '每日一词，积累点滴进步',
    subtitle: '坚持学习，让手语成为你的第二语言',
    cta: '查看今日',
    icon: '📚',
    bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    action: () => refreshDaily()
  },
  {
    title: '共创方言手语库',
    subtitle: '汇集全国各地手语差异，让沟通无障碍',
    cta: '参与贡献',
    icon: '🌍',
    bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    action: () => router.push('/upload')
  }
])

const featuredWords = ref([
  { id: 1, word: '你好', category: '基础', scene: '日常问候', difficulty: 1 },
  { id: 2, word: '谢谢', category: '基础', scene: '日常用语', difficulty: 1 },
  { id: 3, word: '再见', category: '基础', scene: '日常用语', difficulty: 1 },
  { id: 4, word: '对不起', category: '基础', scene: '日常用语', difficulty: 2 },
  { id: 5, word: '家庭', category: '生活', scene: '家庭', difficulty: 2 },
  { id: 6, word: '吃饭', category: '生活', scene: '饮食', difficulty: 1 }
])

const scienceItems = ref([
  { title: '手语历史', desc: '了解中国手语的起源与发展', icon: '📜', color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { title: '手语方言', desc: '各地手语表达差异一览', icon: '🗣', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { title: '聋人文化', desc: '走进聋人社区，感受手语之美', icon: '👥', color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }
])

const dailyWord = ref({ word: '你好', category: '基础', difficulty: 1, id: 1 })
const allWords = [
  { id: 1, word: '你好', category: '基础', difficulty: 1 },
  { id: 2, word: '谢谢', category: '基础', difficulty: 1 },
  { id: 3, word: '再见', category: '基础', difficulty: 1 },
  { id: 4, word: '对不起', category: '基础', difficulty: 2 },
  { id: 5, word: '请', category: '基础', difficulty: 2 },
  { id: 6, word: '家庭', category: '生活', difficulty: 2 },
  { id: 7, word: '爸爸', category: '生活', difficulty: 1 },
  { id: 8, word: '妈妈', category: '生活', difficulty: 1 },
  { id: 9, word: '吃饭', category: '生活', difficulty: 2 },
  { id: 10, word: '喝水', category: '生活', difficulty: 1 }
]

onMounted(() => {
  refreshDaily()
})

function handleBannerClick(banner) {
  banner.action()
}

function refreshDaily() {
  const randomWord = allWords[Math.floor(Math.random() * allWords.length)]
  dailyWord.value = randomWord
}
</script>

<style scoped lang="scss">
.home-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 70px;

  .carousel-section {
    :deep(.el-carousel) {
      .el-carousel__container {
        .el-carousel__item {
          border-radius: 0;

          .banner-content {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 80px;
            color: #fff;

            .banner-text {
              h2 {
                font-size: 36px;
                font-weight: bold;
                margin-bottom: 12px;
              }
              p {
                font-size: 18px;
                opacity: 0.9;
                margin-bottom: 24px;
              }
              .el-button {
                background: rgba(255,255,255,0.2);
                border: 2px solid rgba(255,255,255,0.5);
                backdrop-filter: blur(4px);
                &:hover {
                  background: rgba(255,255,255,0.3);
                }
              }
            }

            .banner-illustration {
              .banner-icon {
                font-size: 120px;
                opacity: 0.3;
              }
            }
          }
        }
      }

      .el-carousel__indicators--outside {
        .el-carousel__indicator {
          button {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(255,255,255,0.5);
          }
          &.is-active button {
            background: #fff;
            width: 24px;
            border-radius: 4px;
          }
        }
      }
    }
  }

  .main-content {
    max-width: 1000px;
    margin: 0 auto;
    padding: 30px 20px;
    display: flex;
    flex-direction: column;
    gap: 32px;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      font-size: 20px;
      font-weight: bold;
      color: #333;
    }

    .refresh-btn {
      font-size: 13px;
      color: #667eea;
      cursor: pointer;
      &:hover { text-decoration: underline; }
    }
  }

  .daily-section {
    .daily-card {
      background: #fff;
      border-radius: 16px;
      padding: 40px;
      text-align: center;
      box-shadow: 0 4px 20px rgba(0,0,0,0.05);

      .daily-word {
        font-size: 64px;
        font-weight: bold;
        color: #333;
        margin-bottom: 16px;
        letter-spacing: 8px;
      }

      .daily-tags {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 12px;
      }

      .daily-hint {
        font-size: 13px;
        color: #999;
        margin-bottom: 24px;
      }

      .daily-actions {
        display: flex;
        justify-content: center;
        gap: 12px;
      }
    }
  }

  .featured-section {
    .featured-carousel {
      :deep(.el-carousel) {
        .el-carousel__item--card {
          border-radius: 16px;
        }
      }

      .featured-card {
        background: #fff;
        border-radius: 16px;
        padding: 24px;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }

        .featured-word {
          font-size: 32px;
          font-weight: bold;
          color: #333;
          margin-bottom: 12px;
        }

        .featured-tags {
          display: flex;
          gap: 6px;
          margin-bottom: 12px;
        }

        .featured-meta {
          .difficulty {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 13px;
            color: #999;
          }
        }
      }
    }
  }

  .science-section {
    .science-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;

      .science-card {
        background: #fff;
        border-radius: 12px;
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        }

        .science-icon {
          width: 56px;
          height: 56px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          margin-bottom: 12px;
          color: #fff;
        }

        .science-info {
          h4 {
            font-size: 15px;
            color: #333;
            margin-bottom: 6px;
          }
          p {
            font-size: 12px;
            color: #999;
            line-height: 1.5;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .home-page {
    .carousel-section {
      :deep(.el-carousel) .el-carousel__container .el-carousel__item .banner-content {
        flex-direction: column;
        padding: 30px 20px;
        justify-content: center;
        text-align: center;
        .banner-text {
          h2 { font-size: 24px; }
          p { font-size: 14px; }
        }
        .banner-illustration { display: none; }
      }
    }

    .science-section .science-grid {
      grid-template-columns: 1fr;
    }

    .featured-section .featured-carousel :deep(.el-carousel) {
      .el-carousel__item--card { width: 60%; }
    }
  }
}
</style>