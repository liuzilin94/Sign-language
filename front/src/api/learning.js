/**
 * 学习中心 API
 */
import { api } from './request'

export const learningApi = {
  // ==================== 基础学习记录（从 index.js 合并） ====================
  createRecord(data) {
    return api.post('/learning/records', data)
  },
  getRecords() {
    return api.get('/learning/records')
  },
  getRecord(wordId) {
    return api.get(`/learning/records/${wordId}`)
  },
  updateRecord(wordId, data) {
    return api.put(`/learning/records/${wordId}`, data)
  },

  // ==================== 学习中心功能 ====================
  /**
   * 获取学习设置
   */
  getSettings() {
    return api.get('/learning/settings')
  },

  /**
   * 更新学习设置
   * @param {Object} data - { daily_new_words, daily_review_words }
   */
  updateSettings(data) {
    return api.put('/learning/settings', data)
  },

  /**
   * 获取今日学习计划
   */
  getTodayPlan() {
    return api.get('/learning/today-plan')
  },

  /**
   * 重置今日学习计划（当设置改变时使用）
   */
  resetTodayPlan() {
    return api.post('/learning/today-plan/reset')
  },

  /**
   * 开始学习/复习会话
   * @param {string} sessionType - 'learn' | 'review'
   */
  startSession(sessionType) {
    return api.post('/learning/start-session', { session_type: sessionType })
  },

  /**
   * 提交答案
   * @param {Object} data - { word_id, session_type, stage, answer }
   */
  submitAnswer(data) {
    return api.post('/learning/submit-answer', data)
  },

  /**
   * 获取学习进度摘要
   */
  getProgress() {
    return api.get('/learning/progress')
  },

  /**
   * 获取词汇识别信息
   * @param {number} wordId - 词汇ID
   */
  getRecognitionInfo(wordId) {
    return api.get(`/learning/recognition-info/${wordId}`)
  }
}
