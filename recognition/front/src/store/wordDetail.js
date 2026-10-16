import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useLearnStore } from './learn'

export const useWordDetailStore = defineStore('wordDetail', () => {
  const dialogVisible = ref(false)
  const currentWordId = ref(null)
  const loading = ref(false)
  const wordData = ref(null)

  const isFavorite = computed(() =>
    wordData.value ? useLearnStore().isFavorite(wordData.value.id) : false
  )
  const isNewWord = computed(() =>
    wordData.value ? useLearnStore().isNewWord(wordData.value.id) : false
  )

  const mockWords = [
    '你好', '谢谢', '再见', '对不起', '请', '家庭', '爸爸', '妈妈', '吃饭',
    '喝水', '工作', '学习', '医生', '老师', '朋友', '帮助', '喜欢', '爱', '快乐', '电脑'
  ]

  const allDialects = ref([
    { id: 1, region: '北京', videoUrl: '', status: 'approved', author: '用户A' },
    { id: 2, region: '上海', videoUrl: '', status: 'pending', author: '用户B' },
    { id: 3, region: '广东', videoUrl: '', status: 'approved', author: '用户C' },
    { id: 4, region: '四川', videoUrl: '', status: 'approved', author: '用户D' },
    { id: 5, region: '东北', videoUrl: '', status: 'pending', author: '用户E' }
  ])

  function openWordDetail(wordId) {
    currentWordId.value = wordId
    dialogVisible.value = true
    loadWordData(wordId)
  }

  function loadWordData(id) {
    if (!id) return
    loading.value = true
    wordData.value = null

    setTimeout(() => {
      const idx = Number(id) - 1
      wordData.value = {
        id,
        word: mockWords[idx] || `词汇#${id}`,
        category: ['基础', '生活', '社会', '情感', '科技'][id % 5] || '基础',
        scene: ['日常问候', '家庭', '饮食', '职业', '人际'][id % 5] || '日常问候',
        difficulty: (id % 3) + 1,
        region: '全国通用',
        videoUrl: '',
        handShape: '五指伸直，掌心朝前',
        position: '双手置于胸前位置',
        movement: '双手向外推出并自然张开',
        images: [],
        dialects: allDialects.value
      }
      loading.value = false
    }, 300)
  }

  return {
    dialogVisible,
    currentWordId,
    loading,
    wordData,
    isFavorite,
    isNewWord,
    allDialects,
    openWordDetail,
    loadWordData
  }
})
