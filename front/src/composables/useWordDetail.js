import { ref } from 'vue'

const dialogVisible = ref(false)
const currentWordId = ref(null)

export function useWordDetail() {
  return { dialogVisible, currentWordId }
}

export function openWordDetail(wordId) {
  currentWordId.value = wordId
  dialogVisible.value = true
}
