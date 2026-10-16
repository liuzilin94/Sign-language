<template>
  <div class="stage-choice">
    <div class="stage-header">
      <div class="stage-badge stage2">
        <span class="badge-num">2</span>
        <span class="badge-text">选择题</span>
      </div>
      <h2 class="question-text">
        下列描述对应哪个词汇？
      </h2>
      <p class="question-desc"><span v-html="formatDesc(question.question_text)"></span></p>
    </div>

    <!-- 选项网格 -->
    <div class="options-grid">
      <div
        v-for="(option, index) in question.options"
        :key="option.id"
        class="option-card"
        :class="{
          'selected': selectedIndex === index,
          'correct': showResult && index === question.correct_index,
          'wrong': showResult && selectedIndex === index && selectedIndex !== question.correct_index
        }"
        @click="handleSelect(index)"
      >
        <div class="option-word">{{ option.word }}</div>
        <div v-if="showResult && index === question.correct_index" class="result-icon correct">
          <el-icon><Check /></el-icon>
        </div>
        <div v-if="showResult && selectedIndex === index && selectedIndex !== question.correct_index" class="result-icon wrong">
          <el-icon><Close /></el-icon>
        </div>
      </div>
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
        :disabled="selectedIndex === null"
        @click="handleConfirm"
      >
        确认选择
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Check, Close } from '@element-plus/icons-vue'

const props = defineProps({
  question: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['answer'])

const selectedIndex = ref(null)
const showResult = ref(false)

// 题目切换时重置选择状态
watch(
  () => props.question ? `${props.question.word_id}-${props.question.stage}` : '',
  () => {
    selectedIndex.value = null
    showResult.value = false
  }
)

function formatDesc(text) {
  if (!text) return ''
  return text.replace(/\n/g, '<br>')
}

function handleSelect(index) {
  if (showResult.value) return
  selectedIndex.value = index
}

function handleConfirm() {
  if (selectedIndex.value === null) return
  showResult.value = true

  // 延迟发送答案，让用户看到结果
  setTimeout(() => {
    emit('answer', { stage2_choice: selectedIndex.value })
  }, 1000)
}

function handleSkip() {
  emit('answer', { stage2_choice: -1 })
}
</script>

<style scoped lang="scss">
.stage-choice {
  background: #fff;
  border-radius: 16px;
  padding: 32px 24px;
}

.stage-header {
  text-align: center;
  margin-bottom: 32px;

  .stage-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
    border-radius: 20px;
    margin-bottom: 20px;

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

  .question-text {
    font-size: 20px;
    font-weight: 600;
    color: #0d0d0d;
    margin: 0 0 12px;
  }

  .question-desc {
    font-size: 15px;
    color: #333;
    line-height: 1.9;
    margin: 0;
    padding: 16px 20px;
    background: #f8f8f6;
    border-radius: 10px;
    border: 1px solid #e8e8e8;
    white-space: pre-wrap;
  }
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.option-card {
  position: relative;
  padding: 24px 16px;
  background: #fafaf8;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 200ms ease;

  &:hover {
    border-color: #409eff;
    background: #f0f7ff;
  }

  &.selected {
    border-color: #409eff;
    background: #e6f0ff;
  }

  &.correct {
    border-color: #67c23a;
    background: #f0f9eb;
  }

  &.wrong {
    border-color: #f56c6c;
    background: #fef0f0;
  }

  .option-word {
    font-size: 24px;
    font-weight: 700;
    color: #0d0d0d;
  }

  .result-icon {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;

    &.correct {
      background: #67c23a;
      color: #fff;
    }

    &.wrong {
      background: #f56c6c;
      color: #fff;
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
      color: #409eff;
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

@media (max-width: 480px) {
  .options-grid {
    grid-template-columns: 1fr;
  }

  .option-card {
    padding: 20px 16px;

    .option-word {
      font-size: 20px;
    }
  }
}
</style>
