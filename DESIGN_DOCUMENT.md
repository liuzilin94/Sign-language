# 掌言手语 — 设计说明

## 目标

帮助手语学习者通过 AI 练习、视觉反馈、规律复习掌握中国手语（CSL）。

## 学习路径

学 → 练 → 测 → 复习，四环节闭环，用户无需切换外部工具。

## 架构

```
浏览器 (Vue 3) → Axios → Flask 后端 (:5001)
                        ├─ JWT 认证
                        ├─ SQLite 数据库
                        ├─ 文件存储
                        └─ AI 手语识别
                             OpenCV → MediaPipe 84维关键点 → CNN-LSTM → 置信度结果
```

## AI 识别流程

摄像头录制 3 秒 → POST /api/predict-isolated → OpenCV 逐帧提取 → MediaPipe 84维关键点 → 30帧×84维时序张量 → CNN-LSTM 推理 → 置信度 > 50% 视为正确

## 数据模型

| 模型 | 作用 |
|------|------|
| User | 用户信息、积分、等级 |
| Word | 词汇定义与分类 |
| LearningRecord | 学习行为记录 |
| ReviewSchedule | 艾宾浩斯复习计划 |
| DialectUpload | 方言视频上传与审核 |
| Post / Comment | 社区动态 |

## 技术选型

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 可视化 | Three.js（数字人）+ ECharts（学习数据）|
| 后端 | Flask + Flask-JWT-Extended |
| 数据库 | SQLite（SQLAlchemy） |
| AI | PyTorch CNN-LSTM + MediaPipe + OpenCV |

## 关键决策

- **MediaPipe**：开箱即用 84 维手部关键点，对光照和遮挡比纯骨骼跟踪更鲁棒
- **艾宾浩斯复习**：间隔重复自动安排复习词条，无需用户手动规划
- **方言审核**：众包视频质量不一，管理员审核机制保障词典内容准确性
