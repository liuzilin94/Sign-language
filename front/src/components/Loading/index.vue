<template>
  <div class="loading-container" :class="{ overlay: overlay }">
    <div class="loading-spinner">
      <div class="spinner"></div>
      <div class="loading-text" v-if="text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '加载中...' },
  overlay: { type: Boolean, default: false }
})
</script>

<style scoped lang="scss">
.loading-container {
  padding: 40px;
  
  &.overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255,255,255,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
  }
  
  .loading-spinner {
    text-align: center;
    
    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid #f3f3f3;
      border-top: 3px solid #0d0d0d;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 16px;
    }
    
    .loading-text {
      color: #8a8a8a;
      font-size: 14px;
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
