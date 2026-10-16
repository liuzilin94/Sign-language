import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useLearnStore } from './learn'
import { wordApi } from '@/api'

// 图片URL映射表（后端ID -> 图片文件名）
const imageUrlMap = {
  '000100': '/images/dict/来.png',
  '000101': '/images/dict/去（出）.png',
  '000102': '/images/dict/到.png',
  '000103': '/images/dict/晒.png',
  '000104': '/images/dict/醒.png',
  '000105': '/images/dict/有.png',
  '000106': '/images/dict/没有（无）.png',
  '000107': '/images/dict/是.png',
  '000108': '/images/dict/不是.png',
  '000109': '/images/dict/属于.png',
  '000110': '/images/dict/小.png',
  '000111': '/images/dict/多.png',
  '000112': '/images/dict/少.png',
  '000113': '/images/dict/长.png',
  '000114': '/images/dict/短.png',
  '000115': '/images/dict/高.png',
  '000116': '/images/dict/矮.png',
  '000117': '/images/dict/远.png',
  '000118': '/images/dict/近.png',
  '000119': '/images/dict/宽.png',
}

export const useWordDetailStore = defineStore('wordDetail', () => {
  const dialogVisible = ref(false)
  const currentWordId = ref(null)
  const loading = ref(false)
  const wordData = ref(null)
  const error = ref(null)

  const isFavorite = computed(() =>
    wordData.value ? useLearnStore().isFavorite(wordData.value.id) : false
  )
  const isNewWord = computed(() =>
    wordData.value ? useLearnStore().isNewWord(wordData.value.id) : false
  )

  const allDialects = ref([
    { id: 1, region: '北京', videoUrl: '', status: 'approved', author: '用户A' },
    { id: 2, region: '上海', videoUrl: '', status: 'pending', author: '用户B' },
    { id: 3, region: '广东', videoUrl: '', status: 'approved', author: '用户C' },
    { id: 4, region: '四川', videoUrl: '', status: 'approved', author: '用户D' },
    { id: 5, region: '东北', videoUrl: '', status: 'pending', author: '用户E' }
  ])

  function getImageUrl(backendId) {
    const url = imageUrlMap[backendId] || ''
    console.log('[WordDetail] getImageUrl:', backendId, '->', url)
    return url
  }

  function getDefaultSteps(wordText) {
    return [
      '手型：五指并拢，掌心朝前',
      '位置：双手置于胸前，与肩同宽',
      `动作：做 "${wordText}" 的手势动作`
    ]
  }

  function openWordDetail(wordId) {
    console.log('[WordDetail] openWordDetail called with:', wordId)
    currentWordId.value = wordId
    dialogVisible.value = true
    loadWordData(wordId)
  }

  async function loadWordData(id) {
    if (!id) return
    loading.value = true
    error.value = null
    wordData.value = null
    console.log('[WordDetail] loadWordData started for id:', id)

    try {
      const res = await wordApi.getWord(id)
      console.log('[WordDetail] API response:', res)
      console.log('[WordDetail] res.data:', res.data)
      console.log('[WordDetail] res.data.backend_id:', res.data?.backend_id)
      console.log('[WordDetail] res.data.steps:', res.data?.steps)
      console.log('[WordDetail] res.data.image_url:', res.data?.image_url)

      if (res.data) {
        const backendId = res.data.backend_id || ''
        const wordText = res.data.word || ''
        const existingSteps = res.data.steps || []
        const existingTips = res.data.tips || []
        const existingImageUrl = res.data.image_url || ''

        // 获取图片URL
        const imageUrl = existingImageUrl || getImageUrl(backendId)
        // 获取步骤数据
        const steps = existingSteps.length > 0 ? existingSteps : getDefaultSteps(wordText)

        console.log('[WordDetail] Processed - backendId:', backendId)
        console.log('[WordDetail] Processed - imageUrl:', imageUrl)
        console.log('[WordDetail] Processed - steps:', steps)

        wordData.value = {
          id: res.data.id,
          backend_id: backendId,
          word: wordText,
          category: res.data.category || '基础',
          scene: res.data.scene || '日常',
          difficulty: res.data.difficulty || 1,
          region: res.data.region || '全国通用',
          videoUrl: res.data.demo_video_url || '',
          imageUrl: imageUrl,
          steps: steps,
          tips: existingTips,
          dialects: allDialects.value
        }

        console.log('[WordDetail] Final wordData:', wordData.value)
      } else {
        console.warn('[WordDetail] No data in response')
      }
    } catch (e) {
      console.error('[WordDetail] Error loading word:', e)
      error.value = '加载失败，请重试'
    } finally {
      loading.value = false
    }
  }

  function closeDialog() {
    dialogVisible.value = false
  }

  return {
    dialogVisible,
    currentWordId,
    loading,
    wordData,
    error,
    isFavorite,
    isNewWord,
    allDialects,
    openWordDetail,
    loadWordData,
    closeDialog
  }
})
