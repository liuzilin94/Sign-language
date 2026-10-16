# 掌言手语 - 阿里云部署指南
# 服务器 IP: 101.201.59.20

## 一、部署包内容

需要上传到服务器的文件：
```
csl-recognition/
├── backend/                    # Flask 后端
│   ├── app.py                 # 主应用
│   ├── models.py              # 数据库模型
│   ├── services.py            # 业务逻辑
│   ├── config.py              # 配置文件
│   ├── csl_recognition.db     # 数据库文件（首次运行后自动创建）
│   └── requirements.txt       # Python 依赖
│
├── front/dist/                 # 前端构建文件（已压缩）
│   ├── index.html
│   ├── assets/
│   └── ...
│
├── models/                     # AI 模型
│   └── best_isolated_model.pth
│
├── dataset/                    # 词汇数据
│   └── corpus.txt
│
├── inference/                  # 推理模块
│   └── predictor.py
│
├── config/                     # 配置文件
│   └── config.py
│
├── requirements.txt            # Python 完整依赖
├── start_model_service.py      # 后端启动脚本
├── init_db.py                  # 数据库初始化
└── DEPLOY.md                   # 本文件
```

## 二、服务器端操作步骤

### 2.1 创建网站目录

```bash
# 通过 SSH 连接到服务器
ssh root@101.201.59.20

# 创建项目目录
mkdir -p /www/wwwroot/csl-recognition
cd /www/wwwroot/csl-recognition
```

### 2.2 上传文件

使用以下方式之一上传文件：
- **方式一**：SCP 命令（本地执行）
```bash
# 上传整个项目（需要先打包）
cd E:\csl-recognition\recognition-deploy
scp -r backend root@101.201.59.20:/www/wwwroot/csl-recognition/
scp -r front/dist root@101.201.59.20:/www/wwwroot/csl-recognition/
scp -r models root@101.201.59.20:/www/wwwroot/csl-recognition/
scp -r dataset root@101.201.59.20:/www/wwwroot/csl-recognition/
scp -r inference root@101.201.59.20:/www/wwwroot/csl-recognition/
scp -r config root@101.201.59.20:/www/wwwroot/csl-recognition/
scp requirements.txt start_model_service.py init_db.py root@101.201.59.20:/www/wwwroot/csl-recognition/
```

- **方式二**：使用 WinSCP / FileZilla 图形化工具

### 2.3 安装 Python 依赖

```bash
cd /www/wwwroot/csl-recognition

# 安装 Python 依赖（可能需要几分钟）
pip install -r requirements.txt
```

### 2.4 安装 Nginx

```bash
# Ubuntu/Debian
apt update
apt install nginx -y

# CentOS
yum install nginx -y
```

### 2.5 配置 Nginx

```bash
# 创建 Nginx 配置文件
nano /etc/nginx/sites-available/csl-recognition
```

写入以下内容：

```nginx
server {
    listen 80;
    server_name 101.201.59.20;

    root /www/wwwroot/csl-recognition/front/dist;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Vue Router History 模式
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理到 Flask 后端
    location /api/ {
        proxy_pass http://127.0.0.1:5001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        
        # 文件上传大小限制
        client_max_body_size 100m;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|glb|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 上传目录（如果有）
    location /uploads/ {
        alias /www/wwwroot/csl-recognition/front/public/uploads/;
        expires 7d;
    }

    # 日志
    access_log /var/log/nginx/csl-access.log;
    error_log /var/log/nginx/csl-error.log;
}
```

启用站点：

```bash
# Ubuntu/Debian
ln -s /etc/nginx/sites-available/csl-recognition /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# CentOS
cp /etc/nginx/sites-available/csl-recognition /etc/nginx/conf.d/
nginx -t
systemctl reload nginx
```

### 2.6 初始化数据库

```bash
cd /www/wwwroot/csl-recognition
python init_db.py
```

### 2.7 启动后端服务

```bash
# 方式一：直接启动（开发模式）
python start_model_service.py

# 方式二：使用 nohup 后台运行（推荐生产环境）
nohup python start_model_service.py > backend.log 2>&1 &

# 方式三：使用 systemd 服务（推荐）
```

### 2.8 配置 systemd 服务（推荐）

```bash
# 创建服务文件
nano /etc/systemd/system/csl-backend.service
```

写入：

```ini
[Unit]
Description=CSL Sign Language Recognition Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/www/wwwroot/csl-recognition
ExecStart=/usr/bin/python3 /www/wwwroot/csl-recognition/start_model_service.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
systemctl daemon-reload
systemctl enable csl-backend
systemctl start csl-backend
systemctl status csl-backend
```

## 三、防火墙配置

```bash
# 开放端口
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp   # HTTPS（可选）
ufw allow 22/tcp    # SSH

# 或使用阿里云安全组
# 在阿里云控制台 → 安全组 → 入方向规则添加：
# - 80端口 HTTP
# - 443端口 HTTPS（可选）
```

## 四、验证部署

### 4.1 检查后端

```bash
curl http://127.0.0.1:5001/api/health
```

预期响应：
```json
{"code": 200, "data": {"service": "CSL手语识别系统后端", "status": "healthy"}, "message": "success"}
```

### 4.2 检查前端

在浏览器访问：`http://101.201.59.20`

### 4.3 测试 API

```bash
curl http://101.201.59.20/api/health
```

## 五、常用命令

```bash
# 查看后端日志
journalctl -u csl-backend -f

# 重启后端
systemctl restart csl-backend

# 停止后端
systemctl stop csl-backend

# 查看 Nginx 日志
tail -f /var/log/nginx/csl-access.log
```

## 六、默认账号

- **管理员账号**：13800000000
- **密码**：admin123
- **登录后**：导航栏可见"管理"入口

## 七、问题排查

### 后端无法启动

```bash
# 查看错误日志
cd /www/wwwroot/csl-recognition
python start_model_service.py
```

### 前端无法访问

```bash
# 检查 Nginx 状态
systemctl status nginx

# 查看 Nginx 错误日志
tail -f /var/log/nginx/csl-error.log
```

### API 代理失败

```bash
# 检查后端是否运行
curl http://127.0.0.1:5001/api/health

# 检查 Nginx 配置
nginx -t
```
