<template>
  <div class="stage-video">
    <div class="stage-header">
      <div class="stage-badge">
        <span class="badge-num">1</span>
        <span class="badge-text">看视频学习</span>
      </div>
      <h2 class="word-display">{{ question.word }}</h2>
    </div>

    <!-- 视频/图片展示 -->
    <div class="media-container">
      <div v-if="question.video_url" class="video-wrapper">
        <video
          ref="videoEl"
          :src="question.video_url"
          controls
          autoplay
          loop
          playsinline
        ></video>
      </div>
      <div v-else-if="question.image_url" class="image-wrapper">
        <img :src="question.image_url" :alt="question.word" />
      </div>
      <div v-else class="placeholder-wrapper">
        <div class="placeholder-content">
          <el-icon><VideoPlay /></el-icon>
          <span>暂无演示视频</span>
        </div>
      </div>
    </div>

    <!-- 动作分解 -->
    <div v-if="question.steps && question.steps.length > 0" class="steps-section">
      <h3 class="section-title">
        <el-icon><List /></el-icon>
        动作分解
      </h3>
      <div class="steps-list">
        <div
          v-for="(step, index) in question.steps"
          :key="index"
          class="step-item"
        >
          <div class="step-num">{{ index + 1 }}</div>
          <div class="step-text">{{ step }}</div>
        </div>
      </div>
    </div>

    <!-- 手型要点 -->
    <div v-if="question.tips && question.tips.length > 0" class="tips-section">
      <h3 class="section-title">
        <el-icon><Star /></el-icon>
        手型要点
      </h3>
      <div class="tips-list">
        <el-tag
          v-for="(tip, index) in question.tips"
          :key="index"
          type="info"
          effect="plain"
        >
          {{ tip }}
        </el-tag>
      </div>
    </div>

    <!-- 元信息 -->
    <div class="meta-section">
      <el-tag v-if="question.category" type="info">{{ question.category }}</el-tag>
      <el-tag v-if="question.difficulty" type="warning">
        {{ ['入门', '基础', '进阶'][question.difficulty - 1] || '基础' }}
      </el-tag>
    </div>

    <!-- 确认按钮 -->
    <div class="action-section">
      <el-button type="primary" size="large" @click="$emit('complete')">
        我学会了，继续下一题
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { VideoPlay, List, Star } from '@element-plus/icons-vue'

defineProps({
  question: {
    type: Object,
    required: true
  }
})

defineEmits(['complete'])

const videoEl = ref(null)
</script>

<style scoped lang="scss">
.stage-video {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
}

.stage-header {
  padding: 24px;
  text-align: center;

  .stage-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
    border-radius: 20px;
    margin-bottom: 16px;

    .badge-num {
      width: 20px;
      height: 20px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 700;
      color: #fff;
    }

    .badge-text {
      font-size: 14px;
      font-weight: 500;
      color: #fff;
    }
  }

  .word-display {
    font-size: 48px;
    font-weight: 700;
    color: #0d0d0d;
    margin: 0;
    letter-spacing: 8px;
    text-indent: 8px;
  }
}

.media-container {
  padding: 0 24px;
  margin-bottom: 24px;
}

.video-wrapper,
.image-wrapper {
  width: 100%;
  max-height: 400px;
  border-radius: 12px;
  overflow: hidden;
  background: #000;

  video, img {
    width: 100%;
    height: auto;
    max-height: 400px;
    object-fit: contain;
  }
}

.placeholder-wrapper {
  width: 100%;
  height: 300px;
  background: #f5f5f5;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;

  .placeholder-content {
    text-align: center;
    color: #c0c4cc;

    .el-icon {
      font-size: 48px;
      margin-bottom: 12px;
    }

    span {
      font-size: 14px;
    }
  }
}

.steps-section,
.tips-section {
  padding: 0 24px;
  margin-bottom: 24px;

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    color: #0d0d0d;
    margin: 0 0 16px;

    .el-icon {
      color: #409eff;
    }
  }
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;

  .step-num {
    width: 28px;
    height: 28px;
    background: #409eff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 600;
    color: #fff;
    flex-shrink: 0;
  }

  .step-text {
    flex: 1;
    padding-top: 4px;
    font-size: 15px;
    color: #3a3a3a;
    line-height: 1.6;
  }
}

.tips-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  .el-tag {
    font-size: 13px;
  }
}

.meta-section {
  padding: 0 24px 24px;
  display: flex;
  gap: 8px;
}

.action-section {
  padding: 24px;
  border-top: 1px solid #f0f0ee;
  display: flex;
  justify-content: center;

  .el-button {
    min-width: 200px;
  }
}
</style>
