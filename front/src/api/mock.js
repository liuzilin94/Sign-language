const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjM1IiByPSIyNSIgZmlsbD0iI2Q0ZDRkNCIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNzUiIHI9IjMwIiBmaWxsPSIjZDRkNGQ0Ii8+PC9zdmc+'

const videoWords = ['冷', '厚', '去', '多', '小', '少', '属于', '快', '慢', '晒', '来', '热', '瘦', '短', '矮', '细', '胖', '薄', '远', '醒', '长']

const mockWords = [
  { id: 1, word: '你好', category: '基础', scene: '日常问候', difficulty: 1, region: '全国通用', videoUrl: '' },
  { id: 2, word: '谢谢', category: '基础', scene: '日常问候', difficulty: 1, region: '全国通用', videoUrl: '' },
  { id: 3, word: '再见', category: '基础', scene: '日常问候', difficulty: 1, region: '全国通用', videoUrl: '' },
  { id: 4, word: '对不起', category: '基础', scene: '日常问候', difficulty: 2, region: '全国通用', videoUrl: '' },
  { id: 5, word: '请', category: '基础', scene: '日常问候', difficulty: 2, region: '全国通用', videoUrl: '' },
  { id: 6, word: '家庭', category: '生活', scene: '家庭', difficulty: 2, region: '北方', videoUrl: '' },
  { id: 7, word: '爸爸', category: '生活', scene: '家庭', difficulty: 1, region: '全国通用', videoUrl: '' },
  { id: 8, word: '妈妈', category: '生活', scene: '家庭', difficulty: 1, region: '全国通用', videoUrl: '' },
  { id: 9, word: '吃饭', category: '生活', scene: '饮食', difficulty: 2, region: '全国通用', videoUrl: '' },
  { id: 10, word: '喝水', category: '生活', scene: '饮食', difficulty: 1, region: '全国通用', videoUrl: '' },
  { id: 11, word: '工作', category: '社会', scene: '职业', difficulty: 2, region: '全国通用', videoUrl: '' },
  { id: 12, word: '学习', category: '社会', scene: '教育', difficulty: 2, region: '全国通用', videoUrl: '' },
  { id: 13, word: '医生', category: '社会', scene: '职业', difficulty: 2, region: '北方', videoUrl: '' },
  { id: 14, word: '老师', category: '社会', scene: '职业', difficulty: 2, region: '全国通用', videoUrl: '' },
  { id: 15, word: '朋友', category: '社交', scene: '人际', difficulty: 2, region: '全国通用', videoUrl: '' },
  { id: 16, word: '帮助', category: '社交', scene: '人际', difficulty: 3, region: '全国通用', videoUrl: '' },
  { id: 17, word: '喜欢', category: '情感', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '' },
  { id: 18, word: '爱', category: '情感', scene: '表达', difficulty: 3, region: '全国通用', videoUrl: '' },
  { id: 19, word: '快乐', category: '情感', scene: '表达', difficulty: 2, region: '南方', videoUrl: '' },
  { id: 20, word: '电脑', category: '科技', scene: '工具', difficulty: 3, region: '全国通用', videoUrl: '' },
  { id: 21, word: '冷', category: '属性', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/冷.mp4' },
  { id: 22, word: '厚', category: '属性', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/厚.mp4' },
  { id: 23, word: '去', category: '方位', scene: '表达', difficulty: 1, region: '全国通用', videoUrl: '/videos/去.mp4' },
  { id: 24, word: '多', category: '尺寸', scene: '表达', difficulty: 1, region: '全国通用', videoUrl: '/videos/多.mp4' },
  { id: 25, word: '小', category: '尺寸', scene: '表达', difficulty: 1, region: '全国通用', videoUrl: '/videos/小.mp4' },
  { id: 26, word: '少', category: '尺寸', scene: '表达', difficulty: 1, region: '全国通用', videoUrl: '/videos/少.mp4' },
  { id: 27, word: '属于', category: '属性', scene: '表达', difficulty: 3, region: '全国通用', videoUrl: '/videos/属于.mp4' },
  { id: 28, word: '快', category: '快慢', scene: '表达', difficulty: 1, region: '全国通用', videoUrl: '/videos/快.mp4' },
  { id: 29, word: '慢', category: '快慢', scene: '表达', difficulty: 1, region: '全国通用', videoUrl: '/videos/慢.mp4' },
  { id: 30, word: '晒', category: '方位', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/晒.mp4' },
  { id: 31, word: '来', category: '方位', scene: '表达', difficulty: 1, region: '全国通用', videoUrl: '/videos/来.mp4' },
  { id: 32, word: '热', category: '温度', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/热.mp4' },
  { id: 33, word: '瘦', category: '胖瘦', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/瘦.mp4' },
  { id: 34, word: '短', category: '尺寸', scene: '表达', difficulty: 1, region: '全国通用', videoUrl: '/videos/短.mp4' },
  { id: 35, word: '矮', category: '高度', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/矮.mp4' },
  { id: 36, word: '细', category: '粗细', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/细.mp4' },
  { id: 37, word: '胖', category: '胖瘦', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/胖.mp4' },
  { id: 38, word: '薄', category: '粗细', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/薄.mp4' },
  { id: 39, word: '远', category: '高度', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/远.mp4' },
  { id: 40, word: '醒', category: '状态', scene: '表达', difficulty: 2, region: '全国通用', videoUrl: '/videos/醒.mp4' },
  { id: 41, word: '长', category: '尺寸', scene: '表达', difficulty: 1, region: '全国通用', videoUrl: '/videos/长.mp4' }
]

const mockDialects = [
  { id: 1, wordId: 1, region: '北京', videoUrl: '', status: 'approved' },
  { id: 2, wordId: 1, region: '上海', videoUrl: '', status: 'approved' },
  { id: 3, wordId: 2, region: '广东', videoUrl: '', status: 'pending' },
  { id: 4, wordId: 6, region: '东北', videoUrl: '', status: 'approved' },
  { id: 5, wordId: 17, region: '四川', videoUrl: '', status: 'rejected' }
]

const mockCommunity = [
  { id: 1, userId: 1, username: '手语达人小王', avatar: defaultAvatar, content: '今天学习了十个常用手语词汇，感觉很有成就感！', images: [], likes: 128, comments: 23, createTime: '2小时前' },
  { id: 2, userId: 2, username: '聋人朋友', avatar: defaultAvatar, content: '分享一个学习手语的小技巧给大家', images: [], likes: 256, comments: 45, createTime: '5小时前' },
  { id: 3, userId: 3, username: '手语教师李老师', avatar: defaultAvatar, content: '新手入门必看！手语基础动作分解演示', images: [], likes: 512, comments: 89, createTime: '1天前' }
]

const mockArticles = [
  { id: 1, title: '手语的起源与发展', summary: '了解手语从手势语到规范化的发展历程', views: 1234, createTime: '2024-01-15' },
  { id: 2, title: '中国手语与地方手语的区别', summary: '全国通用手语与各地方言手语的异同', views: 2567, createTime: '2024-01-20' },
  { id: 3, title: '手语在教育中的应用', summary: '如何用手语辅助特殊教育', views: 3456, createTime: '2024-02-01' },
  { id: 4, title: '聋人文化与手语', summary: '探索聋人社区的文化内涵', views: 1890, createTime: '2024-02-10' }
]

const mockAchievements = [
  { id: 1, name: '初学者', description: '完成首个词汇学习', icon: '🌱', requirement: '学习10个词汇', progress: 100 },
  { id: 2, name: '每日打卡', description: '连续7天学习', icon: '📅', requirement: '连续学习7天', progress: 60 },
  { id: 3, name: '手语达人', description: '掌握100个词汇', icon: '🎯', requirement: '学习100个词汇', progress: 45 },
  { id: 4, name: '方言专家', description: '上传并通过5个方言视频', icon: '🏆', requirement: '通过5个方言审核', progress: 20 },
  { id: 5, name: '学习之星', description: '学习时长超过100小时', icon: '⭐', requirement: '学习100小时', progress: 35 }
]

export default {
  getWords: (params = {}) => {
    let result = [...mockWords]
    if (params.category) result = result.filter(w => w.category === params.category)
    if (params.scene) result = result.filter(w => w.scene === params.scene)
    if (params.difficulty) result = result.filter(w => w.difficulty === params.difficulty)
    if (params.region) result = result.filter(w => w.region === params.region || w.region === '全国通用')
    if (params.keyword) result = result.filter(w => w.word.includes(params.keyword))
    return Promise.resolve({ data: result })
  },
  
  getWordById: (id) => {
    const word = mockWords.find(w => w.id === Number(id))
    const dialects = mockDialects.filter(d => d.wordId === Number(id))
    return Promise.resolve({ data: { ...word, dialects } })
  },
  
  getDialects: (wordId) => {
    return Promise.resolve({ data: mockDialects.filter(d => d.wordId === Number(wordId)) })
  },
  
  getCommunity: (params = {}) => {
    return Promise.resolve({ data: mockCommunity })
  },
  
  getArticles: () => {
    return Promise.resolve({ data: mockArticles })
  },
  
  getAchievements: () => {
    return Promise.resolve({ data: mockAchievements })
  },
  
  login: (phone, code) => {
    if (phone && code) {
      return Promise.resolve({
        data: {
          token: 'mock_token_' + Date.now(),
          userInfo: {
            id: 1,
            username: '手语学习者',
            phone: phone,
            avatar: defaultAvatar,
            level: 5,
            exp: 1250,
            points: 380
          }
        }
      })
    }
    return Promise.reject(new Error('登录失败'))
  },
  
  register: (phone, code, password) => {
    return Promise.resolve({
      data: {
        token: 'mock_token_' + Date.now(),
        userInfo: {
          id: 1,
          username: '新用户',
          phone: phone,
          avatar: defaultAvatar,
          level: 1,
          exp: 0,
          points: 100
        }
      }
    })
  },
  
  uploadDialect: (formData) => {
    return Promise.resolve({
      data: {
        id: Date.now(),
        status: 'pending'
      }
    })
  }
}
