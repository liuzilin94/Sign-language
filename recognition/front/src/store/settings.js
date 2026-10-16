import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref({
    floatingBallEnabled: true,
    notificationsEnabled: true,
    defaultPlaybackSpeed: 1,
    autoPlay: false,
    downloadQuality: 'high'
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

  function clearCache() {
    localStorage.removeItem('learnStats')
    localStorage.removeItem('reviewSchedule')
    localStorage.removeItem('notes')
  }

  return {
    settings,
    updateSetting,
    loadSettings,
    clearCache
  }
})
