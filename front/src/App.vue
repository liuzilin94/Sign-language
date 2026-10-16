<template>
  <div id="app">
    <Navbar />
    <main class="main-content">
      <router-view />
    </main>
    <WordDetailDialog />
    <FloatingBall v-if="showFloatingBall" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar/index.vue'
import FloatingBall from './components/FloatingBall/index.vue'
import WordDetailDialog from './components/WordDetailDialog/index.vue'
import { useSettingsStore } from './store'

const route = useRoute()
const settingsStore = useSettingsStore()

const showFloatingBall = computed(() => {
  return settingsStore.settings.floatingBallEnabled && route.name !== 'Login' && route.name !== 'Register'
})
</script>

<style scoped>
#app {
  min-height: 100vh;
  background: #fafaf8;
}

.main-content {
  min-height: calc(100vh - 60px);
}
</style>
