"""
业务逻辑服务层 - 精简版
包含所有核心业务逻辑：认证、词汇、学习、复习等
"""
import os
import bcrypt
import json
from datetime import datetime, timedelta
from flask import current_app, request
from backend.models import db, User, Word, LearningRecord, ReviewSchedule, Post, Comment, DialectUpload, StudyStat, LearningProgress, UserLearningSettings, DailyPlan, LearningChoiceOptions
from backend.learning_service import LearningCenterService

# ==================== 工具函数 ====================
def hash_password(password: str) -> str:
    """密码加密"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

# ==================== 用户认证服务 ====================
class AuthService:
    """用户认证服务"""
    
    @staticmethod
    def register(username: str, phone: str, password: str):
        """
        用户注册
        Returns: (User, error_message)
        """
        # 参数验证
        if not username or len(username) < 2:
            return None, "用户名至少2个字符"
        if not phone or not phone.isdigit() or len(phone) != 11:
            return None, "手机号格式错误（11位数字）"
        if not password or len(password) < 6:
            return None, "密码至少6位"

        # 检查是否已存在
        if User.query.filter_by(phone=phone).first():
            return None, "手机号已注册"
        if User.query.filter_by(username=username).first():
            return None, "用户名已存在"

        # 创建用户
        user = User(
            username=username,
            phone=phone,
            password_hash=hash_password(password)
        )
        db.session.add(user)
        db.session.commit()

        return user, "注册成功"

    @staticmethod
    def login(phone: str, password: str):
        """
        用户登录
        Returns: (User, error_message)
        """
        if not phone or not password:
            return None, "参数不完整"

        user = User.query.filter_by(phone=phone).first()
        if not user:
            return None, "用户不存在"
        if not verify_password(password, user.password_hash):
            return None, "密码错误"

        # 更新最后活跃日期
        user.last_active_date = datetime.now().date()
        db.session.commit()

        return user, "登录成功"

# ==================== 词汇服务 ====================
class WordService:
    """词汇管理服务"""
    
    @staticmethod
    def get_words(page=1, page_size=20, category=None, difficulty=None, keyword=None):
        """
        获取词汇列表（支持分页和筛选）
        """
        query = Word.query

        if category:
            query = query.filter_by(category=category)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        if keyword:
            query = query.filter(Word.word.like(f"%{keyword}%"))

        # 分页
        total = query.count()
        items = query.order_by(Word.id.asc()) \
                    .offset((page - 1) * page_size) \
                    .limit(page_size) \
                    .all()

        return {
            'items': [w.to_dict() for w in items],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    @staticmethod
    def get_word(word_id):
        """获取词汇详情"""
        word = Word.query.get(word_id)
        return word.to_dict() if word else None

    @staticmethod
    def get_word_by_backend_id(backend_id):
        """根据backend_id获取词汇"""
        word = Word.query.filter_by(backend_id=backend_id).first()
        return word.to_dict() if word else None

    @staticmethod
    def import_from_corpus(corpus_path, video_base_path=None):
        """
        从corpus.txt导入词汇（仅用于初始化）
        video_base_path: 视频文件基础路径，如 'front/public/videos'
        """
        if not os.path.exists(corpus_path):
            print(f"⚠️  corpus.txt 不存在: {corpus_path}")
            return 0

        # 获取可用的视频文件列表
        available_videos = set()
        if video_base_path and os.path.isdir(video_base_path):
            for f in os.listdir(video_base_path):
                if f.endswith('.mp4'):
                    # 提取词汇名（去掉.mp4扩展名）
                    word_name = f[:-4]
                    available_videos.add(word_name)
            print(f"📹 找到 {len(available_videos)} 个视频文件: {sorted(available_videos)}")

        count = 0
        with open(corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    backend_id = parts[0].strip()
                    word_text = parts[1].strip()
                    # 处理括号中的备选词，如 "去（出）" -> "去"
                    if '（' in word_text:
                        word_text = word_text.split('（')[0]

                    # 检查是否已存在
                    existing = Word.query.filter_by(backend_id=backend_id).first()
                    if existing:
                        continue

                    # 自动设置视频路径
                    demo_video_url = None
                    # 1. 精确匹配
                    if word_text in available_videos:
                        demo_video_url = f'/videos/{word_text}.mp4'
                    # 2. 备选词匹配：从backend_id提取主词
                    elif '（' in backend_id:
                        # backend_id格式如 000101去（出）
                        import re
                        match = re.match(r'\d+(.*?)（', backend_id)
                        if match:
                            main_word = match.group(1)
                            if main_word in available_videos:
                                demo_video_url = f'/videos/{main_word}.mp4'

                    word = Word(
                        backend_id=backend_id,
                        word=word_text,
                        category='基础',
                        difficulty=1,
                        demo_video_url=demo_video_url
                    )
                    db.session.add(word)
                    count += 1

        db.session.commit()
        return count

    @staticmethod
    def update_video_urls(video_base_path):
        """
        批量更新现有词汇的视频路径
        遍历所有词汇，自动匹配视频文件
        """
        if not os.path.isdir(video_base_path):
            print(f"[WARN] Video directory does not exist: {video_base_path}")
            return 0

        # 获取可用的视频文件列表
        available_videos = {}
        for f in os.listdir(video_base_path):
            if f.endswith('.mp4'):
                word_name = f[:-4]  # 去掉.mp4扩展名
                available_videos[word_name] = f'/videos/{f}'

        print(f"[VIDEO] Found {len(available_videos)} video files")

        # 更新所有词汇的视频路径
        all_words = Word.query.all()
        updated_count = 0
        matched_words = []

        for word in all_words:
            video_url = None

            # 1. 精确匹配词汇名
            if word.word in available_videos:
                video_url = available_videos[word.word]
            else:
                # 2. 从 word 字段提取主词（去掉括号内容，如"矮（低）" -> "矮"）
                main_word = word.word
                for sep in ['（', '(', '（', '(']:
                    if sep in main_word:
                        main_word = main_word.split(sep)[0]
                        break
                if main_word in available_videos:
                    video_url = available_videos[main_word]

            # 如果找到视频且与现有值不同，则更新
            if video_url and word.demo_video_url != video_url:
                word.demo_video_url = video_url
                db.session.add(word)
                updated_count += 1
                matched_words.append(f"{word.word} -> {video_url}")

        db.session.commit()
        print(f"[OK] Updated {updated_count} word video paths")
        for match in matched_words:
            print(f"   {match}")
        return updated_count

# ==================== 学习记录服务 ====================
class LearningService:
    """学习记录服务"""
    
    @staticmethod
    def _update_study_stat(user_id, word_id=None):
        """更新每日学习统计"""
        from datetime import date
        today = date.today()
        stat = StudyStat.query.filter_by(user_id=user_id, date=today).first()
        if not stat:
            stat = StudyStat(user_id=user_id, date=today)
            db.session.add(stat)

        # 确保字段有默认值（修复NoneType错误）
        if stat.practice_count is None:
            stat.practice_count = 0
        if stat.minutes is None:
            stat.minutes = 0
        if stat.words_count is None:
            stat.words_count = 0

        stat.practice_count += 1
        # 每次练习约3分钟
        stat.minutes += 3

        # 如果是新学习的词汇，增加词汇计数
        if word_id:
            existing_record = LearningRecord.query.filter_by(user_id=user_id, word_id=word_id).first()
            # 只有当这是第一次练习时才增加词汇计数
            if not existing_record or existing_record.practice_count == 1:
                stat.words_count += 1

        db.session.add(stat)
    
    @staticmethod
    def create_record(user_id, word_id, is_correct=False, confidence=0.0):
        """
        创建练习记录
        学词标准：3次练习中至少2次成功，或连续2次成功 → 标记为已学会并创建复习计划
        Returns: dict (record)
        """
        record = LearningRecord.query.filter_by(user_id=user_id, word_id=word_id).first()
        is_new_record = False
        if not record:
            record = LearningRecord(user_id=user_id, word_id=word_id)
            is_new_record = True

        # 确保数值字段有默认值（修复NoneType错误）
        if record.practice_count is None:
            record.practice_count = 0
        if record.correct_count is None:
            record.correct_count = 0
        if record.avg_accuracy is None:
            record.avg_accuracy = 0.0

        # 记录上一轮正确状态（用于判断连续正确）
        prev_correct = record.correct_count > 0 and record.avg_accuracy == 1.0

        record.practice_count += 1
        if is_correct:
            record.correct_count += 1
        record.avg_accuracy = record.correct_count / record.practice_count
        record.last_practice_at = datetime.now()

        # 判断是否满足"已学会"条件（且之前未标记为已学会）
        if not record.is_learned:
            total = record.practice_count
            correct = record.correct_count
            consecutive_ok = (prev_correct and is_correct)
            majority_ok = (total >= 3 and correct >= 2)
            # 满足任一条件：标记为已学会 + 创建复习计划
            if consecutive_ok or majority_ok:
                record.is_learned = True
                try:
                    ReviewService._create_schedule(user_id, word_id)
                except Exception as e:
                    print(f"创建复习计划失败（不影响记录保存）: {e}")

        db.session.add(record)
        
        # 更新每日学习统计
        LearningService._update_study_stat(user_id, word_id if is_new_record else None)
        
        db.session.commit()

        return record.to_dict()

    @staticmethod
    def get_records(user_id):
        """获取用户所有学习记录"""
        records = LearningRecord.query.filter_by(user_id=user_id).all()
        return [r.to_dict() for r in records]

    @staticmethod
    def get_record(user_id, word_id):
        """获取单个学习记录"""
        record = LearningRecord.query.filter_by(user_id=user_id, word_id=word_id).first()
        return record.to_dict() if record else None

    @staticmethod
    def update_record(user_id, word_id, **kwargs):
        """更新学习记录（收藏、标记学会等）"""
        record = LearningRecord.query.filter_by(user_id=user_id, word_id=word_id).first()
        if not record:
            record = LearningRecord(user_id=user_id, word_id=word_id)
            # 确保字段有默认值
            if record.practice_count is None:
                record.practice_count = 0
            if record.correct_count is None:
                record.correct_count = 0

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)

        db.session.add(record)
        db.session.commit()

        return record.to_dict()

    @staticmethod
    def get_learned_words(user_id):
        """获取已学会的词汇列表"""
        records = LearningRecord.query.filter_by(user_id=user_id, is_learned=True).all()
        return [r.word_id for r in records]

    @staticmethod
    def get_favorites(user_id):
        """获取收藏的词汇列表"""
        records = LearningRecord.query.filter_by(user_id=user_id, is_favorite=True).all()
        return [r.word_id for r in records]

# ==================== 复习服务（艾宾浩斯） ====================
class ReviewService:
    """复习计划服务 - 基于艾宾浩斯遗忘曲线"""
    
    # 复习间隔（天）
    REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]

    @staticmethod
    def get_today_reviews(user_id):
        """
        获取今日待复习词汇
        Returns: list of ReviewSchedule
        """
        today = datetime.now()
        schedules = ReviewSchedule.query.filter(
            ReviewSchedule.user_id == user_id,
            ReviewSchedule.next_review_at <= today
        ).all()

        return [s.to_dict() for s in schedules]

    @staticmethod
    def complete_review(user_id, word_id, is_correct=False):
        """
        完成一次复习（艾宾浩斯）
        复习成功 → 进入下一轮间隔；复习失败 → 间隔重置为1天
        同时同步更新 LearningRecord 的统计数据
        Returns: dict (schedule)
        """
        schedule = ReviewSchedule.query.filter_by(user_id=user_id, word_id=word_id).first()

        if not schedule:
            # 创建新的复习计划
            schedule = ReviewService._create_schedule(user_id, word_id)

        # 更新连续正确次数
        if is_correct:
            schedule.correct_count += 1
        else:
            schedule.correct_count = 0

        # 计算下次复习间隔
        idx = min(schedule.correct_count, len(ReviewService.REVIEW_INTERVALS) - 1)
        interval = ReviewService.REVIEW_INTERVALS[idx]
        schedule.interval = interval
        schedule.last_review_at = datetime.now()
        schedule.next_review_at = datetime.now() + timedelta(days=interval)

        db.session.add(schedule)

        # 同步更新 LearningRecord 的统计数据
        record = LearningRecord.query.filter_by(user_id=user_id, word_id=word_id).first()
        if record:
            record.practice_count += 1
            if is_correct:
                record.correct_count += 1
            record.avg_accuracy = record.correct_count / record.practice_count
            record.last_practice_at = datetime.now()
            db.session.add(record)
        
        # 更新每日学习统计
        LearningService._update_study_stat(user_id, word_id)

        db.session.commit()

        return schedule.to_dict()

    @staticmethod
    def _create_schedule(user_id, word_id):
        """创建初始复习计划"""
        schedule = ReviewSchedule(
            user_id=user_id,
            word_id=word_id,
            interval=1,
            next_review_at=datetime.now() + timedelta(days=1)
        )
        db.session.add(schedule)
        db.session.commit()
        return schedule

    @staticmethod
    def get_schedule(user_id, word_id):
        """获取单个复习计划"""
        schedule = ReviewSchedule.query.filter_by(user_id=user_id, word_id=word_id).first()
        return schedule.to_dict() if schedule else None

# ==================== 社区服务 ====================
class CommunityService:
    """社区动态服务"""
    
    @staticmethod
    def get_posts(page=1, page_size=20, sort_by='latest', user_id=None):
        """获取动态列表（分页）"""
        query = Post.query.filter_by(status='published')

        # 按用户筛选
        if user_id:
            query = query.filter_by(user_id=user_id)

        if sort_by == 'hot':
            query = query.order_by(Post.likes_count.desc(), Post.created_at.desc())
        else:  # latest
            query = query.order_by(Post.created_at.desc())

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            'items': [p.to_dict() for p in items],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    @staticmethod
    def create_post(user_id, content, images=None, video_url=None, word_tags=None, request_obj=None):
        """发布动态（支持文件上传）"""
        import uuid

        uploaded_images = []
        uploaded_video_url = None

        if request_obj and request_obj.content_type and 'multipart/form-data' in request_obj.content_type:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            posts_folder = os.path.join(upload_folder, 'posts')
            os.makedirs(posts_folder, exist_ok=True)

            # 处理图片
            files = request_obj.files.getlist('images')
            for f in files:
                if f and f.filename:
                    ext = os.path.splitext(f.filename)[1].lower()
                    filename = f"{uuid.uuid4().hex}{ext}"
                    filepath = os.path.join(posts_folder, filename)
                    f.save(filepath)
                    uploaded_images.append(f"/uploads/posts/{filename}")

            # 处理视频
            video_file = request_obj.files.get('video')
            if video_file and video_file.filename:
                ext = os.path.splitext(video_file.filename)[1].lower()
                filename = f"{uuid.uuid4().hex}{ext}"
                filepath = os.path.join(posts_folder, filename)
                video_file.save(filepath)
                uploaded_video_url = f"/uploads/posts/{filename}"

        post = Post(
            user_id=user_id,
            content=content,
            images=json.dumps(uploaded_images) if uploaded_images else None,
            video_url=uploaded_video_url,
            word_tags=json.dumps(word_tags) if word_tags else None
        )
        db.session.add(post)
        db.session.commit()

        # 发布动态奖励3积分
        try:
            PointsService.add_points(user_id, 3, 'community')
        except Exception:
            pass

        return post.to_dict()

    @staticmethod
    def delete_post(user_id, post_id):
        """删除动态（软删除）"""
        post = Post.query.get(post_id)
        if not post:
            return False, "动态不存在"
        if post.user_id != user_id:
            return False, "无权删除"

        post.status = 'deleted'
        db.session.commit()

        return True, "删除成功"

    @staticmethod
    def like_post(post_id):
        """点赞动态"""
        post = Post.query.get(post_id)
        if not post:
            return False, "动态不存在"

        post.likes_count += 1
        db.session.commit()

        # 帖子被点赞，发布者获得1积分
        try:
            PointsService.add_points(post.user_id, 1, 'community')
        except Exception:
            pass

        return True, post.likes_count

    @staticmethod
    def unlike_post(post_id):
        """取消点赞"""
        post = Post.query.get(post_id)
        if not post:
            return False, "动态不存在"

        if post.likes_count > 0:
            post.likes_count -= 1
        db.session.commit()

        return True, post.likes_count

    @staticmethod
    def get_comments(post_id, page=1, page_size=20):
        """获取评论列表"""
        query = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            'items': [c.to_dict() for c in items],
            'total': total
        }

    @staticmethod
    def add_comment(post_id, user_id, content):
        """发表评论"""
        comment = Comment(post_id=post_id, user_id=user_id, content=content)
        db.session.add(comment)

        # 更新动态的评论数
        post = Post.query.get(post_id)
        if post:
            post.comments_count += 1

        db.session.commit()

        return comment.to_dict()

# ==================== 方言上传服务 ====================
class DialectService:
    """方言上传服务"""
    
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}

    @staticmethod
    def allowed_file(filename):
        """检查文件类型"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in DialectService.ALLOWED_EXTENSIONS

    @staticmethod
    def upload_dialect(user_id, word_id, region, video_file, description=None):
        """
        上传方言视频
        Returns: (DialectUpload, error_message)
        """
        # 验证词汇是否存在
        word = Word.query.get(word_id)
        if not word:
            return None, "词汇不存在"

        # 保存文件
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        dialect_folder = os.path.join(upload_folder, 'dialects')
        os.makedirs(dialect_folder, exist_ok=True)

        # 生成唯一文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{word_id}_{region.replace(' ', '_')}_{timestamp}.{video_file.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(dialect_folder, filename)
        video_file.save(filepath)

        # 相对路径（用于URL）
        video_url = f"/uploads/dialects/{filename}"

        # 创建记录
        dialect = DialectUpload(
            user_id=user_id,
            word_id=word_id,
            region=region,
            video_url=video_url,
            description=description,
            status='pending'
        )
        db.session.add(dialect)
        db.session.commit()

        return dialect, "上传成功"

    @staticmethod
    def get_my_uploads(user_id):
        """获取我的上传记录"""
        dialects = DialectUpload.query.filter_by(user_id=user_id).order_by(DialectUpload.created_at.desc()).all()
        return [d.to_dict() for d in dialects]

    @staticmethod
    def get_word_dialects(word_id):
        """获取词汇的已审核方言"""
        dialects = DialectUpload.query.filter_by(
            word_id=word_id, 
            status='approved'
        ).all()
        return [d.to_dict() for d in dialects]

# ==================== 统计服务 ====================
class StatsService:
    """学习统计服务"""

    @staticmethod
    def get_overview(user_id):
        """获取学习概览"""
        from backend.models import Word
        user = User.query.get(user_id)
        records = LearningRecord.query.filter_by(user_id=user_id).all()

        total_practice = sum(r.practice_count for r in records)
        total_correct = sum(r.correct_count for r in records)
        avg_accuracy = total_correct / total_practice if total_practice > 0 else 0.0

        # 已学习的词汇数
        learned_words = LearningRecord.query.filter_by(user_id=user_id, is_learned=True).count()

        # 计算总学习时长（从练习记录估算）
        # 每次练习约3分钟
        total_minutes = total_practice * 3
        total_hours = round(total_minutes / 60, 1)

        # 掌握率：已掌握词汇数 / 已学习词汇数
        mastered_words = LearningRecord.query.filter_by(user_id=user_id, is_learned=True).count()
        mastery_rate = round(mastered_words / learned_words * 100, 1) if learned_words > 0 else 0

        # 成就数（暂时返回0，后续可扩展）
        achievements = 0

        return {
            'learned_words': learned_words,
            'total_words': Word.query.count(),
            'mastery_rate': mastery_rate,
            'total_hours': total_hours,
            'total_minutes': total_minutes,
            'level': user.level if user else 1,
            'exp': user.exp if user else 0,
            'points': user.points if user else 0,
            'streak_days': user.streak_days if user else 0,
            'achievements': achievements,
            'avg_accuracy': round(avg_accuracy * 100, 1),
            'total_practice': total_practice
        }

    @staticmethod
    def get_chart_data(user_id, period='week'):
        """
        获取图表数据
        period: 'week' | 'month' | 'year'
        返回数组格式: [{date, minutes, words_count}]
        """
        from datetime import date

        today = date.today()
        result = []

        if period == 'week':
            # 近7天
            for i in range(6, -1, -1):
                d = today - timedelta(days=i)
                stat = StudyStat.query.filter_by(user_id=user_id, date=d).first()
                # 每次练习约3分钟
                minutes = (stat.practice_count if stat else 0) * 3
                result.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'minutes': minutes,
                    'words_count': stat.words_count if stat else 0,
                    'practice_count': stat.practice_count if stat else 0
                })

        elif period == 'month':
            # 近30天
            for i in range(29, -1, -1):
                d = today - timedelta(days=i)
                stat = StudyStat.query.filter_by(user_id=user_id, date=d).first()
                minutes = (stat.practice_count if stat else 0) * 3
                result.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'minutes': minutes,
                    'words_count': stat.words_count if stat else 0,
                    'practice_count': stat.practice_count if stat else 0
                })

        elif period == 'year':
            # 整年，按月聚合
            year = int(request.args.get('year', today.year))
            for month in range(1, 13):
                stat = StudyStat.query.filter_by(user_id=user_id, date=date(year, month, 1)).first()
                month_minutes = 0
                month_words = 0
                month_practice = 0
                # 跨月汇总该月所有日
                from calendar import monthrange
                _, last_day = monthrange(year, month)
                for day in range(1, last_day + 1):
                    d = date(year, month, day)
                    s = StudyStat.query.filter_by(user_id=user_id, date=d).first()
                    if s:
                        month_minutes += (s.practice_count or 0) * 3
                        month_words += s.words_count or 0
                        month_practice += s.practice_count or 0
                result.append({
                    'date': f'{year}-{month:02d}',
                    'minutes': month_minutes,
                    'words_count': month_words,
                    'practice_count': month_practice
                })

        return result

    @staticmethod
    def get_radar_data(user_id):
        """
        获取雷达图数据：按词汇分类维度计算掌握度
        返回 {daily, social, emotion, life, tech} 各维度 0-100
        """
        category_map = {
            '日常': 'daily',
            '社会': 'social',
            '情感': 'emotion',
            '生活': 'life',
            '科技': 'tech',
        }
        result = {k: 0 for k in category_map.values()}

        records = (
            LearningRecord.query
            .join(Word)
            .filter(LearningRecord.user_id == user_id, LearningRecord.is_learned == True)
            .all()
        )
        if not records:
            return result

        cat_stats = {}
        for r in records:
            cat = r.word.category if r.word else '日常'
            key = category_map.get(cat, 'daily')
            if key not in cat_stats:
                cat_stats[key] = {'total': 0, 'correct': 0}
            cat_stats[key]['total'] += r.practice_count or 1
            cat_stats[key]['correct'] += r.correct_count or 0

        for key, stat in cat_stats.items():
            result[key] = round(
                (stat['correct'] / stat['total'] * 100) if stat['total'] > 0 else 0
            )

        return result

    @staticmethod
    def get_ranking(limit=10, user_id=None):
        """
        获取学习排行榜，按累计学习时长排序
        时长 = SUM(study_stats.minutes)
        user_id: 当前登录用户ID，用于标记 isMe
        """
        from sqlalchemy import func

        ranking = (
            db.session.query(
                User.id,
                User.username,
                User.avatar_url,
                User.level,
                func.coalesce(func.sum(StudyStat.minutes), 0).label('total_minutes')
            )
            .outerjoin(StudyStat, User.id == StudyStat.user_id)
            .group_by(User.id)
            .order_by(func.coalesce(func.sum(StudyStat.minutes), 0).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                'id': row.id,
                'name': row.username,
                'avatar': row.avatar_url,
                'level': row.level,
                'hours': round(row.total_minutes / 60, 1),
                'minutes': row.total_minutes,
                'isMe': row.id == user_id
            }
            for row in ranking
        ]

# ==================== 积分与等级服务 ====================
class PointsService:
    """积分与等级服务"""

    # 每级需要的积分
    POINTS_PER_LEVEL = 100

    @staticmethod
    def add_points(user_id, points, reason=''):
        """
        增加用户积分
        Returns: (new_points, level_up, new_level)
        """
        user = User.query.get(user_id)
        if not user:
            return None, False, None

        old_level = user.level
        old_points = user.points

        # 增加积分
        user.points += points

        # 检查是否升级
        level_up = False
        new_level = old_level
        while user.points >= new_level * PointsService.POINTS_PER_LEVEL:
            new_level += 1
            level_up = True

        user.level = new_level
        db.session.commit()

        return user.points, level_up, new_level

    @staticmethod
    def deduct_points(user_id, points):
        """
        扣除用户积分
        Returns: (success, new_points)
        """
        user = User.query.get(user_id)
        if not user:
            return False, None

        if user.points < points:
            return False, user.points

        user.points -= points
        db.session.commit()

        return True, user.points

    @staticmethod
    def get_level_info(user_id):
        """获取用户等级信息"""
        user = User.query.get(user_id)
        if not user:
            return None

        current_level_points = (user.level - 1) * PointsService.POINTS_PER_LEVEL
        next_level_points = user.level * PointsService.POINTS_PER_LEVEL
        progress = user.points - current_level_points
        total_needed = PointsService.POINTS_PER_LEVEL

        return {
            'level': user.level,
            'points': user.points,
            'current_level_points': current_level_points,
            'next_level_points': next_level_points,
            'progress': progress,
            'total_needed': total_needed,
            'progress_percent': round(progress / total_needed * 100, 1)
        }

    @staticmethod
    def get_points_history(user_id, limit=20):
        """获取积分变动历史（可扩展）"""
        # 简化版：返回各来源统计
        return {
            'arena': 0,
            'learning': 0,
            'review': 0,
            'community': 0,
            'dialect': 0
        }

# ==================== 竞技场服务 ====================
class ArenaService:
    """竞技场服务 - 从所有词汇中随机抽取题目"""

    # 竞技场题目数量
    ARENA_QUESTION_COUNT = 10
    # 每题答题时间（秒）
    ARENA_TIME_LIMIT = 8
    # 答对奖励积分
    ARENA_POINTS_PER_CORRECT = 1

    @staticmethod
    def generate_arena_questions(user_id):
        """
        生成竞技场题目
        只从有视频的词汇中抽取题目，确保包含阶段2（选择题）和阶段3（看视频输入）
        Returns: dict {questions, total_count}
        """
        # 只获取有视频的词汇
        words_with_video = Word.query.filter(Word.demo_video_url.isnot(None)).all()

        if not words_with_video:
            return None, '词库为空，没有有视频的词汇'

        # 确保有足够的有视频词汇
        if len(words_with_video) < ArenaService.ARENA_QUESTION_COUNT:
            return None, f'有视频的词汇不足，需要至少{ArenaService.ARENA_QUESTION_COUNT}个，当前只有{len(words_with_video)}个'

        # 随机打乱词汇
        import random
        random.shuffle(words_with_video)

        # 计算各类题目数量（各占一半）
        half_count = ArenaService.ARENA_QUESTION_COUNT // 2
        stage2_count = half_count
        stage3_count = ArenaService.ARENA_QUESTION_COUNT - half_count  # 处理奇数情况

        # 分割词汇
        stage2_words = words_with_video[:stage2_count]
        stage3_words = words_with_video[stage2_count:stage2_count + stage3_count]

        # 生成阶段2选择题
        stage2_questions = []
        stage2_word_ids = []
        for word in stage2_words:
            choice_data = LearningCenterService._get_or_create_choice_options(
                user_id, word.id, 'learn', word
            )
            stage2_questions.append({
                'word_id': word.id,
                'word': word.word,
                'stage': 2,
                'stage_name': '选择题',
                'question_text': choice_data['question_text'],
                'options': choice_data['options'],
                'correct_index': choice_data['correct_index']
            })
            stage2_word_ids.append(word.id)

        # 生成阶段3看视频输入题
        stage3_questions = []
        for word in stage3_words:
            stage3_questions.append({
                'word_id': word.id,
                'word': word.word,
                'stage': 3,
                'stage_name': '看视频输入',
                'video_url': word.demo_video_url,
                'image_url': word.image_url
            })

        # 合并并打乱题目顺序
        questions = stage2_questions + stage3_questions
        random.shuffle(questions)

        return {
            'questions': questions,
            'total_count': len(questions),
            'time_limit': ArenaService.ARENA_TIME_LIMIT,
            'points_per_correct': ArenaService.ARENA_POINTS_PER_CORRECT
        }, None

    @staticmethod
    def submit_arena_answer(user_id, question_index, answer_data):
        """
        提交竞技场答案
        answer_data: {'selected_index': int} 或 {'user_input': str}
        Returns: {is_correct, correct_answer}
        """
        # 答案验证逻辑在提交完整结果时处理
        return {'is_correct': None, 'correct_answer': None}

    @staticmethod
    def finish_arena(user_id, answers):
        """
        完成竞技场
        answers: [{word_id, stage, is_correct}]
        Returns: {correct_count, total_count, points_earned, level_up, new_level}
        """
        correct_count = sum(1 for a in answers if a.get('is_correct'))

        # 计算奖励积分
        points_earned = correct_count * ArenaService.ARENA_POINTS_PER_CORRECT

        # 添加积分
        new_points, level_up, new_level = PointsService.add_points(user_id, points_earned, '竞技场')

        return {
            'correct_count': correct_count,
            'total_count': len(answers),
            'points_earned': points_earned,
            'total_points': new_points,
            'level_up': level_up,
            'new_level': new_level
        }
