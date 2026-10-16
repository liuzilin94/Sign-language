import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useLearnStore = defineStore('learn', () => {
  const favorites = ref(JSON.parse(localStorage.getItem('favorites') || '[]'))
  const newWords = ref(JSON.parse(localStorage.getItem('newWords') || '[]'))
  const notes = ref(JSON.parse(localStorage.getItem('notes') || '{}'))
  const reviewSchedule = ref(JSON.parse(localStorage.getItem('reviewSchedule') || '{}'))
  const learnStats = ref(JSON.parse(localStorage.getItem('learnStats') || '[]'))
  
  function toggleFavorite(wordId) {
    const index = favorites.value.indexOf(wordId)
    if (index > -1) {
      favorites.value.splice(index, 1)
    } else {
      favorites.value.push(wordId)
    }
    localStorage.setItem('favorites', JSON.stringify(favorites.value))
  }
  
  function isFavorite(wordId) {
    return favorites.value.includes(wordId)
  }
  
  function toggleNewWord(wordId) {
    const index = newWords.value.indexOf(wordId)
    if (index > -1) {
      newWords.value.splice(index, 1)
    } else {
      newWords.value.push(wordId)
    }
    localStorage.setItem('newWords', JSON.stringify(newWords.value))
  }
  
  function isNewWord(wordId) {
    return newWords.value.includes(wordId)
  }
  
  function addNote(wordId, note) {
    const wordNotes = notes.value[wordId] || []
    wordNotes.push({
      id: Date.now(),
      content: note,
      time: new Date().toLocaleString()
    })
    notes.value[wordId] = wordNotes
    localStorage.setItem('notes', JSON.stringify(notes.value))
  }
  
  function deleteNote(wordId, noteId) {
    const wordNotes = notes.value[wordId] || []
    notes.value[wordId] = wordNotes.filter(n => n.id !== noteId)
    localStorage.setItem('notes', JSON.stringify(notes.value))
  }
  
  function getNotes(wordId) {
    return notes.value[wordId] || []
  }
  
  function recordLearnTime(minutes) {
    const today = new Date().toLocaleDateString()
    const existing = learnStats.value.find(s => s.date === today)
    if (existing) {
      existing.minutes += minutes
    } else {
      learnStats.value.push({ date: today, minutes })
    }
    localStorage.setItem('learnStats', JSON.stringify(learnStats.value))
  }
  
  function getReviewWords(wordId) {
    const schedule = reviewSchedule.value[wordId]
    if (!schedule) return true
    const now = Date.now()
    return schedule.nextReview <= now
  }
  
  function updateReviewSchedule(wordId, correct) {
    const intervals = [1, 2, 4, 7, 15, 30]
    const current = reviewSchedule.value[wordId] || { interval: 0 }
    const newInterval = correct ? intervals[Math.min(current.interval, intervals.length - 1)] : 1
    reviewSchedule.value[wordId] = {
      interval: correct ? newInterval : 0,
      nextReview: Date.now() + newInterval * 24 * 60 * 60 * 1000,
      lastReview: Date.now()
    }
    localStorage.setItem('reviewSchedule', JSON.stringify(reviewSchedule.value))
  }
  
  return {
    favorites,
    newWords,
    notes,
    reviewSchedule,
    learnStats,
    toggleFavorite,
    isFavorite,
    toggleNewWord,
    isNewWord,
    addNote,
    deleteNote,
    getNotes,
    recordLearnTime,
    getReviewWords,
    updateReviewSchedule
  }
})
