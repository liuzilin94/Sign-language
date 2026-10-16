"""
Flask主应用 - 精简版MVP
整合所有API路由、中间件和配置
"""
import os
import sys
import json
import tempfile
from datetime import datetime, date
import numpy as np
from flask import Flask, request, jsonify, send_file, current_app
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# 导入配置（Flask配置和模型配置）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.config import Config as ModelConfig  # 模型配置
from backend.config import Config as FlaskConfig  # Flask应用配置

# 导入数据库模型和服务
from backend.models import db, User, Word, LearningRecord, ReviewSchedule, DialectUpload, LearningProgress, UserLearningSettings, DailyPlan, LearningChoiceOptions, StudyStat, Post
from backend.services import AuthService, WordService, LearningService, ReviewService, CommunityService, DialectService, StatsService, PointsService, ArenaService
from backend.learning_service import LearningCenterService
from backend.routes.learning import learning_bp

# ==================== 应用初始化 ====================
app = Flask(__name__)
app.config.from_object(FlaskConfig)

# 初始化扩展
CORS(app, origins=FlaskConfig.CORS_ORIGINS, supports_credentials=True)
db.init_app(app)
jwt = JWTManager(app)

# 注册蓝图
app.register_blueprint(learning_bp)

# 确保上传目录存在
os.makedirs(FlaskConfig.UPLOAD_FOLDER, exist_ok=True)

# ==================== 辅助函数 ====================
def validate_phone(phone):
    """验证手机号格式"""
    import re
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_password(password):
    """验证密码强度"""
    return len(password) >= 6

def success_response(data=None, message="success", code=200, status_code=200):
    """成功响应"""
    response = jsonify({'code': code, 'message': message, 'data': data, 'timestamp': datetime.now().timestamp()})
    return response, status_code

def error_response(message, code=400, error_code=None):
    """错误响应"""
    return jsonify({
        'code': error_code or code,
        'message': message,
        'data': None,
        'timestamp': datetime.now().timestamp()
    }), code

# ==================== 视频文件服务 ====================
@app.route('/videos/<path:filename>')
def serve_video(filename):
    """提供视频文件访问 - 支持中文文件名"""
    possible_dirs = [
        os.path.join(os.path.dirname(app.root_path), 'front', 'public', 'videos'),
        os.path.join(os.path.dirname(app.root_path), 'video'),
        os.path.join(os.path.dirname(app.root_path), 'recognition', 'front', 'public', 'videos'),
        os.path.join(os.path.dirname(app.root_path), 'server-deploy', 'front', 'dist', 'videos'),
        os.path.join(os.path.dirname(app.root_path), 'deploy-package', 'front', 'dist', 'videos'),
    ]

    from urllib.parse import unquote
    decoded_filename = unquote(filename)

    print(f"[Video Request] filename: {filename}, decoded: {decoded_filename}")

    for video_dir in possible_dirs:
        if os.path.exists(video_dir):
            try:
                for f in os.listdir(video_dir):
                    if f.lower().endswith('.mp4') and decoded_filename.lower().endswith('.mp4'):
                        f_base = f[:-4]
                        req_base = decoded_filename[:-4]

                        if f_base == req_base:
                            print(f"[Video Match] Found in {video_dir}: {f}")
                            return send_file(os.path.join(video_dir, f), mimetype='video/mp4')

                        if f_base.lower() == req_base.lower():
                            print(f"[Video Match] Found (case-insensitive) in {video_dir}: {f}")
                            return send_file(os.path.join(video_dir, f), mimetype='video/mp4')
            except Exception as e:
                print(f"[Video Dir Error] {video_dir}: {e}")

    print(f"[Video Not Found] filename: {filename}, decoded: {decoded_filename}")
    return jsonify({'error': 'Video not found'}), 404

# ==================== 错误处理 ====================
@app.errorhandler(400)
def bad_request(e):
    return error_response("参数错误", 400, 40001)

@app.errorhandler(404)
def not_found(e):
    return error_response("资源不存在", 404, 40401)

@app.errorhandler(401)
def unauthorized(e):
    return error_response("未授权", 401, 40101)

@app.errorhandler(500)
def server_error(e):
    return error_response("服务器内部错误", 500, 50001)

# ==================== 健康检查 ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return success_response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'CSL手语识别系统后端'
    })

# ==================== 认证模块 ====================
def _safe_trim(value, default=''):
    """安全地去除字符串两端空白，处理非字符串类型"""
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据格式错误", 400, 40001)

        username = _safe_trim(data.get('username', ''))
        phone = _safe_trim(data.get('phone', ''))
        password = _safe_trim(data.get('password', ''))

        # 参数验证
        if not all([username, phone, password]):
            return error_response("参数不完整", 400, 40001)

        if len(username) < 2:
            return error_response("用户名至少2个字符", 400, 40002)

        if not validate_phone(phone):
            return error_response("手机号格式错误", 400, 40003)

        if not validate_password(password):
            return error_response("密码至少6位", 400, 40004)

        # 注册
        user, msg = AuthService.register(username, phone, password)
        if not user:
            return error_response(msg, 409, 40901)

        # 生成JWT token (注册后自动登录)
        access_token = create_access_token(identity=str(user.id))

        return success_response({
            'user_id': user.id,
            'username': user.username,
            'phone': user.phone,
            'token': access_token,
            'token_type': 'Bearer',
            'expires_in': 604800,  # 7天
            'user_info': user.to_dict()
        }, msg, 201, 201)

    except Exception as e:
        return error_response(f"注册失败: {str(e)}", 500)

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据格式错误", 400, 40001)

        phone = _safe_trim(data.get('phone', ''))
        password = _safe_trim(data.get('password', ''))

        if not all([phone, password]):
            return error_response("参数不完整", 400, 40001)

        # 登录验证
        user, msg = AuthService.login(phone, password)
        if not user:
            return error_response(msg, 401, 40101)

        # 生成JWT token (identity必须是字符串)
        access_token = create_access_token(identity=str(user.id))

        return success_response({
            'token': access_token,
            'token_type': 'Bearer',
            'expires_in': 604800,  # 7天
            'user_info': user.to_dict()
        }, msg)

    except Exception as e:
        return error_response(f"登录失败: {str(e)}", 500)

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    """获取当前用户信息"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return error_response("用户不存在", 404, 40401)

        # 统计用户数据
        posts_count = Post.query.filter_by(user_id=user_id, status='published').count()
        total_likes = db.session.query(db.func.sum(Post.likes_count)).filter_by(user_id=user_id).scalar() or 0

        user_data = user.to_dict()
        user_data['posts_count'] = posts_count
        user_data['total_likes'] = total_likes

        return success_response(user_data)

    except Exception as e:
        return error_response(f"获取用户信息失败: {str(e)}", 500)

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """退出登录（客户端删除token即可）"""
    return success_response(message="退出成功")

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """获取用户资料（公开信息）"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response("用户不存在", 404, 40401)

        posts_count = Post.query.filter_by(user_id=user_id, status='published').count()
        total_likes = db.session.query(db.func.sum(Post.likes_count)).filter_by(user_id=user_id).scalar() or 0

        return success_response({
            'id': user.id,
            'username': user.username,
            'avatar': user.avatar_url,
            'level': user.level,
            'points': user.points,
            'streak_days': user.streak_days,
            'posts_count': posts_count,
            'total_likes': total_likes,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })

    except Exception as e:
        return error_response(f"获取用户资料失败: {str(e)}", 500)

@app.route('/api/users/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """上传头像"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return error_response("用户不存在", 404, 40401)

        if 'avatar' not in request.files:
            return error_response("请选择图片", 400, 40001)

        f = request.files['avatar']
        if not f.filename:
            return error_response("请选择图片", 400, 40001)

        import uuid
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return error_response("仅支持 jpg/png/gif/webp 格式", 400, 40002)

        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        avatars_folder = os.path.join(upload_folder, 'avatars')
        os.makedirs(avatars_folder, exist_ok=True)

        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(avatars_folder, filename)
        f.save(filepath)

        avatar_url = f"/uploads/avatars/{filename}"
        user.avatar_url = avatar_url
        db.session.commit()

        return success_response({'avatar': avatar_url}, "头像上传成功")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(f"头像上传失败: {str(e)}", 500)

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    """获取当前登录用户资料"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return error_response("用户不存在", 404, 40401)

        return success_response({
            'id': user.id,
            'username': user.username,
            'phone': user.phone,
            'avatar': user.avatar_url,
            'level': user.level,
            'points': user.points,
            'streak_days': user.streak_days,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(f"获取用户资料失败: {str(e)}", 500)

# ==================== 词汇模块 ====================
@app.route('/api/words', methods=['GET'])
def get_words():
    """获取词汇列表（支持分页和筛选）"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)  # 最大100
        category = request.args.get('category')
        difficulty = request.args.get('difficulty', type=int)
        keyword = request.args.get('keyword')

        filters = {}
        if category: filters['category'] = category
        if difficulty: filters['difficulty'] = difficulty
        if keyword: filters['keyword'] = keyword

        result = WordService.get_words(page, page_size, **filters)
        
        # 添加 vocabulary_index 字段（与 corpus.txt 顺序一致，用于识别API的 target_index）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        corpus_file = os.path.join(project_root, 'dataset', 'corpus.txt')
        
        vocabulary_order = {}  # backend_id -> vocabulary_index
        if os.path.exists(corpus_file):
            with open(corpus_file, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            vocabulary_order[parts[0].strip()] = idx
        
        # 为返回的词汇添加 vocabulary_index
        for item in result.get('items', []):
            backend_id = item.get('backend_id', '')
            if backend_id in vocabulary_order:
                item['vocabulary_index'] = vocabulary_order[backend_id]
            else:
                item['vocabulary_index'] = None
        
        return success_response(result)

    except Exception as e:
        return error_response(f"获取词汇列表失败: {str(e)}", 500)

@app.route('/api/words/<int:word_id>', methods=['GET'])
def get_word(word_id):
    """获取词汇详情"""
    try:
        word = WordService.get_word(word_id)
        if not word:
            return error_response("词汇不存在", 404, 40401)

        return success_response(word)

    except Exception as e:
        return error_response(f"获取词汇详情失败: {str(e)}", 500)

@app.route('/api/words/<int:word_id>/dialects', methods=['GET'])
def get_word_dialects(word_id):
    """获取词汇方言列表"""
    try:
        dialects = DialectService.get_word_dialects(word_id)
        return success_response(dialects)

    except Exception as e:
        return error_response(f"获取方言列表失败: {str(e)}", 500)

# ==================== 学习记录模块 ====================
@app.route('/api/learning/records', methods=['POST'])
@jwt_required()
def create_record():
    """创建练习记录"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        word_id = data.get('word_id')
        is_correct = bool(data.get('is_correct', False))
        confidence = float(data.get('confidence', 0.0))

        if not word_id:
            return error_response("word_id不能为空", 400, 40001)

        # 验证词汇是否存在
        word = Word.query.get(word_id)
        if not word:
            return error_response("词汇不存在", 404, 40401)

        record = LearningService.create_record(user_id, word_id, is_correct, confidence)
        return success_response(record, "练习记录已保存", 201)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(f"创建练习记录失败: {str(e)}", 500)

@app.route('/api/learning/records', methods=['GET'])
@jwt_required()
def get_records():
    """获取学习记录列表"""
    try:
        user_id = int(get_jwt_identity())
        records = LearningService.get_records(user_id)
        return success_response(records)

    except Exception as e:
        return error_response(f"获取学习记录失败: {str(e)}", 500)

@app.route('/api/learning/records/<int:word_id>', methods=['GET'])
@jwt_required()
def get_record(word_id):
    """获取单个学习记录"""
    try:
        user_id = int(get_jwt_identity())
        record = LearningService.get_record(user_id, word_id)
        if not record:
            return error_response("学习记录不存在", 404, 40401)

        return success_response(record)

    except Exception as e:
        return error_response(f"获取学习记录失败: {str(e)}", 500)

@app.route('/api/learning/records/<int:word_id>', methods=['PUT'])
@jwt_required()
def update_record(word_id):
    """更新学习记录（收藏/标记学会）"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        record = LearningService.update_record(user_id, word_id, **data)
        return success_response(record, "更新成功")

    except Exception as e:
        return error_response(f"更新失败: {str(e)}", 500)

# ==================== 复习模块 ====================
@app.route('/api/review/today', methods=['GET'])
@jwt_required()
def get_today_reviews():
    """获取今日待复习词汇"""
    try:
        user_id = int(get_jwt_identity())
        reviews = ReviewService.get_today_reviews(user_id)
        return success_response({'total': len(reviews), 'words': reviews})

    except Exception as e:
        return error_response(f"获取复习列表失败: {str(e)}", 500)

@app.route('/api/review/complete/<int:word_id>', methods=['POST'])
@jwt_required()
def complete_review(word_id):
    """完成复习"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        is_correct = data.get('is_correct', False)

        result = ReviewService.complete_review(user_id, word_id, is_correct)
        return success_response(result, "复习完成")

    except Exception as e:
        return error_response(f"完成复习失败: {str(e)}", 500)

# ==================== 社区模块 ====================
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """获取社区动态列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 50)
        sort_by = request.args.get('sort', 'latest')

        # 检查是否请求"我的"帖子
        user_id = request.args.get('user_id', type=int)

        result = CommunityService.get_posts(page, page_size, sort_by, user_id)
        return success_response(result)

    except Exception as e:
        return error_response(f"获取动态列表失败: {str(e)}", 500)

@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    """发布动态（支持 multipart 文件上传）"""
    try:
        user_id = int(get_jwt_identity())

        # 优先从 multipart formdata 取，fallback 到 JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            content = _safe_trim(request.form.get('content', ''))
            word_tags_raw = request.form.get('word_tags', '')
            word_tags = json.loads(word_tags_raw) if word_tags_raw else None
        else:
            data = request.get_json(silent=True)
            if not data:
                return error_response("请求数据格式错误", 400, 40001)
            content = _safe_trim(data.get('content', ''))
            word_tags = data.get('word_tags')

        if not content:
            return error_response("动态内容不能为空", 400, 40001)

        post = CommunityService.create_post(
            user_id=user_id,
            content=content,
            images=None,
            video_url=None,
            word_tags=word_tags,
            request_obj=request
        )
        return success_response(post, "发布成功", 201)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(f"发布失败: {str(e)}", 500)

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """删除动态"""
    try:
        user_id = int(get_jwt_identity())
        success, msg = CommunityService.delete_post(user_id, post_id)
        if not success:
            return error_response(msg, 403, 40301)

        return success_response(message="删除成功")

    except Exception as e:
        return error_response(f"删除失败: {str(e)}", 500)

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    """点赞动态"""
    try:
        success, likes_count = CommunityService.like_post(post_id)
        if not success:
            return error_response(likes_count, 404, 40401)

        return success_response({'likes_count': likes_count})

    except Exception as e:
        return error_response(f"点赞失败: {str(e)}", 500)

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """获取评论列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 50)

        result = CommunityService.get_comments(post_id, page, page_size)
        return success_response(result)

    except Exception as e:
        return error_response(f"获取评论失败: {str(e)}", 500)

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """发表评论"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        if not data:
            return error_response("请求数据格式错误", 400, 40001)
        content = _safe_trim(data.get('content', ''))

        if not content:
            return error_response("评论内容不能为空", 400, 40001)

        comment = CommunityService.add_comment(post_id, user_id, content)
        return success_response(comment, "评论成功", 201)

    except Exception as e:
        return error_response(f"评论失败: {str(e)}", 500)

# ==================== 方言上传模块 ====================
@app.route('/api/dialects/upload', methods=['POST'])
@jwt_required()
def upload_dialect():
    """上传方言视频"""
    try:
        user_id = int(get_jwt_identity())
        word_id = request.form.get('word_id', type=int)
        region = _safe_trim(request.form.get('region', ''))
        description = _safe_trim(request.form.get('description', ''))

        if not word_id or not region:
            return error_response("word_id和region不能为空", 400, 40001)

        # 检查文件
        if 'video' not in request.files:
            return error_response("未上传视频文件", 400, 40002)

        video_file = request.files['video']
        if video_file.filename == '':
            return error_response("视频文件名为空", 400, 40003)

        if not DialectService.allowed_file(video_file.filename):
            return error_response("不支持的文件类型", 400, 40004)

        # 上传
        dialect, msg = DialectService.upload_dialect(
            user_id=user_id,
            word_id=word_id,
            region=region,
            video_file=video_file,
            description=description
        )

        if not dialect:
            return error_response(msg, 500)

        return success_response(dialect, "上传成功，等待审核", 201)

    except Exception as e:
        return error_response(f"上传失败: {str(e)}", 500)

@app.route('/api/dialects/my', methods=['GET'])
@jwt_required()
def get_my_dialects():
    """获取我的上传记录"""
    try:
        user_id = int(get_jwt_identity())
        dialects = DialectService.get_my_uploads(user_id)
        return success_response(dialects)

    except Exception as e:
        return error_response(f"获取上传记录失败: {str(e)}", 500)

# ==================== 统计模块 ====================
@app.route('/api/stats/overview', methods=['GET'])
@jwt_required()
def get_stats_overview():
    """学习概览"""
    try:
        user_id = int(get_jwt_identity())
        stats = StatsService.get_overview(user_id)
        return success_response(stats)

    except Exception as e:
        return error_response(f"获取统计失败: {str(e)}", 500)

@app.route('/api/stats/chart', methods=['GET'])
@jwt_required()
def get_stats_chart():
    """图表数据"""
    try:
        user_id = int(get_jwt_identity())
        period = request.args.get('period', 'week')
        chart_data = StatsService.get_chart_data(user_id, period)
        return success_response(chart_data)

    except Exception as e:
        return error_response(f"获取图表数据失败: {str(e)}", 500)

@app.route('/api/stats/radar', methods=['GET'])
@jwt_required()
def get_stats_radar():
    """雷达图数据"""
    try:
        user_id = int(get_jwt_identity())
        data = StatsService.get_radar_data(user_id)
        return success_response(data)
    except Exception as e:
        return error_response(f"获取雷达图数据失败: {str(e)}", 500)

@app.route('/api/stats/ranking', methods=['GET'])
@jwt_required()
def get_stats_ranking():
    """排行榜"""
    try:
        user_id = int(get_jwt_identity())
        limit = int(request.args.get('limit', 10))
        data = StatsService.get_ranking(limit, user_id)
        return success_response(data)
    except Exception as e:
        return error_response(f"获取排行榜失败: {str(e)}", 500)

@app.route('/api/stats/calendar', methods=['GET'])
@jwt_required()
def get_stats_calendar():
    """学习日历数据：返回指定月份的每日学习状态"""
    try:
        user_id = int(get_jwt_identity())
        year = int(request.args.get('year', date.today().year))
        month = int(request.args.get('month', date.today().month))

        from calendar import monthrange
        _, last_day = monthrange(year, month)

        result = {}
        for day in range(1, last_day + 1):
            d = date(year, month, day)
            stat = StudyStat.query.filter_by(user_id=user_id, date=d).first()
            has_learning = stat is not None and (stat.words_count > 0 or stat.practice_count > 0)
            result[str(day)] = {
                'has_learning': has_learning,
                'words_count': stat.words_count if stat else 0,
                'minutes': (stat.practice_count if stat else 0) * 3
            }

        return success_response({
            'year': year,
            'month': month,
            'days': result
        })
    except Exception as e:
        return error_response(f"获取日历数据失败: {str(e)}", 500)

# ==================== 手语识别模块 ====================
# 懒加载识别器，避免启动时加载模型
_predictor = None
_backend_id_to_idx = {}

def get_predictor():
    """获取或初始化识别器（懒加载）"""
    global _predictor, _backend_id_to_idx
    if _predictor is None:
        try:
            # 导入识别器
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from inference.predictor import IsolatedWordPredictor

            print("正在初始化手语识别模型...")
            project_root = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(project_root, '..', 'models', 'best_isolated_model.pth')
            corpus_path = os.path.join(project_root, '..', 'dataset', 'corpus.txt')

            _predictor = IsolatedWordPredictor(
                model_type='cnn_lstm',
                model_path=model_path,
                corpus_file=corpus_path
            )

            # 构建 backend_id 到训练索引的映射（与 ui_plus.py 一致：使用 pandas + corpus.txt）
            _backend_id_to_idx = {}
            if hasattr(_predictor, 'corpus_by_idx'):
                if os.path.exists(corpus_path):
                    try:
                        import pandas as pd
                        df = pd.read_csv(corpus_path, sep='\t', header=None, names=['backend_id', 'text'], encoding='utf-8')
                        for _, row in df.iterrows():
                            backend_id = str(row['backend_id']).strip()
                            word_text = str(row['text']).strip()
                            for train_idx, text in _predictor.corpus_by_idx.items():
                                if text == word_text:
                                    _backend_id_to_idx[backend_id] = train_idx
                                    break
                        print(f"词汇映射构建完成: {len(_backend_id_to_idx)} 个词汇")
                    except Exception as e:
                        print(f"构建词汇映射失败: {e}")

            print(f"手语识别模型初始化完成，词汇映射: {len(_backend_id_to_idx)} 个")
        except Exception as e:
            print(f"识别器初始化失败: {e}")
            import traceback
            traceback.print_exc()
            _predictor = None
            _backend_id_to_idx = {}
    return _predictor, _backend_id_to_idx

@app.route('/api/init-isolated', methods=['POST'])
def init_isolated():
    """初始化孤立词识别模型 - 与 ui_plus.py 格式一致"""
    try:
        predictor, backend_id_to_idx = get_predictor()
        if predictor is None:
            return jsonify({
                'success': False,
                'message': '模型初始化失败，请检查模型文件是否存在'
            }), 500

        return jsonify({
            'success': True,
            'message': '模型初始化成功',
            'model_type': 'cnn_lstm',
            'vocab_size': len(backend_id_to_idx),
            'num_classes': predictor.config.num_classes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'初始化失败: {str(e)}'
        }), 500

@app.route('/api/predict-isolated', methods=['POST'])
def predict_isolated():
    """孤立词手语识别接口"""
    try:
        # 检查是否有视频文件
        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'message': '请上传视频文件'
            })

        video_file = request.files['video']
        word_id = request.form.get('target_index') or request.form.get('word_id')
        print(f"[predict] word_id received: {repr(word_id)}, type: {type(word_id)}")

        # 将前端传来的ID转换为模型训练索引
        target_idx = None
        if word_id:
            try:
                # 获取识别器和映射
                predictor, backend_map = get_predictor()
                if predictor is None:
                    return jsonify({
                        'success': False,
                        'message': '识别器未初始化'
                    })

                # 尝试多种方式解析 word_id
                word_id_str = str(word_id).strip()
                print(f"[predict] word_id_str: {repr(word_id_str)}, isdigit: {word_id_str.isdigit()}")

                # 方式1: 如果 word_id 是数字格式
                if word_id_str.isdigit():
                    potential_idx = int(word_id_str)  # 前端已转换为 0-based
                    print(f"[predict] potential_idx: {potential_idx}, corpus_by_idx keys: {list(predictor.corpus_by_idx.keys())[:5]}...")
                    # 检查这个索引是否在词汇表范围内
                    if predictor.corpus_by_idx and potential_idx in predictor.corpus_by_idx:
                        target_idx = potential_idx
                        print(f"[predict] using direct index: {target_idx}, word: {predictor.corpus_by_idx.get(target_idx)}")
                    else:
                        print(f"[predict] index {potential_idx} not in corpus, trying database lookup")
                        # 方式2: 尝试作为数据库ID查找
                        try:
                            word_id_int = int(word_id_str)
                            word = Word.query.get(word_id_int)
                            if word:
                                print(f"[predict] found word in DB: id={word.id}, text={word.text}, backend_id={word.backend_id}")
                                # 使用 backend_id 查找训练索引
                                target_idx = backend_map.get(word.backend_id)
                                print(f"[predict] backend_map lookup: backend_id={word.backend_id} -> {target_idx}")
                                if target_idx is None:
                                    # 方式3: 直接使用 word_id - 1 作为训练索引（兼容旧格式）
                                    target_idx = potential_idx
                                    print(f"[predict] falling back to direct index: {target_idx}")
                        except Exception as ex:
                            print(f"[predict] DB lookup error: {ex}")
                            # 方式3: 直接使用 word_id - 1 作为训练索引
                            target_idx = potential_idx

                if target_idx is None:
                    print(f"[predict] WARNING: cannot resolve word_id={repr(word_id)}")
                    # 最后尝试：直接使用 word_id - 1
                    if word_id_str.isdigit():
                        target_idx = int(word_id_str)

            except (ValueError, TypeError) as e:
                print(f"[predict] word_id conversion error: {e}")
                target_idx = None

        print(f"[predict] final target_idx: {target_idx}")

        # 获取识别器
        predictor, _ = get_predictor()
        if predictor is None:
            return jsonify({
                'success': False,
                'message': '识别器未初始化，请先调用 /api/init-isolated'
            })

        # 保存视频到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            video_file.save(tmp.name)
            tmp_path = tmp.name

        try:
            # 提取视频特征
            features = predictor.feature_extractor.extract_from_video(tmp_path)

            # 检查特征是否为全零（表示未检测到手部）
            if features is None or len(features) == 0:
                return jsonify({
                    'success': False,
                    'message': '视频中未检测到手部关键点，请确保手部可见'
                })

            # 检查特征是否为全零（可能是无效输入）
            if np.all(features == 0):
                return jsonify({
                    'success': False,
                    'message': '视频中未检测到手部关键点，请确保手部可见'
                })

            # 检查特征维度
            if features.shape[1] != 84:
                return jsonify({
                    'success': False,
                    'message': f'特征维度错误: {features.shape[1]}，期望 84'
                })

            # 执行预测
            result = predictor._predict(
                features,
                return_prob=True,
                top_k=1,
                target_index=target_idx
            )

            # 处理不同的返回格式
            if isinstance(result, tuple):
                # 当 target_index 为 None 时，返回 (predicted_text, confidence)
                predicted_text, confidence = result
                target_text = ''
                target_confidence = 0.0
                predicted_idx = -1
            else:
                # 当 target_index 不为 None 时，返回字典
                predicted_text = result.get('predicted', '未知')
                confidence = result.get('confidence', 0.0)
                target_text = result.get('target', '')
                target_confidence = result.get('target_confidence', 0.0)
                predicted_idx = result.get('predicted_idx', -1)

            # 构建响应数据
            response_data = {
                'success': True,
                'predicted': predicted_text,
                'confidence': confidence,
                'target': target_text,
                'target_confidence': target_confidence,
                'predicted_idx': predicted_idx,
                'message': '识别成功'
            }
            print(f"[predict] response: {response_data}")
            return jsonify(response_data)

        finally:
            # 删除临时文件
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'识别失败: {str(e)}'
        })

@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    """获取词汇表（用于识别）

    返回格式：
    - id: 0-based 索引，与 corpus.txt 顺序一致，用于 predict-isolated 接口
    - text: 词汇文本
    """
    try:
        predictor, _ = get_predictor()
        if predictor is None or not hasattr(predictor, 'corpus_by_idx'):
            return jsonify({
                'success': True,
                'vocabulary': [
                    {'id': 0, 'text': '你好'},
                    {'id': 1, 'text': '谢谢'},
                    {'id': 2, 'text': '再见'},
                    {'id': 3, 'text': '对不起'},
                    {'id': 4, 'text': '请'},
                ]
            })

        vocabulary = []
        for idx, text in predictor.corpus_by_idx.items():
            vocabulary.append({
                'id': idx,  # 0-based 索引，与 corpus.txt 顺序一致
                'text': text
            })

        return jsonify({
            'success': True,
            'vocabulary': vocabulary
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取词汇表失败: {str(e)}'
        })

# ==================== 管理员模块 ====================
@app.route('/api/admin/dialects', methods=['GET'])
@jwt_required()
def admin_get_dialects():
    """管理员：获取所有待审核方言上传"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return error_response('无权限访问', 403)

        status = request.args.get('status', 'pending')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        query = DialectUpload.query.order_by(DialectUpload.created_at.desc())
        if status != 'all':
            query = query.filter_by(status=status)

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        items = []
        for d in pagination.items:
            items.append({
                'id': d.id,
                'word': d.word.word if d.word else None,
                'word_id': d.word_id,
                'user': d.user.username if d.user else '未知',
                'user_id': d.user_id,
                'region': d.region,
                'video_url': d.video_url,
                'description': d.description,
                'status': d.status,
                'rejection_reason': d.rejection_reason,
                'created_at': d.created_at.isoformat() if d.created_at else None,
                'reviewed_at': d.reviewed_at.isoformat() if d.reviewed_at else None,
            })

        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages
        })
    except Exception as e:
        return error_response(f'获取列表失败: {str(e)}', 500)

@app.route('/api/admin/dialects/<int:dialect_id>/review', methods=['POST'])
@jwt_required()
def admin_review_dialect(dialect_id):
    """管理员：审核方言上传（批准/驳回）"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return error_response('无权限访问', 403)

        data = request.get_json()
        action = data.get('action')  # 'approve' | 'reject'
        reason = data.get('reason', '')

        dialect = DialectUpload.query.get(dialect_id)
        if not dialect:
            return error_response('记录不存在', 404)

        if action == 'approve':
            dialect.status = 'approved'
            dialect.rejection_reason = None
            # 方言审核通过，奖励上传者10积分
            try:
                PointsService.add_points(dialect.user_id, 10, 'dialect')
            except Exception:
                pass
        elif action == 'reject':
            dialect.status = 'rejected'
            dialect.rejection_reason = reason
        else:
            return error_response('无效的操作', 400)

        dialect.reviewer_id = user_id
        dialect.reviewed_at = datetime.now()
        db.session.commit()

        return success_response({'status': dialect.status}, '审核完成')
    except Exception as e:
        return error_response(f'审核失败: {str(e)}', 500)

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def admin_get_stats():
    """管理员：获取平台统计"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return error_response('无权限访问', 403)

        total_users = User.query.count()
        total_words = Word.query.count()
        pending_dialects = DialectUpload.query.filter_by(status='pending').count()
        approved_dialects = DialectUpload.query.filter_by(status='approved').count()
        rejected_dialects = DialectUpload.query.filter_by(status='rejected').count()
        learned_count = LearningRecord.query.filter_by(is_learned=True).count()
        total_reviews = ReviewSchedule.query.count()

        return success_response({
            'total_users': total_users,
            'total_words': total_words,
            'pending_dialects': pending_dialects,
            'approved_dialects': approved_dialects,
            'rejected_dialects': rejected_dialects,
            'learned_count': learned_count,
            'total_reviews': total_reviews,
        })
    except Exception as e:
        return error_response(f'获取统计失败: {str(e)}', 500)

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def admin_get_users():
    """管理员：获取用户列表"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return error_response('无权限访问', 403)

        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        pagination = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=page_size, error_out=False
        )
        items = [{
            'id': u.id,
            'username': u.username,
            'phone': u.phone,
            'role': u.role or 'user',
            'level': u.level,
            'points': u.points,
            'streak_days': u.streak_days,
            'learned_words': LearningRecord.query.filter_by(user_id=u.id, is_learned=True).count(),
            'created_at': u.created_at.isoformat() if u.created_at else None,
        } for u in pagination.items]

        return success_response({
            'items': items,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
        })
    except Exception as e:
        return error_response(f'获取用户列表失败: {str(e)}', 500)

@app.route('/api/admin/users/<int:target_user_id>/role', methods=['PUT'])
@jwt_required()
def admin_update_user_role(target_user_id):
    """管理员：修改用户角色"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return error_response('无权限访问', 403)

        data = request.get_json()
        new_role = data.get('role')
        if new_role not in ('user', 'admin'):
            return error_response('无效的角色', 400)

        target = User.query.get(target_user_id)
        if not target:
            return error_response('用户不存在', 404)
        if target.id == user_id:
            return error_response('不能修改自己的角色', 400)

        target.role = new_role
        db.session.commit()
        return success_response({'role': new_role}, '角色已更新')
    except Exception as e:
        return error_response(f'更新失败: {str(e)}', 500)

# ==================== 竞技场模块 ====================
@app.route('/api/arena/start', methods=['POST'])
@jwt_required()
def arena_start():
    """开始竞技场挑战"""
    try:
        user_id = int(get_jwt_identity())

        result, error = ArenaService.generate_arena_questions(user_id)
        if error:
            return error_response(error, 400)

        return success_response(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(f"竞技场启动失败: {str(e)}", 500)

@app.route('/api/arena/verify', methods=['POST'])
@jwt_required()
def arena_verify():
    """验证竞技场答案"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        word_id = data.get('word_id')
        stage = data.get('stage')
        answer = data.get('answer')  # 选择题为索引，输入题为字符串

        if not word_id or not stage:
            return error_response("参数不完整", 400)

        word = Word.query.get(word_id)
        if not word:
            return error_response("词汇不存在", 404)

        is_correct = False
        correct_answer = None

        if stage == 2:
            # 选择题验证
            selected_index = answer if isinstance(answer, int) else -1
            cached = LearningChoiceOptions.query.filter_by(
                user_id=user_id,
                word_id=word_id,
                session_type='learn'
            ).first()
            if cached:
                correct_index = cached.correct_index
                correct_answer = json.loads(cached.options)[correct_index]['word'] if cached.options else None
                is_correct = (selected_index == correct_index)

        elif stage == 3:
            # 输入题验证
            user_input = answer.strip() if isinstance(answer, str) else ''
            correct_answer = word.word
            is_correct = (user_input == word.word)

        return success_response({
            'is_correct': is_correct,
            'correct_answer': correct_answer
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(f"答案验证失败: {str(e)}", 500)

@app.route('/api/arena/finish', methods=['POST'])
@jwt_required()
def arena_finish():
    """完成竞技场挑战"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        answers = data.get('answers', [])  # [{word_id, stage, is_correct}]

        result = ArenaService.finish_arena(user_id, answers)
        return success_response(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(f"竞技场完成失败: {str(e)}", 500)

# ==================== 积分与等级模块 ====================
@app.route('/api/points/level', methods=['GET'])
@jwt_required()
def get_level_info():
    """获取用户等级信息"""
    try:
        user_id = int(get_jwt_identity())
        info = PointsService.get_level_info(user_id)
        if not info:
            return error_response("用户不存在", 404)
        return success_response(info)

    except Exception as e:
        return error_response(f"获取等级信息失败: {str(e)}", 500)

@app.route('/api/points/add', methods=['POST'])
@jwt_required()
def add_points():
    """增加用户积分（用于各种积分奖励场景）"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        points = data.get('points', 0)
        source = data.get('source', '')  # learning, review, community, dialect

        if points <= 0:
            return error_response("积分必须大于0", 400)

        new_points, level_up, new_level = PointsService.add_points(user_id, points, source)

        return success_response({
            'new_points': new_points,
            'level_up': level_up,
            'new_level': new_level
        })

    except Exception as e:
        return error_response(f"增加积分失败: {str(e)}", 500)

# ==================== 初始化数据库命令 ====================
@app.cli.command('init-db')
def init_db_command():
    """Flask命令：初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建完成")

        # 导入词汇（传入视频目录路径）
        corpus_path = os.path.join(app.root_path, '..', '..', 'dataset', 'corpus.txt')
        video_path = os.path.join(app.root_path, '..', 'video')
        count = WordService.import_from_corpus(corpus_path, video_path)
        print(f"✅ 导入词汇: {count}个")

        # 更新现有词汇的视频路径（确保已存在的词汇也能关联视频）
        update_count = WordService.update_video_urls(video_path)
        print(f"✅ 更新视频路径: {update_count}个")

        # 创建默认管理员
        admin = User(
            username='admin',
            phone='13800000000',
            password_hash=hash_password('admin123'),
            level=10,
            points=9999,
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ 默认管理员: admin / admin123 (角色: admin)")

        print("\n🎉 初始化完成!")
        print("   启动命令: python app.py")

@app.cli.command('update-videos')
def update_videos_command():
    """Flask命令：更新所有词汇的视频路径"""
    with app.app_context():
        video_path = os.path.join(app.root_path, '..', 'video')
        count = WordService.update_video_urls(video_path)
        print(f"[OK] Updated {count} word video paths")

# ==================== 主程序入口 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("  CSL手语识别系统 - 后端服务")
    print("=" * 60)
    print(f"  环境: 开发模式")
    print(f"  地址: http://localhost:5001")
    print(f"  数据库: SQLite")
    print(f"  初始化: flask init-db")
    print("=" * 60)

    # 首次运行自动初始化
    with app.app_context():
        db.create_all()
        print("[OK] 数据库表已就绪")

    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True, use_reloader=False)
