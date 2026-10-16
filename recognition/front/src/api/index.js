import request from './mock'

export const wordApi = {
  getWords: (params) => request.getWords(params),
  getWordById: (id) => request.getWordById(id),
  getDialects: (wordId) => request.getDialects(wordId)
}

export const userApi = {
  login: (phone, code) => request.login(phone, code),
  register: (phone, code, password) => request.register(phone, code, password),
  logout: () => Promise.resolve({ data: true })
}

export const communityApi = {
  getPosts: (params) => request.getCommunity(params),
  likePost: (id) => Promise.resolve({ data: true }),
  commentPost: (id, content) => Promise.resolve({ data: { id: Date.now(), content } })
}

export const articleApi = {
  getArticles: () => request.getArticles()
}

export const achievementApi = {
  getAchievements: () => request.getAchievements()
}

export const uploadApi = {
  uploadDialect: (formData) => request.uploadDialect(formData)
}
