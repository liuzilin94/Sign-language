<template>
  <div class="achievements-page">
    <div class="user-info-card">
      <div class="user-avatar">
        <svg class="avatar-svg" viewBox="0 0 100 100"><circle cx="50" cy="35" r="25" fill="#ddd"/><circle cx="50" cy="75" r="30" fill="#ddd"/></svg>
        <span class="level-badge">{{ level }}</span>
      </div>
      <div class="user-details">
        <h2>{{ username }}</h2>
        <div class="exp-bar">
          <el-progress :percentage="expPercent" :show-text="false" />
          <span class="exp-text">{{ currentExp }} / {{ nextLevelExp }} 经验值</span>
        </div>
        <div class="user-stats">
          <div class="stat">
            <span class="value">{{ points }}</span>
            <span class="label">积分</span>
          </div>
          <div class="stat">
            <span class="value">{{ totalExp }}</span>
            <span class="label">总经验</span>
          </div>
          <div class="stat">
            <span class="value">{{ streakDays }}</span>
            <span class="label">连续天数</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="achievements-grid">
      <h3>我的成就</h3>
      <div class="achievement-list">
        <div
          v-for="achievement in achievements"
          :key="achievement.id"
          class="achievement-card"
          :class="{ unlocked: achievement.progress >= 100 }"
          @click="showAchievementDetail(achievement)"
        >
          <div class="achievement-icon">
            {{ achievement.icon }}
          </div>
          <div class="achievement-info">
            <h4>{{ achievement.name }}</h4>
            <p>{{ achievement.description }}</p>
            <el-progress :percentage="achievement.progress" :show-text="false" size="small" />
          </div>
          <div class="achievement-status">
            <el-icon v-if="achievement.progress >= 100"><CircleCheck /></el-icon>
            <span v-else class="progress-text">{{ achievement.progress }}%</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="badges-wall">
      <h3>勋章墙</h3>
      <div class="badges-grid">
        <div
          v-for="badge in badges"
          :key="badge.id"
          class="badge-item"
          :class="{ earned: badge.earned }"
          @click="showBadgeDetail(badge)"
        >
          <div class="badge-icon">{{ badge.icon }}</div>
          <span class="badge-name">{{ badge.name }}</span>
        </div>
      </div>
    </div>
    
    <div class="points-shop">
      <h3>积分商城</h3>
      <div class="products-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          <div class="product-image">{{ product.icon }}</div>
          <h4>{{ product.name }}</h4>
          <p>{{ product.desc }}</p>
          <div class="product-action">
            <span class="price">{{ product.price }} 积分</span>
            <el-button size="small" type="primary" @click="exchange(product)">兑换</el-button>
          </div>
        </div>
      </div>
    </div>
    
    <el-dialog v-model="detailDialogVisible" :title="selectedAchievement?.name" width="400px">
      <div class="achievement-detail">
        <div class="detail-icon">{{ selectedAchievement?.icon }}</div>
        <p class="detail-desc">{{ selectedAchievement?.description }}</p>
        <div class="detail-progress">
          <el-progress :percentage="selectedAchievement?.progress || 0" />
          <span>{{ selectedAchievement?.progress || 0 }}% 完成</span>
        </div>
        <div class="detail-requirement">
          <span class="label">获取条件</span>
          <span>{{ selectedAchievement?.requirement }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { CircleCheck } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const username = ref('手语学习者')
const level = ref(5)
const currentExp = ref(1250)
const nextLevelExp = ref(2000)
const points = ref(380)
const totalExp = ref(3650)
const streakDays = ref(15)

const expPercent = ref(Math.round(currentExp.value / nextLevelExp.value * 100))

const achievements = ref([
  { id: 1, name: '初学者', description: '完成首个词汇学习', icon: '🌱', progress: 100, requirement: '学习10个词汇' },
  { id: 2, name: '每日打卡', description: '连续7天学习', icon: '📅', progress: 60, requirement: '连续学习7天' },
  { id: 3, name: '手语达人', description: '掌握100个词汇', icon: '🎯', progress: 45, requirement: '学习100个词汇' },
  { id: 4, name: '方言专家', description: '上传并通过5个方言视频', icon: '🏆', progress: 20, requirement: '通过5个方言审核' },
  { id: 5, name: '学习之星', description: '学习时长超过100小时', icon: '⭐', progress: 35, requirement: '学习100小时' },
  { id: 6, name: '社区活跃', description: '发布10条动态', icon: '🔥', progress: 80, requirement: '发布10条动态' }
])

const badges = ref([
  { id: 1, name: '初露锋芒', icon: '🌟', earned: true },
  { id: 2, name: '坚持不懈', icon: '💪', earned: true },
  { id: 3, name: '学习之星', icon: '⭐', earned: true },
  { id: 4, name: '手语专家', icon: '🎓', earned: true },
  { id: 5, name: '方言专家', icon: '🌍', earned: false },
  { id: 6, name: '全勤达人', icon: '🏅', earned: false },
  { id: 7, name: '分享达人', icon: '🤝', earned: false },
  { id: 8, name: '满分学员', icon: '💯', earned: false }
])

const products = ref([
  { id: 1, name: '手语教程一本', desc: '精选手语教程电子版', icon: '📚', price: 100 },
  { id: 2, name: '主题皮肤', desc: '平台专属主题皮肤', icon: '🎨', price: 200 },
  { id: 3, name: '高级功能', desc: '一个月高级会员', icon: '💎', price: 500 }
])

const detailDialogVisible = ref(false)
const selectedAchievement = ref(null)

function showAchievementDetail(achievement) {
  selectedAchievement.value = achievement
  detailDialogVisible.value = true
}

function showBadgeDetail(badge) {
  ElMessage.info(badge.earned ? `恭喜获得 ${badge.name} 勋章！` : `继续努力解锁 ${badge.name} 勋章`)
}

function exchange(product) {
  if (points.value >= product.price) {
    points.value -= product.price
    ElMessage.success(`成功兑换 ${product.name}！`)
  } else {
    ElMessage.warning('积���不足')
  }
}
</script>

<style scoped lang="scss">
.achievements-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 130px);
  
  .user-info-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 30px;
    display: flex;
    gap: 30px;
    color: #fff;
    margin-bottom: 30px;
    
    .user-avatar {
      position: relative;
      
      img {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 3px solid #fff;
      }
      
      .level-badge {
        position: absolute;
        bottom: -5px;
        right: -5px;
        background: #f56c6c;
        color: #fff;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: bold;
        border: 2px solid #fff;
      }
    }
    
    .user-details {
      flex: 1;
      
      h2 {
        font-size: 24px;
        margin: 0 0 16px;
      }
      
      .exp-bar {
        margin-bottom: 20px;
        
        .el-progress {
          :deep(.el-progress-bar__outer) {
            background: rgba(255,255,255,0.3);
          }
        }
        
        .exp-text {
          font-size: 12px;
          opacity: 0.9;
          margin-top: 4px;
          display: block;
        }
      }
      
      .user-stats {
        display: flex;
        gap: 30px;
        
        .stat {
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
  }
  
  .achievements-grid,
  .badges-wall,
  .points-shop {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    
    h3 {
      font-size: 18px;
      color: #333;
      margin-bottom: 20px;
    }
  }
  
  .achievement-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .achievement-card {
      display: flex;
      align-items: center;
      padding: 16px;
      background: #f9fafb;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        background: #f0f2f5;
      }
      
      &.unlocked {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
      }
      
      .achievement-icon {
        font-size: 36px;
        margin-right: 16px;
      }
      
      .achievement-info {
        flex: 1;
        
        h4 {
          font-size: 16px;
          color: #333;
          margin: 0 0 4px;
        }
        
        p {
          font-size: 13px;
          color: #999;
          margin: 0 0 8px;
        }
        
        .el-progress {
          max-width: 200px;
        }
      }
      
      .achievement-status {
        .el-icon {
          font-size: 24px;
          color: #67c23a;
        }
        
        .progress-text {
          font-size: 14px;
          color: #999;
        }
      }
    }
  }
  
  .badges-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 16px;
    
    .badge-item {
      text-align: center;
      padding: 20px 10px;
      background: #f9fafb;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s;
      opacity: 0.5;
      
      &:hover {
        transform: scale(1.05);
      }
      
      &.earned {
        opacity: 1;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
      }
      
      .badge-icon {
        font-size: 40px;
        margin-bottom: 8px;
      }
      
      .badge-name {
        font-size: 13px;
        color: #333;
      }
    }
  }
  
  .products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    
    .product-card {
      padding: 20px;
      background: #f9fafb;
      border-radius: 12px;
      text-align: center;
      
      .product-image {
        font-size: 48px;
        margin-bottom: 12px;
      }
      
      h4 {
        font-size: 16px;
        color: #333;
        margin: 0 0 8px;
      }
      
      p {
        font-size: 12px;
        color: #999;
        margin: 0 0 16px;
      }
      
      .product-action {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .price {
          font-size: 14px;
          color: #667eea;
          font-weight: bold;
        }
      }
    }
  }
  
  .achievement-detail {
    text-align: center;
    
    .detail-icon {
      font-size: 64px;
      margin-bottom: 16px;
    }
    
    .detail-desc {
      color: #666;
      margin-bottom: 20px;
    }
    
    .detail-progress {
      margin-bottom: 20px;
      
      span {
        display: block;
        margin-top: 8px;
        color: #667eea;
        font-weight: bold;
      }
    }
    
    .detail-requirement {
      padding: 12px;
      background: #f9fafb;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      .label {
        font-size: 12px;
        color: #999;
      }
    }
  }
}

@media (max-width: 768px) {
  .achievements-page {
    .user-info-card {
      flex-direction: column;
      align-items: center;
      text-align: center;
    }
  }
}
</style>
