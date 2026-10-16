<template>
  <div class="science-page">
    <div class="page-header">
      <h2>手语科普</h2>
      <p>了解手语文化，学习手语知识</p>
    </div>
    
    <div class="daily-section">
      <div class="daily-card word-card">
        <div class="card-label">每日一词</div>
        <div class="card-content">
          <h3>{{ dailyWord.word }}</h3>
          <p>{{ dailyWord.meaning }}</p>
          <el-tag size="small">{{ dailyWord.category }}</el-tag>
        </div>
        <el-button type="primary" @click="openWordDetail(dailyWord.id)">
          查看详情
        </el-button>
      </div>
      
      <div class="daily-card sentence-card">
        <div class="card-label">每日一句</div>
        <div class="card-content">
          <p class="sentence">{{ dailySentence.text }}</p>
          <p class="translation">{{ dailySentence.translation }}</p>
        </div>
      </div>
    </div>
    
    <div class="articles-section">
      <h3>科普文章</h3>
      <div class="article-list">
        <div
          v-for="article in articles"
          :key="article.id"
          class="article-card"
          @click="goToArticle(article.id)"
        >
          <div class="article-header">
            <h4>{{ article.title }}</h4>
            <el-icon><Star /></el-icon>
          </div>
          <p class="article-summary">{{ article.summary }}</p>
          <div class="article-meta">
            <span class="views"><el-icon><View /></el-icon> {{ article.views }} 阅读</span>
            <span class="date">{{ article.createTime }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="video-section">
      <h3>科普视频</h3>
      <div class="video-list">
        <div v-for="video in videos" :key="video.id" class="video-card" @click="playVideo(video)">
          <div class="video-cover">
            <img :src="video.cover" alt="" @error="handleImageError" />
            <div class="play-btn">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <span class="duration">{{ video.duration }}</span>
          </div>
          <div class="video-info">
            <h4>{{ video.title }}</h4>
            <p>{{ video.desc }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="knowledge-cards">
      <h3>手语知识卡片</h3>
      <div class="cards-grid">
        <div v-for="card in knowledgeCards" :key="card.id" class="knowledge-card">
          <div class="card-icon">{{ card.icon }}</div>
          <h4>{{ card.title }}</h4>
          <p>{{ card.desc }}</p>
        </div>
      </div>
    </div>
    
    <el-dialog v-model="videoDialogVisible" title="视频播放" width="700px">
      <VideoPlayer v-if="currentVideo" :src="currentVideo.url" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Star, View, VideoPlay } from '@element-plus/icons-vue'
import { articleApi } from '@/api'
import { useWordDetailStore } from '@/store'
import VideoPlayer from '@/components/VideoPlayer/index.vue'

const { openWordDetail } = useWordDetailStore()

const videoDialogVisible = ref(false)
const currentVideo = ref(null)

const dailyWord = ref({
  id: 1,
  word: '你好',
  meaning: '用于问候的常用手势，表示友好和礼貌',
  category: '基础问候'
})

const dailySentence = ref({
  text: '手语是人类最美丽的语言之一',
  translation: 'Sign language is one of the most beautiful languages'
})

const articles = ref([
  {
    id: 1,
    title: '手语的起源与发展',
    summary: '了解手语从手势语到规范化的发展历程，探索人类无声交流的智慧结晶。',
    views: 1234,
    createTime: '2024-01-15'
  },
  {
    id: 2,
    title: '中国手语与地方手语的区别',
    summary: '全国通用手语与各地方言手语的异同，帮助你更好地理解手语的多样性。',
    views: 2567,
    createTime: '2024-01-20'
  },
  {
    id: 3,
    title: '手语在教育中的应用',
    summary: '如何用手语辅助特殊教育，让教育更加包容和多元化。',
    views: 3456,
    createTime: '2024-02-01'
  },
  {
    id: 4,
    title: '聋人文化与手语',
    summary: '探索聋人社区的文化内涵，了解手语背后的文化价值。',
    views: 1890,
    createTime: '2024-02-10'
  }
])

const videos = ref([
  {
    id: 1,
    title: '基础手语入门教程',
    desc: '适合初学者的手语基础动作演示',
    duration: '12:30',
    url: '',
    cover: defaultCover
  },
  {
    id: 2,
    title: '数字手势详解',
    desc: '1-10数字的手语表达方式',
    duration: '08:45',
    url: '',
    cover: defaultCover
  },
  {
    id: 3,
    title: '日常交流手语短句',
    desc: '实用日常交流用语手语演示',
    duration: '15:20',
    url: '',
    cover: defaultCover
  }
])

const knowledgeCards = ref([
  {
    id: 1,
    icon: '🖐',
    title: '手型',
    desc: '手语的基本元素之一，不同的手型代表不同的含义'
  },
  {
    id: 2,
    icon: '📍',
    title: '位置',
    desc: '手势在空间中的位置影响其表达的意思'
  },
  {
    id: 3,
    icon: '🔄',
    title: '动作',
    desc: '手的移动方向和方式是区分手势的关键'
  },
  {
    id: 4,
    icon: '😊',
    title: '表情',
    desc: '面部表情在手语中同样重要，承载情感信息'
  }
])

function handleImageError(e) {
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 225" fill="%23ddd"><rect width="400" height="225"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="%23999">视频封面</text></svg>'
}

function goToArticle(id) {
  console.log('查看文章:', id)
}

function playVideo(video) {
  currentVideo.value = video
  videoDialogVisible.value = true
}
</script>

<style scoped lang="scss">
.science-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 130px);
  
  .page-header {
    text-align: center;
    margin-bottom: 30px;
    
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
  
  .daily-section {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 30px;
    
    .daily-card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      
      .card-label {
        font-size: 12px;
        color: #667eea;
        margin-bottom: 12px;
      }
      
      &.word-card {
        .card-content {
          margin-bottom: 16px;
          
          h3 {
            font-size: 28px;
            color: #333;
            margin-bottom: 8px;
          }
          
          p {
            color: #666;
            margin-bottom: 12px;
          }
        }
      }
      
      &.sentence-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        
        .card-content {
          .sentence {
            font-size: 20px;
            line-height: 1.6;
            margin-bottom: 12px;
          }
          
          .translation {
            font-size: 14px;
            opacity: 0.9;
          }
        }
      }
    }
  }
  
  .articles-section,
  .video-section,
  .knowledge-cards {
    margin-bottom: 30px;
    
    h3 {
      font-size: 18px;
      color: #333;
      margin-bottom: 16px;
    }
  }
  
  .articles-section {
    .article-list {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      
      .article-card {
        background: #fff;
        border-radius: 12px;
        padding: 20px;
        cursor: pointer;
        transition: all 0.3s;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .article-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          
          h4 {
            font-size: 16px;
            color: #333;
            margin: 0;
          }
          
          .el-icon {
            color: #999;
          }
        }
        
        .article-summary {
          color: #666;
          font-size: 14px;
          line-height: 1.6;
          margin-bottom: 12px;
        }
        
        .article-meta {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #999;
          
          .views {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }
    }
  }
  
  .video-section {
    .video-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      
      .video-card {
        background: #fff;
        border-radius: 12px;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.3s;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .video-cover {
          position: relative;
          aspect-ratio: 16/9;
          background: #ddd;
          
          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
          
          .play-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(255,255,255,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            
            .el-icon {
              font-size: 24px;
              color: #667eea;
            }
          }
          
          .duration {
            position: absolute;
            bottom: 8px;
            right: 8px;
            padding: 2px 8px;
            background: rgba(0,0,0,0.7);
            color: #fff;
            font-size: 12px;
            border-radius: 4px;
          }
        }
        
        .video-info {
          padding: 16px;
          
          h4 {
            font-size: 14px;
            color: #333;
            margin: 0 0 4px;
          }
          
          p {
            font-size: 12px;
            color: #999;
            margin: 0;
          }
        }
      }
    }
  }
  
  .knowledge-cards {
    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      
      .knowledge-card {
        background: #fff;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        
        .card-icon {
          font-size: 48px;
          margin-bottom: 12px;
        }
        
        h4 {
          font-size: 16px;
          color: #333;
          margin: 0 0 8px;
        }
        
        p {
          font-size: 14px;
          color: #999;
          margin: 0;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .science-page {
    .daily-section {
      grid-template-columns: 1fr;
    }
    
    .articles-section .article-list {
      grid-template-columns: 1fr;
    }
  }
}
</style>
