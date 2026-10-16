<template>
  <div class="dictionary-page">
    <div class="filter-section">
      <div class="filter-title">筛选条件</div>
      <el-form :inline="true" class="filter-form">
        <el-form-item label="分类">
          <el-select v-model="filters.category" placeholder="全部分类" clearable @change="handleFilter">
            <el-option label="基础" value="基础" />
            <el-option label="生活" value="生活" />
            <el-option label="社会" value="社会" />
            <el-option label="社交" value="社交" />
            <el-option label="情感" value="情感" />
            <el-option label="科技" value="科技" />
          </el-select>
        </el-form-item>
        <el-form-item label="场景">
          <el-select v-model="filters.scene" placeholder="全部场景" clearable @change="handleFilter">
            <el-option label="日常问候" value="日常问候" />
            <el-option label="家庭" value="家庭" />
            <el-option label="饮食" value="饮食" />
            <el-option label="职业" value="职业" />
            <el-option label="人际" value="人际" />
            <el-option label="表达" value="表达" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="filters.difficulty" placeholder="全部难度" clearable @change="handleFilter">
            <el-option label="入门" :value="1" />
            <el-option label="基础" :value="2" />
            <el-option label="进阶" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="地区">
          <el-select v-model="filters.region" placeholder="全部地区" clearable @change="handleFilter">
            <el-option label="全国通用" value="全国通用" />
            <el-option label="北方" value="北方" />
            <el-option label="南方" value="南方" />
          </el-select>
        </el-form-item>
      </el-form>
      <div class="search-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索手语词汇..."
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>
    </div>
    
    <div class="word-list">
      <div class="list-header">
        <span class="total">共 {{ filteredWords.length }} 个词汇</span>
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button label="grid"><el-icon><Grid /></el-icon></el-radio-button>
          <el-radio-button label="list"><el-icon><List /></el-icon></el-radio-button>
        </el-radio-group>
      </div>
      
      <div v-if="loading" class="loading-wrapper">
        <Loading text="加载中..." />
      </div>
      
      <div v-else-if="filteredWords.length === 0" class="empty-wrapper">
        <EmptyState text="未找到匹配的词汇">
          <template #action>
            <el-button @click="resetFilters">重置筛选</el-button>
          </template>
        </EmptyState>
      </div>
      
      <div v-else :class="['word-grid', viewMode]">
        <div
          v-for="word in filteredWords"
          :key="word.id"
          class="word-card"
          @click="openWordDetail(word)"
        >
          <div class="word-main">{{ word.word }}</div>
          <div class="word-tags">
            <el-tag size="small">{{ word.category }}</el-tag>
            <el-tag size="small" type="info">{{ word.scene }}</el-tag>
          </div>
          <div class="word-meta">
            <span class="difficulty">
              <el-icon><Star /></el-icon>
              {{ ['入门', '基础', '进阶'][word.difficulty - 1] }}
            </span>
            <span class="region">{{ word.region }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="pagination-wrapper" v-if="filteredWords.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredWords.length"
        layout="prev, pager, next"
      />
    </div>

    <WordDetailDialog />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Search, Grid, List, Star } from '@element-plus/icons-vue'
import { wordApi } from '@/api'
import Loading from '@/components/Loading/index.vue'
import EmptyState from '@/components/EmptyState/index.vue'
import WordDetailDialog from '@/components/WordDetailDialog/index.vue'
import { useWordDetailStore } from '@/store'

const route = useRoute()
const wordDetailStore = useWordDetailStore()

const loading = ref(false)
const viewMode = ref('grid')
const currentPage = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const allWords = ref([])

const filters = reactive({
  category: '',
  scene: '',
  difficulty: '',
  region: ''
})

const filteredWords = computed(() => {
  let result = allWords.value

  if (keyword.value) {
    result = result.filter(w => w.word.includes(keyword.value))
  }

  if (filters.category) {
    result = result.filter(w => w.category === filters.category)
  }
  if (filters.scene) {
    result = result.filter(w => w.scene === filters.scene)
  }
  if (filters.difficulty) {
    result = result.filter(w => w.difficulty === filters.difficulty)
  }
  if (filters.region) {
    result = result.filter(w => w.region === filters.region || w.region === '全国通用')
  }

  return result
})

function openWordDetail(word) {
  wordDetailStore.openWordDetail(word.id)
}

async function fetchWords() {
  loading.value = true
  try {
    const res = await wordApi.getWords()
    allWords.value = res.data
    if (route.query.keyword) {
      keyword.value = route.query.keyword
    }
  } catch (e) {
    console.error('获取词汇列表失败', e)
  } finally {
    loading.value = false
  }
}

function handleFilter() {
  currentPage.value = 1
}

function handleSearch() {
  currentPage.value = 1
}

function resetFilters() {
  filters.category = ''
  filters.scene = ''
  filters.difficulty = ''
  filters.region = ''
  keyword.value = ''
}

onMounted(fetchWords)

watch(() => route.query.keyword, (newVal) => {
  if (newVal) keyword.value = newVal
})
</script>

<style scoped lang="scss">
.dictionary-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 130px);
  
  .filter-section {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    
    .filter-title {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 16px;
      color: #333;
    }
    
    .filter-form {
      .el-form-item {
        margin-bottom: 12px;
      }
    }
    
    .search-bar {
      margin-top: 16px;
      
      .el-input {
        max-width: 400px;
      }
    }
  }
  
  .word-list {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    
    .list-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      .total {
        color: #666;
        font-size: 14px;
      }
    }
    
    .word-grid {
      &.grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 16px;
        
        .word-card {
          padding: 20px;
        }
      }
      
      &.list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        
        .word-card {
          padding: 16px 20px;
          flex-direction: row;
          align-items: center;
          
          .word-main {
            margin-bottom: 0;
            margin-right: auto;
          }
          
          .word-tags {
            margin-bottom: 0;
          }
        }
      }
      
      .word-card {
        background: #f9fafb;
        border-radius: 8px;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        gap: 10px;
        transition: all 0.3s;
        
        &:hover {
          background: #f0f2f5;
          transform: translateY(-2px);
        }
        
        .word-main {
          font-size: 20px;
          font-weight: bold;
          color: #333;
        }
        
        .word-tags {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        
        .word-meta {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #999;
          
          .difficulty {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }
    }
    
    .loading-wrapper,
    .empty-wrapper {
      padding: 40px;
    }
    
    .pagination-wrapper {
      margin-top: 20px;
      display: flex;
      justify-content: center;
    }
  }
}

@media (max-width: 768px) {
  .dictionary-page {
    .filter-section {
      .filter-form {
        display: flex;
        flex-direction: column;
        
        .el-form-item {
          margin-bottom: 8px;
        }
      }
    }
    
    .word-list .word-grid {
      &.grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }
  }
}
</style>
