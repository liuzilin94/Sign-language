"""
配置管理 - 简化版
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-csl-2025'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'csl_recognition.db')
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-csl-2025'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    # 确保identity作为字符串存储
    JWT_IDENTITY_CLAIMS = 'sub'
    JWT_JSON_NOREFRESHER = True  # 强制JSON序列化
    
    # 文件上传 - 使用与Nginx root一致的路径
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'frontend', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'jpg', 'jpeg', 'png'}
    
    # CORS
    CORS_ORIGINS = [
        'http://localhost:5173', 'http://localhost:8080',
        'http://127.0.0.1:5173', 'http://localhost:3000',
        'http://localhost:3001', 'http://localhost:3002',
        'http://localhost:3003', 'http://localhost:3004',
        'http://localhost:3005', 'http://localhost:3006',
        'http://localhost:3007', 'http://localhost:3011',
        'http://127.0.0.1:5000', 'http://localhost:5000',
        'http://127.0.0.1:5001', 'http://localhost:5001',
        'http://127.0.0.1:3000', 'http://localhost:3000',
    ]
