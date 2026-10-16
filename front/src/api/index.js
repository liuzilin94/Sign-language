/**
 * API 统一导出
 */
import { api } from './request'
export { api }

// ==================== 认证模块 ====================
export const authApi = {
  login(data) {
    return api.post('/auth/login', data)
  },
  register(data) {
    return api.post('/auth/register', data)
  },
  getMe() {
    return api.get('/auth/me')
  },
  logout() {
    return api.post('/auth/logout')
  }
}

// ==================== 用户模块 ====================
export const userApi = {
  getProfile(userId) {
    return api.get(`/users/${userId}`)
  },
  uploadAvatar(formData) {
    return api.post('/users/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// ==================== 词汇模块 ====================
export const wordApi = {
  getList(params) {
    // 兼容 page/limit -> page_size
    const p = { ...params }
    if (p.limit !== undefined) { p.page_size = p.limit; delete p.limit }
    if (p.page === undefined) { p.page = 1 }
    return api.get('/words', { params: p })
  },
  getWords(params) {
    return api.get('/words', { params })
  },
  getWord(id) {
    return api.get(`/words/${id}`)
  },
  getWordById(id) {
    return api.get(`/words/${id}`)
  },
  getDialects(wordId) {
    return api.get(`/words/${wordId}/dialects`)
  }
}

// ==================== 复习模块 ====================
export const reviewApi = {
  getTodayReviews() {
    return api.get('/review/today')
  },
  completeReview(wordId, isCorrect) {
    return api.post(`/review/complete/${wordId}`, { is_correct: isCorrect })
  }
}

// ==================== 社区模块 ====================
export const communityApi = {
  getPosts(params) {
    return api.get('/posts', { params })
  },
  createPost(data, isFormData = false) {
    if (isFormData) {
      return api.post('/posts', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    return api.post('/posts', data)
  },
  deletePost(id) {
    return api.delete(`/posts/${id}`)
  },
  likePost(id) {
    return api.post(`/posts/${id}/like`)
  },
  getComments(postId, params) {
    return api.get(`/posts/${postId}/comments`, { params })
  },
  createComment(postId, content) {
    return api.post(`/posts/${postId}/comments`, { content })
  }
}

// ==================== 方言上传模块 ====================
export const dialectApi = {
  upload(formData) {
    return api.post('/dialects/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  getMyUploads() {
    return api.get('/dialects/my')
  },
  getWordDialects(wordId) {
    return api.get(`/words/${wordId}/dialects`)
  }
}

// 别名：uploadApi 指向 dialectApi（兼容旧代码）
export const uploadApi = dialectApi

// ==================== 管理员模块 ====================
export const adminApi = {
  getStats() {
    return api.get('/admin/stats')
  },
  getDialects(params) {
    return api.get('/admin/dialects', { params })
  },
  reviewDialect(dialectId, action, reason) {
    return api.post(`/admin/dialects/${dialectId}/review`, { action, reason })
  },
  getUsers(params) {
    return api.get('/admin/users', { params })
  },
  updateUserRole(userId, role) {
    return api.put(`/admin/users/${userId}/role`, { role })
  }
}

// ==================== 手语识别模块 ====================
export const recognitionApi = {
  initModel() {
    return api.post('/init-isolated', { model_type: 'cnn_lstm' })
  },
  getVocabulary() {
    return api.get('/vocabulary')
  },
  predict(videoBlob, targetIndex) {
    const formData = new FormData()
    formData.append('video', videoBlob, 'recording.webm')
    formData.append('target_index', targetIndex.toString())
    return api.post('/predict-isolated', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// ==================== 统计模块 ====================
export const statsApi = {
  getOverview() {
    return api.get('/stats/overview')
  },
  getChart(period = 'week') {
    return api.get('/stats/chart', { params: { period } })
  },
  getCalendar(year, month) {
    return api.get('/stats/calendar', { params: { year, month } })
  },
  getRadar() {
    return api.get('/stats/radar')
  },
  getRanking(limit = 10) {
    return api.get('/stats/ranking', { params: { limit } })
  }
}

// ==================== 学习中心模块 ====================
export { learningApi } from './learning'

// ==================== 竞技场模块 ====================
export const arenaApi = {
  start() {
    return api.post('/arena/start')
  },
  verify(wordId, stage, answer) {
    return api.post('/arena/verify', {
      word_id: wordId,
      stage: stage,
      answer: answer
    })
  },
  finish(answers) {
    return api.post('/arena/finish', { answers })
  }
}

// ==================== 积分与等级模块 ====================
export const pointsApi = {
  getLevelInfo() {
    return api.get('/points/level')
  },
  addPoints(points, source) {
    return api.post('/points/add', { points, source })
  }
}
