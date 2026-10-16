<template>
  <div class="dict-page">
    <div class="page-header">
      <h1>词典</h1>
      <p>收录标准中国手语词汇</p>
    </div>

    <div class="dict-filters">
      <el-input
        v-model="keyword"
        placeholder="搜索词汇..."
        clearable
        @keyup.enter="handleSearch"
        class="dict-search"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <div class="dict-main">
      <div class="dict-toolbar">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button label="grid">
            <el-icon><Grid /></el-icon>
          </el-radio-button>
          <el-radio-button label="list">
            <el-icon><List /></el-icon>
          </el-radio-button>
        </el-radio-group>
      </div>

      <div v-if="loading" class="dict-loading">
        <Loading text="加载中..." />
      </div>

      <div v-else-if="filteredWords.length === 0" class="dict-empty">
        <p>未找到匹配的词汇</p>
        <el-button @click="resetFilters">重置筛选</el-button>
      </div>

        <div v-else :class="['dict-grid', viewMode]">
          <div
            v-for="word in paginatedWords"
            :key="word.id"
            class="dict-card"
            @click="openWordDetail(word.id)"
          >
            <div class="dict-card-inner">
              <span class="dict-word">{{ word.word }}</span>
            </div>
          </div>
        </div>

      <div class="dict-pagination" v-if="filteredWords.length > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredWords.length"
          layout="prev, pager, next"
          @current-change="scrollToTop"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Grid, List } from '@element-plus/icons-vue'
import { wordApi } from '@/api'
import Loading from '@/components/Loading/index.vue'
import { useWordDetailStore } from '@/store'

const wordDetailStore = useWordDetailStore()
const loading = ref(false)
const keyword = ref('')
const viewMode = ref('grid')
const currentPage = ref(1)
const pageSize = ref(40)
const allWords = ref([])

const categories = ['基础', '生活', '社会', '社交', '情感', '科技']
const scenes = ['日常问候', '家庭', '饮食', '职业', '人际', '表达']

const filters = ref({ category: '', scene: '', difficulty: '', region: '' })

const filteredWords = computed(() => {
  let result = allWords.value
  if (keyword.value) {
    result = result.filter(w => w.word.includes(keyword.value))
  }
  if (filters.value.category) {
    result = result.filter(w => w.category === filters.value.category)
  }
  if (filters.value.scene) {
    result = result.filter(w => w.scene === filters.value.scene)
  }
  if (filters.value.difficulty) {
    result = result.filter(w => w.difficulty === filters.value.difficulty)
  }
  if (filters.value.region) {
    result = result.filter(w => w.region === filters.value.region || w.region === '全国通用')
  }
  return result
})

const paginatedWords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredWords.value.slice(start, start + pageSize.value)
})

function openWordDetail(wordId) {
  wordDetailStore.openWordDetail(wordId)
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function fetchWords() {
  loading.value = true
  try {
    const res = await wordApi.getWords({ page: 1, page_size: 100 })
    const words = res.data.items || res.data
    // 映射 demo_video_url -> videoUrl
    allWords.value = words.map(w => ({
      ...w,
      videoUrl: w.demo_video_url || w.videoUrl || ''
    }))
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
}

function resetFilters() {
  filters.value = { category: '', scene: '', difficulty: '', region: '' }
  keyword.value = ''
  currentPage.value = 1
}

onMounted(fetchWords)
</script>

<style scoped lang="scss">
.dict-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 48px 32px 80px;
  min-height: calc(100vh - 60px);

  .page-header {
    text-align: center;
    margin-bottom: 40px;

    h1 {
      font-size: 28px;
      font-weight: 700;
      color: #0d0d0d;
      margin: 0 0 6px;
      letter-spacing: -0.5px;
    }

    p {
      font-size: 14px;
      color: #8a8a8a;
      margin: 0;
    }
  }

  .dict-filters {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 24px;
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 16px 20px;

    .dict-search {
      width: 180px;

      :deep(.el-input__wrapper) {
        border-radius: 6px;
      }
    }

    .dict-select {
      width: 110px;

      :deep(.el-input__wrapper) {
        border-radius: 6px;
      }
    }
  }

  .dict-main {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 20px 24px;

      .dict-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;

      :deep(.el-radio-button__inner) {
        border-radius: 4px;
      }
    }
  }

  .dict-loading,
  .dict-empty {
    padding: 80px 0;
    text-align: center;
    color: #8a8a8a;
    font-size: 14px;
  }

  .dict-empty p {
    margin-bottom: 16px;
  }

  .dict-grid {
    &.grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 10px;

      .dict-card {
        padding: 20px 14px;
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 8px;
      }
    }

    &.list {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .dict-card {
        padding: 14px 16px;
        flex-direction: row;
        align-items: center;
        gap: 12px;

        .dict-card-inner {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .dict-tags {
          margin-bottom: 0;
        }

        .dict-meta {
          margin-left: auto;
        }
      }
    }

    .dict-card {
      background: #fafaf8;
      border: 1px solid transparent;
      border-radius: 8px;
      cursor: pointer;
      transition: all 180ms ease;
      display: flex;

      &:hover {
        background: #fff;
        border-color: #c8c8c8;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
      }

      .dict-card-inner {
        .dict-word {
          font-size: 20px;
          font-weight: 600;
          color: #0d0d0d;
        }
      }

      .dict-tags {
        display: flex;
        gap: 5px;
        flex-wrap: wrap;
      }

      .dict-meta {
        display: flex;
        gap: 8px;
        font-size: 11px;
        color: #c8c8c8;
      }
    }
  }

  .dict-pagination {
    margin-top: 24px;
    display: flex;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .dict-page {
    padding: 32px 16px 60px;

    .dict-filters {
      padding: 12px 14px;

      .dict-search {
        width: 100%;
      }

      .dict-select {
        flex: 1;
        min-width: 90px;
      }
    }

    .dict-main {
      padding: 16px;
    }

    .dict-grid.grid {
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;

      .dict-card {
        padding: 16px 8px;

        .dict-word {
          font-size: 17px;
        }
      }
    }
  }
}
</style>
