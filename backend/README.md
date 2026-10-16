# CSL手语识别系统 - 后端API服务

基于Flask + SQLAlchemy的RESTful API服务

## 快速开始

### 1. 环境准备
```bash
cd recognition/backend
python -m venv venv
# Windows
venv\Scripts\Activate.ps1
# 或 Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
python init_db.py
```

### 3. 启动服务
```bash
python app.py
```

服务将在 `http://localhost:5001` 启动

## 项目结构

```
backend/
├── app.py                  # Flask主应用入口
├── config.py               # 配置（数据库、JWT等）
├── requirements.txt         # Python依赖
├── init_db.py              # 数据库初始化脚本
├── schema.sql              # 建表SQL脚本
├── models/                 # 数据模型（SQLAlchemy）
│   ├── __init__.py
│   ├── user.py
│   ├── word.py
│   ├── learning.py
│   ├── review.py
│   ├── post.py
│   ├── comment.py
│   ├── dialect.py
│   └── study.py
├── api/                    # API路由（蓝图）
│   ├── __init__.py
│   ├── auth.py            # 认证（注册/登录）
│   ├── words.py           # 词汇管理
│   ├── learning.py        # 学习记录
│   ├── review.py          # 复习系统
│   ├── posts.py           # 社区动态
│   ├── comments.py        # 评论
│   ├── dialects.py        # 方言上传
│   ├── stats.py           # 学习统计
│   ├── tasks.py           # 每日任务
│   └── achievements.py    # 成就系统
├── services/              # 业务逻辑层
│   ├── __init__.py
│   ├── auth_service.py
│   ├── word_service.py
│   ├── learning_service.py
│   ├── review_service.py  # 艾宾浩斯算法
│   ├── community_service.py
│   └── stats_service.py
├── utils/                 # 工具函数
│   ├── __init__.py
│   ├── auth.py           # JWT处理
│   ├── validators.py     # 参数验证
│   └── helpers.py        # 辅助函数
└── migrations/           # 数据库迁移（可选）
    ├── __init__.py
    └── versions/

```

## API文档

完整API接口请参考：`../API_DOCUMENTATION.md`

## 数据库设计

详细设计请参考：`../DATABASE_DESIGN.md`

## 核心功能

- ✅ 用户注册/登录（JWT认证）
- ✅ 词汇管理（从corpus.txt读取）
- ✅ 学习记录（练习历史、收藏、笔记）
- ✅ 艾宾浩斯复习算法
- ✅ 社区动态（发布、点赞、评论）
- ✅ 方言视频上传与审核
- ✅ 学习统计与图表
- ✅ 每日任务系统
- ✅ 成就系统

## 开发规范

### 响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 错误处理
```json
{
  "code": 40001,
  "message": "参数错误",
  "data": null
}
```

### 认证方式
```
Authorization: Bearer <jwt_token>
```

## 后续扩展

- [ ] 管理员后台
- [ ] 消息通知系统
- [ ] 实时聊天（WebSocket）
- [ ] 视频审核（AI自动审核）
- [ ] 数据导出（Excel/PDF）
- [ ] 缓存优化（Redis）
- [ ] 文件存储迁移（OSS）
