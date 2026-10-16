# 掌言手语 - 宝塔面板云服务器部署指南

> 本文件夹已包含部署到云服务器所需的全部文件。上传到服务器后按以下步骤操作。

---

## 目录结构说明

```
recognition-deploy/
├── backend/              # Flask 后端（API 服务，端口 5001）
│   ├── app.py            # 主入口
│   ├── models.py         # SQLAlchemy 数据库模型
│   ├── services.py       # 业务逻辑
│   ├── config.py         # 后端配置（密钥、数据库路径）
│   └── requirements.txt  # Python 依赖（精简版）
├── front/
│   ├── dist/             # ✅ 已构建的前端静态文件（379个文件）
│   ├── src/              # Vue 源码（可重新构建）
│   ├── package.json      # npm 依赖
│   └── vite.config.js    # Vite 配置
├── inference/            # PyTorch 模型推理（MediaPipe + CNN-LSTM）
├── models/               # 模型架构代码（CNN-LSTM / BiLSTM / GRU / Transformer）
├── data/                 # 数据预处理（84维手部关键点提取）
├── dataset/              # 词汇语料 corpus.txt
├── config/               # 训练/推理全局配置
├── start_model_service.py # 后端一键启动脚本
├── init_db.py            # 数据库初始化
└── requirements.txt      # Python 完整依赖
```

---

## 一、上传文件

将整个 `recognition-deploy` 文件夹上传到服务器，例如：

```
/www/wwwroot/csl-recognition/
```

---

## 二、后端部署

### 2.1 安装 Python 依赖

```bash
cd /www/wwwroot/csl-recognition

# 方式一：使用项目自带的启动脚本（推荐）
python start_model_service.py

# 方式二：手动安装依赖
pip install -r requirements.txt
```

> `requirements.txt` 中包含 PyTorch、MediaPipe、Flask 等核心依赖。安装后端精简依赖：
> ```bash
> pip install -r backend/requirements.txt
> ```

### 2.2 初始化数据库

```bash
cd /www/wwwroot/csl-recognition
python init_db.py
```

### 2.3 启动后端（后台运行）

```bash
# 方式一：使用项目启动脚本
python start_model_service.py &

# 方式二：使用 Gunicorn（推荐生产环境）
pip install gunicorn
gunicorn -w 2 -b 127.0.0.1:5001 backend.app:app --daemon --log-file backend.log

# 验证后端是否启动成功
curl http://127.0.0.1:5001/api/health
```

### 2.4 后端开机自启（systemd）

```bash
sudo nano /etc/systemd/system/csl-backend.service
```

写入以下内容：

```ini
[Unit]
Description=CSL Recognition Backend
After=network.target

[Service]
Type=notify
User=www
Group=www
WorkingDirectory=/www/wwwroot/csl-recognition
ExecStart=/usr/bin/python3 start_model_service.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable csl-backend
sudo systemctl start csl-backend
```

---

## 三、前端部署（Nginx + 宝塔面板）

### 3.1 宝塔面板添加站点

1. **网站** → **添加站点**
   - 域名：服务器IP（如 `1.2.3.4`）
   - 根目录：`/www/wwwroot/csl-recognition/front/dist`
   - PHP版本：**纯静态**
   - 点击 **提交**

2. 站点设置 → **伪静态**，添加：

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

3. 站点设置 → **反向代理** → **添加反向代理**：
   - 代理名称：`api-backend`
   - 目标URL：`http://127.0.0.1:5001`
   - 发送域名：`$host`

### 3.2 或手动修改 Nginx 配置

在 `/www/server/panel/vhost/nginx/` 中找到对应 `.conf` 文件，替换为以下内容：

```nginx
server {
    listen 80;
    server_name 你的服务器IP;

    root /www/wwwroot/csl-recognition/front/dist;
    index index.html;

    # Vue Router history 模式
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理到 Flask 后端
    location /api/ {
        proxy_pass http://127.0.0.1:5001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|glb|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

保存后执行：`nginx -s reload`

---

## 四、HTTPS + 域名配置（推荐）

### 4.1 申请 SSL 证书

在宝塔面板 → 网站 → 找到你的站点 → SSL → Let's Encrypt → 申请

### 4.2 修改前端 API 地址

当前 `front/dist` 中的 `baseURL` 是 `http://localhost:5001/api`，如果需要改为服务器IP，重新构建：

```bash
cd /www/wwwroot/csl-recognition/front

# 修改 src/api/index.js 中的 baseURL：
# baseURL: 'http://你的服务器IP:5001/api'
# 或如果有域名：
# baseURL: 'https://你的域名/api'

npm install
npm run build
```

> 如果使用反向代理（步骤三），前端 `baseURL` 保持 `/api` 即可，Nginx 会自动转发。

### 4.3 完整 HTTPS Nginx 配置

```nginx
server {
    listen 443 ssl http2;
    server_name 你的域名或IP;

    ssl_certificate /www/server/panel/vhost/cert/你的域名/fullchain.pem;
    ssl_certificate_key /www/server/panel/vhost/cert/你的域名/privkey.pem;

    root /www/wwwroot/csl-recognition/front/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name 你的域名或IP;
    return 301 https://$server_name$request_uri;
}
```

---

## 五、防火墙端口开放

| 端口 | 用途 | 状态 |
|------|------|------|
| 22 | SSH | 默认开放 |
| 80 | HTTP | 在云服务器控制台开放 |
| 443 | HTTPS | 在云服务器控制台开放 |
| 5001 | Flask 后端 | **仅内网访问**，不需要开放 |

---

## 六、验证部署

```bash
# 1. 检查后端
curl http://127.0.0.1:5001/api/health
# 期望：{"code": 200, "data": {"service": "CSL手语识别系统后端"}, ...}

# 2. 检查前端（通过 Nginx）
curl http://你的服务器IP/
# 期望：返回 HTML 内容

# 3. 通过 Nginx 代理访问 API
curl http://你的服务器IP/api/health
# 期望：与第1步相同
```

---

## 七、注意事项

### 7.1 模型权重文件
`models/` 目录中只有模型架构代码（.py），**模型权重文件（.pth）不在项目中**。如果需要手语识别功能，需要：
- 自行训练模型（运行 `train_isolated.py`），或
- 从原作者处获取 `.pth` 文件放入 `models/` 目录

### 7.2 上传目录权限
```bash
chmod -R 755 /www/wwwroot/csl-recognition/front/public/uploads/
chown -R www:www /www/wwwroot/csl-recognition/front/public/uploads/
```

### 7.3 JWT 密钥
生产环境请修改 `backend/config.py` 中的 `SECRET_KEY` 和 `JWT_SECRET_KEY`：
```python
SECRET_KEY = 'your-strong-random-secret-key'
JWT_SECRET_KEY = 'your-jwt-secret-key'
```

### 7.4 数据库
SQLite 数据库文件位于 `backend/csl_recognition.db`，首次运行 `python init_db.py` 后自动创建。

### 7.5 默认管理员账号
- 手机号：`13800000000`
- 密码：`admin123`
