<template>
  <div class="stage-input">
    <div class="stage-header">
      <div class="stage-badge stage3">
        <span class="badge-num">3</span>
        <span class="badge-text">看视频输入</span>
      </div>
      <p class="instruction-text">观看下方视频，在输入框中输入对应的词汇</p>
    </div>

    <!-- 视频展示 -->
    <div class="video-container">
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
      <div v-else class="placeholder">
        <el-icon><VideoPlay /></el-icon>
        <span>暂无视频</span>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-section">
      <el-input
        v-model="userInput"
        placeholder="请输入答案"
        size="large"
        clearable
        @keyup.enter="handleSubmit"
      >
        <template #prefix>
          <el-icon><Edit /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 不确定按钮 -->
    <div class="skip-section">
      <el-button text @click="handleSkip">
        不确定，跳过此题
      </el-button>
    </div>

    <!-- 确认按钮 -->
    <div class="action-section">
      <el-button
        type="primary"
        size="large"
        :disabled="!userInput.trim()"
        @click="handleSubmit"
      >
        确认提交
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { VideoPlay, Edit } from '@element-plus/icons-vue'

const props = defineProps({
  question: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['answer'])

const userInput = ref('')

// 题目切换时重置输入
watch(
  () => props.question ? `${props.question.word_id}-${props.question.stage}` : '',
  () => {
    userInput.value = ''
  }
)

function handleSubmit() {
  if (!userInput.value.trim()) return
  emit('answer', { stage3_input: userInput.value.trim() })
}

function handleSkip() {
  emit('answer', { stage3_input: '' })
}
</script>

<style scoped lang="scss">
.stage-input {
  background: #fff;
  border-radius: 16px;
  padding: 32px 24px;
}

.stage-header {
  text-align: center;
  margin-bottom: 24px;

  .stage-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: linear-gradient(135deg, #9c27b0 0%, #ba68c8 100%);
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

  .instruction-text {
    font-size: 16px;
    color: #8a8a8a;
    margin: 0;
  }
}

.video-container {
  margin-bottom: 24px;
}

.video-wrapper,
.image-wrapper {
  width: 100%;
  max-height: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: #000;

  video, img {
    width: 100%;
    height: auto;
    max-height: 300px;
    object-fit: contain;
  }
}

.placeholder {
  width: 100%;
  height: 200px;
  background: #f5f5f5;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;

  .el-icon {
    font-size: 40px;
    margin-bottom: 8px;
  }

  span {
    font-size: 14px;
  }
}

.input-section {
  margin-bottom: 16px;

  .el-input {
    font-size: 18px;

    :deep(.el-input__inner) {
      height: 56px;
    }
  }
}

.skip-section {
  text-align: center;
  margin-bottom: 24px;

  .el-button {
    color: #8a8a8a;
    font-size: 14px;

    &:hover {
      color: #9c27b0;
    }
  }
}

.action-section {
  display: flex;
  justify-content: center;

  .el-button {
    min-width: 200px;
  }
}
</style>
