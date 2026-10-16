import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { learningApi, reviewApi } from '@/api'
import { useUserStore } from '@/store/user'

export const useLearnStore = defineStore('learn', () => {
  const favorites = ref([])           // 收藏的词汇ID列表
  const newWords = ref([])           // 标记为生词的ID列表
  const learnedWords = ref([])         // 已学会的词汇ID列表
  const reviewWords = ref([])          // 待复习词汇列表
  const records = ref([])              // 所有学习记录
  const notes = ref({})              // 笔记 { wordId: [{ id, content, time }] }

  // 计算属性：是否已收藏
  function isFavorite(wordId) {
    return favorites.value.includes(wordId)
  }

  // 计算属性：是否标记为生词
  function isNewWord(wordId) {
    return newWords.value.includes(wordId)
  }

  // 计算属性：是否已学会
  function isLearned(wordId) {
    return learnedWords.value.includes(wordId)
  }

  // 获取某个词汇的笔记
  function getNotes(wordId) {
    return notes.value[wordId] || []
  }

  // 添加笔记
  function addNote(wordId, content) {
    if (!notes.value[wordId]) {
      notes.value[wordId] = []
    }
    notes.value[wordId].push({
      id: Date.now(),
      content,
      time: new Date().toLocaleString('zh-CN')
    })
    saveToStorage()
  }

  // 删除笔记
  function deleteNote(wordId, noteId) {
    if (notes.value[wordId]) {
      notes.value[wordId] = notes.value[wordId].filter(n => n.id !== noteId)
      saveToStorage()
    }
  }

  // 切换生词标记
  async function toggleNewWord(wordId) {
    const current = isNewWord(wordId)
    if (current) {
      newWords.value = newWords.value.filter(id => id !== wordId)
    } else {
      newWords.value.push(wordId)
    }
    saveToStorage()
  }

  // 保存数据到 localStorage
  function saveToStorage() {
    try {
      localStorage.setItem('csl_notes', JSON.stringify(notes.value))
      localStorage.setItem('csl_new_words', JSON.stringify(newWords.value))
      localStorage.setItem('csl_favorites', JSON.stringify(favorites.value))
    } catch (e) {
      console.error('Save to storage failed:', e)
    }
  }

  // 从 localStorage 加载数据
  function loadFromStorage() {
    try {
      notes.value = JSON.parse(localStorage.getItem('csl_notes') || '{}')
      newWords.value = JSON.parse(localStorage.getItem('csl_new_words') || '[]')
      favorites.value = JSON.parse(localStorage.getItem('csl_favorites') || '[]')
    } catch (e) {
      console.error('Load from storage failed:', e)
    }
  }

  // ==================== 学习记录操作 ====================
  async function fetchRecords() {
    // 从API获取学习记录
    const userStore = useUserStore()
    if (!userStore.isLoggedIn) return

    try {
      const res = await learningApi.getRecords()
      records.value = res.data
      // 更新本地状态
      favorites.value = res.data.filter(r => r.is_favorite).map(r => r.word_id)
      learnedWords.value = res.data.filter(r => r.is_learned).map(r => r.word_id)
      // 保存到 localStorage
      saveToStorage()
    } catch (error) {
      console.error('获取学习记录失败:', error)
    }
  }

  async function createRecord(wordId, isCorrect, confidence) {
    // 创建练习记录
    try {
      const res = await learningApi.createRecord({
        word_id: wordId,
        is_correct: isCorrect,
        confidence: confidence
      })
      // 更新本地缓存
      const index = records.value.findIndex(r => r.word_id === wordId)
      if (index > -1) {
        records.value[index] = res.data
      } else {
        records.value.push(res.data)
      }
      return res.data
    } catch (error) {
      console.error('创建记录失败:', error)
      throw error
    }
  }

  async function updateRecord(wordId, data) {
    // 更新学习记录（收藏/标记学会）
    try {
      const res = await learningApi.updateRecord(wordId, data)
      const index = records.value.findIndex(r => r.word_id === wordId)
      if (index > -1) {
        records.value[index] = res.data
      }
      // 同步更新本地列表
      if (data.is_favorite !== undefined) {
        const favIndex = favorites.value.indexOf(wordId)
        if (data.is_favorite && favIndex === -1) {
          favorites.value.push(wordId)
        } else if (!data.is_favorite && favIndex > -1) {
          favorites.value.splice(favIndex, 1)
        }
      }
      if (data.is_learned !== undefined) {
        if (data.is_learned && !learnedWords.value.includes(wordId)) {
          learnedWords.value.push(wordId)
        } else if (!data.is_learned && learnedWords.value.includes(wordId)) {
          const idx = learnedWords.value.indexOf(wordId)
          learnedWords.value.splice(idx, 1)
        }
      }
      // 保存到 localStorage
      saveToStorage()
      return res.data
    } catch (error) {
      console.error('更新记录失败:', error)
      throw error
    }
  }

  async function toggleFavorite(wordId) {
    // 切换收藏状态
    const current = isFavorite(wordId)
    await updateRecord(wordId, { is_favorite: !current })
  }

  async function markAsLearned(wordId) {
    // 标记为已学会
    await updateRecord(wordId, { is_learned: true })
  }

  // ==================== 复习功能 ====================
  async function fetchTodayReviews() {
    // 获取今日待复习
    // API返回: { code, message, data: [{word_id, word, interval, next_review_at, correct_count, ...}] }
    try {
      const res = await reviewApi.getTodayReviews()
      // 直接使用 res.data 作为数组
      reviewWords.value = Array.isArray(res.data) ? res.data : (res.data?.words || [])
      return reviewWords.value
    } catch (error) {
      console.error('获取复习列表失败:', error)
      return []
    }
  }

  async function completeReview(wordId, isCorrect) {
    // 完成复习
    try {
      const res = await reviewApi.completeReview(wordId, isCorrect)
      // 从待复习列表中移除
      const idx = reviewWords.value.findIndex(w => w.word_id === wordId)
      if (idx > -1) {
        reviewWords.value.splice(idx, 1)
      }
      // 更新学习记录中的复习信息
      const rec = records.value.find(r => r.word_id === wordId)
      if (rec) {
        rec.practice_count = (rec.practice_count || 0) + 1
        if (isCorrect) rec.correct_count = (rec.correct_count || 0) + 1
      }
      return res.data
    } catch (error) {
      console.error('完成复习失败:', error)
      throw error
    }
  }

  // 获取复习进度（艾宾浩斯阶段）
  function getReviewStage(correctCount) {
    const stages = [
      { stage: 1, label: '初次学习', interval: '1天后' },
      { stage: 2, label: '短期记忆', interval: '2天后' },
      { stage: 3, label: '中期记忆', interval: '4天后' },
      { stage: 4, label: '长期记忆', interval: '7天后' },
      { stage: 5, label: '深度记忆', interval: '15天后' },
      { stage: 6, label: '永久记忆', interval: '30天后' }
    ]
    return stages[Math.min(correctCount, stages.length - 1)]
  }

  // ==================== 数据统计 ====================
  function getTotalPracticeCount() {
    return records.value.reduce((sum, r) => sum + r.practice_count, 0)
  }

  function getAverageAccuracy() {
    if (records.value.length === 0) return 0
    const sum = records.value.reduce((sum, r) => sum + r.avg_accuracy, 0)
    return (sum / records.value.length).toFixed(2)
  }

  // ==================== 初始化 ====================
  async function init() {
    // 初始化学习数据
    await fetchRecords()
    await fetchTodayReviews()
  }

  return {
    // 状态
    favorites,
    newWords,
    learnedWords,
    reviewWords,
    records,
    notes,
    // 计算
    isFavorite,
    isNewWord,
    isLearned,
    getNotes,
    // 操作
    fetchRecords,
    createRecord,
    updateRecord,
    toggleFavorite,
    toggleNewWord,
    markAsLearned,
    addNote,
    deleteNote,
    fetchTodayReviews,
    completeReview,
    getReviewStage,
    loadFromStorage,
    // 统计
    getTotalPracticeCount,
    getAverageAccuracy,
    init
  }
})
