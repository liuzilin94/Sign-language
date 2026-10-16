import { defineStore } from 'pinia'
import { ref } from 'vue'
import { learningApi } from '@/api/learning'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref({
    floatingBallEnabled: true,
    notificationsEnabled: true,
    defaultPlaybackSpeed: 1,
    autoPlay: false,
    downloadQuality: 'high'
  })

  // 学习设置（从后端同步）
  const learningSettings = ref({
    daily_new_words: 3,
    daily_review_words: 5
  })

  function updateSetting(key, value) {
    settings.value[key] = value
    localStorage.setItem('settings', JSON.stringify(settings.value))
  }

  function loadSettings() {
    const saved = localStorage.getItem('settings')
    if (saved) {
      settings.value = { ...settings.value, ...JSON.parse(saved) }
    }
  }

  // 加载学习设置
  async function loadLearningSettings() {
    try {
      const res = await learningApi.getSettings()
      if (res.data) {
        learningSettings.value.daily_new_words = res.data.daily_new_words || 3
        learningSettings.value.daily_review_words = res.data.daily_review_words || 5
      }
    } catch (e) {
      console.error('加载学习设置失败:', e)
    }
  }

  // 保存学习设置并重置今日计划
  async function saveLearningSettings(data) {
    try {
      await learningApi.updateSettings(data)
      learningSettings.value.daily_new_words = data.daily_new_words
      learningSettings.value.daily_review_words = data.daily_review_words
      // 重置今日计划，以便按新设置重新生成
      await learningApi.resetTodayPlan()
      return true
    } catch (e) {
      console.error('保存学习设置失败:', e)
      return false
    }
  }

  function clearCache() {
    localStorage.removeItem('learnStats')
    localStorage.removeItem('reviewSchedule')
    localStorage.removeItem('notes')
  }

  return {
    settings,
    learningSettings,
    updateSetting,
    loadSettings,
    loadLearningSettings,
    saveLearningSettings,
    clearCache
  }
})
