<template>
  <div class="empty-state">
    <div class="empty-icon">
      <slot name="icon">
        <el-icon><Files /></el-icon>
      </slot>
    </div>
    <div class="empty-text">{{ text }}</div>
    <div class="empty-action" v-if="$slots.action">
      <slot name="action"></slot>
    </div>
  </div>
</template>

<script setup>
import { Files } from '@element-plus/icons-vue'

defineProps({
  text: { type: String, default: '暂无数据' }
})
</script>

<style scoped lang="scss">
.empty-state {
  padding: 60px 20px;
  text-align: center;
  
  .empty-icon {
    font-size: 64px;
    color: #dcdfe6;
    margin-bottom: 16px;
  }
  
  .empty-text {
    color: #909399;
    font-size: 14px;
    margin-bottom: 16px;
  }
}
</style>
