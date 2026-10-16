"""环境检查脚本"""
import sys
import os
import time

print("=" * 60)
print("CSL 手语识别系统 - 环境检查")
print("=" * 60)

# 1. Python环境
print("\n[1] Python 环境")
print(f"    Python版本: {sys.version}")
print(f"    Python路径: {sys.executable}")

# 2. 依赖检查
print("\n[2] Python 依赖")
deps = [
    ('Flask', 'flask'),
    ('SQLAlchemy', 'sqlalchemy'),
    ('Flask-SQLAlchemy', 'flask_sqlalchemy'),
    ('Flask-JWT-Extended', 'flask_jwt_extended'),
    ('Flask-CORS', 'flask_cors'),
    ('bcrypt', 'bcrypt'),
    ('PyTorch', 'torch'),
    ('MediaPipe', 'mediapipe'),
    ('pytest', 'pytest'),
    ('numpy', 'numpy'),
    ('pandas', 'pandas'),
    ('Pillow', 'PIL'),
    ('OpenCV', 'cv2'),
]

for name, module in deps:
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"    {name}: {version} OK")
    except ImportError:
        print(f"    {name}: NOT FOUND")

# 3. 文件检查
print("\n[3] 关键文件检查")
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files_to_check = [
    (os.path.join(project_root, 'backend', 'app.py'), '后端入口'),
    (os.path.join(project_root, 'backend', 'models.py'), '数据模型'),
    (os.path.join(project_root, 'inference', 'predictor.py'), '预测器'),
    (os.path.join(project_root, 'dataset', 'corpus.txt'), '词汇表'),
    (os.path.join(project_root, 'config', 'config.py'), '配置文件'),
]

for filepath, desc in files_to_check:
    status = "OK" if os.path.exists(filepath) else "NOT FOUND"
    print(f"    {desc}: {status}")

# 4. 数据库检查
print("\n[4] 数据库检查")
db_path = os.path.join(project_root, 'backend', 'csl_recognition.db')
if os.path.exists(db_path):
    print(f"    数据库文件: OK ({db_path})")
    size = os.path.getsize(db_path)
    print(f"    数据库大小: {size / 1024:.2f} KB")
else:
    print(f"    数据库文件: NOT FOUND (需要初始化)")

# 5. 模型文件检查
print("\n[5] 模型文件检查")
models_dir = os.path.join(project_root, 'models')
if os.path.exists(models_dir):
    pth_files = [f for f in os.listdir(models_dir) if f.endswith('.pth')]
    if pth_files:
        for f in pth_files:
            fpath = os.path.join(models_dir, f)
            size = os.path.getsize(fpath)
            print(f"    {f}: {size / 1024 / 1024:.2f} MB OK")
    else:
        print(f"    .pth模型文件: NOT FOUND")
else:
    print(f"    models目录: NOT FOUND")

# 6. 视频目录检查
print("\n[6] 视频目录检查")
video_dir = os.path.join(project_root, 'video')
if os.path.exists(video_dir):
    mp4_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]
    print(f"    视频目录: OK")
    print(f"    视频数量: {len(mp4_files)}")
else:
    print(f"    视频目录: NOT FOUND")

# 7. 前端检查
print("\n[7] 前端检查")
front_dir = os.path.join(project_root, 'front')
if os.path.exists(front_dir):
    print(f"    前端目录: OK")
    pkg_json = os.path.join(front_dir, 'package.json')
    if os.path.exists(pkg_json):
        print(f"    package.json: OK")
    node_modules = os.path.join(front_dir, 'node_modules')
    if os.path.exists(node_modules):
        print(f"    node_modules: OK")
    else:
        print(f"    node_modules: NOT FOUND (需要npm install)")
else:
    print(f"    前端目录: NOT FOUND")

# 8. CUDA检查
print("\n[8] GPU支持检查")
try:
    import torch
    if torch.cuda.is_available():
        print(f"    CUDA可用: OK")
        print(f"    GPU数量: {torch.cuda.device_count()}")
        print(f"    GPU名称: {torch.cuda.get_device_name(0)}")
    else:
        print(f"    CUDA: NOT AVAILABLE (使用CPU)")
except Exception as e:
    print(f"    CUDA检查失败: {e}")

print("\n" + "=" * 60)
print("环境检查完成")
print("=" * 60)
