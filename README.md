# 掌言手语 — 中国手语学习与识别平台

## 环境要求

- Python 3.10+
- Node.js 18+
- npm

## 环境配置

```bash
# 后端依赖
cd recognition
pip install -r requirements.txt

# 前端依赖
cd front
npm install
```

## 启动

**1. 初始化数据库**
```bash
cd recognition
python init_db.py
```

**2. 启动后端**（端口 5001）
```bash
cd recognition
python start_model_service.py
```

**3. 启动前端**（端口 5173）
```bash
cd recognition/front
npm run dev
```

访问 `http://localhost:5173`

## 管理员登录

- 手机号：`13800000000`
- 密码：`admin123`

登录后在导航栏可见"管理"入口。

## 项目结构

```
recognition/
├── front/              # Vue 3 前端
├── backend/            # Flask 后端 API
├── models/             # PyTorch AI 模型
├── inference/          # 模型推理核心
├── dataset/            # 语料数据
├── features/           # 特征提取
├── trainers/           # 模型训练脚本
├── ui_plus.py          # Flask + PyQt5 桌面客户端
└── requirements.txt     # Python 依赖
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Three.js + ECharts |
| 后端 | Flask + Flask-CORS + Flask-JWT-Extended |
| 数据库 | SQLite（SQLAlchemy ORM） |
| AI | PyTorch + MediaPipe + OpenCV |
