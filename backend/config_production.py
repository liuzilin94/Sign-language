"""
配置管理 - 生产环境版本
使用时只需修改本文件中的路径配置，无需改动其他代码
复制到 backend/config.py 使用，或设置环境变量切换
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class ProductionConfig:
    """生产环境配置"""

    # ===== 修改这里 =====
    # 服务器上项目的根目录（绝对路径）
    PROJECT_ROOT = '/www/wwwroot/csl-recognition'

    # Flask 密钥（生产环境请改为复杂随机字符串）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-to-a-strong-random-secret-key'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(PROJECT_ROOT, 'backend', 'csl_recognition.db')}"

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'change-this-to-a-strong-random-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_IDENTITY_CLAIMS = 'sub'
    JWT_JSON_NOREFRESHER = True

    # 文件上传 - 改为绝对路径
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'front', 'public', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'jpg', 'jpeg', 'png', 'webm'}

    # CORS - 允许所有来源（生产环境可限制为具体域名）
    CORS_ORIGINS = ['*']


# 如果设置环境变量 CONFIG_ENV=production 则自动使用生产配置
if os.environ.get('CONFIG_ENV') == 'production':
    Config = ProductionConfig
else:
    # 导入原有开发配置
    from . import Config as DevConfig
    Config = DevConfig
