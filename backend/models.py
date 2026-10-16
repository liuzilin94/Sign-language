"""
数据模型 - 精简版（核心4表 + 扩展表）
所有模型合并为一个文件，便于快速部署
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ==================== 用户模型 ====================
class User(db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    phone = db.Column(db.String(20), unique=True, nullable=False, comment='手机号')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    avatar_url = db.Column(db.String(500), default='default.png', comment='头像')
    level = db.Column(db.Integer, default=1, comment='等级')
    exp = db.Column(db.Integer, default=0, comment='经验值')
    points = db.Column(db.Integer, default=0, comment='积分')
    streak_days = db.Column(db.Integer, default=0, comment='连续学习天数')
    last_active_date = db.Column(db.Date, comment='最后活跃日期')
    role = db.Column(db.String(20), default='user', comment='角色: user=普通用户, admin=管理员')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    learning_records = db.relationship('LearningRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    review_schedules = db.relationship('ReviewSchedule', backref='user', lazy=True, cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='user', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', lazy=True, cascade='all, delete-orphan')
    dialect_uploads = db.relationship('DialectUpload', foreign_keys='DialectUpload.user_id', backref='user', lazy=True, cascade='all, delete-orphan')
    reviewed_dialects = db.relationship('DialectUpload', foreign_keys='DialectUpload.reviewer_id', backref='reviewer', lazy=True)
    study_stats = db.relationship('StudyStat', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'level': self.level,
            'exp': self.exp,
            'points': self.points,
            'streak_days': self.streak_days,
            'last_active_date': self.last_active_date.isoformat() if self.last_active_date else None,
            'role': self.role or 'user',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ==================== 词汇模型 ====================
class Word(db.Model):
    """词汇表 - 从corpus.txt同步"""
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    backend_id = db.Column(db.String(20), unique=True, nullable=False, comment='corpus.txt中的ID')
    word = db.Column(db.String(50), nullable=False, comment='词汇文字')
    category = db.Column(db.String(20), default='基础', comment='分类')
    scene = db.Column(db.String(20), comment='场景')
    difficulty = db.Column(db.Integer, default=1, comment='难度等级')
    region = db.Column(db.String(20), default='全国通用', comment='地区/方言')
    tips = db.Column(db.Text, comment='手型要点(JSON数组)')
    steps = db.Column(db.Text, comment='动作分解(JSON数组)')
    demo_video_url = db.Column(db.String(500), comment='示范视频路径')
    glb_model_file = db.Column(db.String(100), comment='3D模型文件名')
    image_url = db.Column(db.String(500), comment='图解图片路径')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关系
    learning_records = db.relationship('LearningRecord', backref='word', lazy=True)
    review_schedules = db.relationship('ReviewSchedule', backref='word', lazy=True, cascade='all, delete-orphan')
    dialect_uploads = db.relationship('DialectUpload', back_populates='word', lazy=True)

    def to_dict(self):
        """转换为字典格式"""
        import json
        return {
            'id': self.id,
            'backend_id': self.backend_id,
            'word': self.word,
            'category': self.category,
            'scene': self.scene,
            'difficulty': self.difficulty,
            'region': self.region,
            'tips': json.loads(self.tips) if self.tips else [],
            'steps': json.loads(self.steps) if self.steps else [],
            'demo_video_url': self.demo_video_url,
            'glb_model_file': self.glb_model_file,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ==================== 学习记录模型 ====================
class LearningRecord(db.Model):
    """学习记录表 - 替代localStorage"""
    __tablename__ = 'learning_records'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'word_id', name='unique_user_word'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    practice_count = db.Column(db.Integer, default=0, comment='练习次数')
    correct_count = db.Column(db.Integer, default=0, comment='正确次数')
    avg_accuracy = db.Column(db.Float, default=0.0, comment='平均准确率')
    last_practice_at = db.Column(db.DateTime, comment='最后练习时间')
    is_learned = db.Column(db.Boolean, default=False, comment='是否已学会')
    is_favorite = db.Column(db.Boolean, default=False, comment='是否收藏')
    notes = db.Column(db.Text, comment='用户笔记(JSON数组)')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典格式"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word_id': self.word_id,
            'word': self.word.word if self.word else None,
            'practice_count': self.practice_count,
            'correct_count': self.correct_count,
            'avg_accuracy': self.avg_accuracy,
            'last_practice_at': self.last_practice_at.isoformat() if self.last_practice_at else None,
            'is_learned': self.is_learned,
            'is_favorite': self.is_favorite,
            'notes': json.loads(self.notes) if self.notes else []
        }

# ==================== 复习计划模型 ====================
class ReviewSchedule(db.Model):
    """复习计划表 - 艾宾浩斯遗忘曲线"""
    __tablename__ = 'review_schedules'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'word_id', name='unique_user_word_review'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id', ondelete='CASCADE'), nullable=False)
    interval = db.Column(db.Integer, default=0, comment='当前间隔天数')
    next_review_at = db.Column(db.DateTime, nullable=False, comment='下次复习时间')
    last_review_at = db.Column(db.DateTime, comment='上次复习时间')
    correct_count = db.Column(db.Integer, default=0, comment='连续正确次数')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word_id': self.word_id,
            'word': self.word.word if self.word else None,
            'interval': self.interval,
            'next_review_at': self.next_review_at.isoformat() if self.next_review_at else None,
            'last_review_at': self.last_review_at.isoformat() if self.last_review_at else None,
            'correct_count': self.correct_count
        }

# ==================== 社区动态模型 ====================
class Post(db.Model):
    """社区动态表"""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False, comment='动态内容')
    images = db.Column(db.Text, comment='图片URL列表(JSON数组)')
    video_url = db.Column(db.String(500), comment='关联视频URL')
    word_tags = db.Column(db.Text, comment='关联词汇ID列表(JSON数组)')
    likes_count = db.Column(db.Integer, default=0, comment='点赞数')
    comments_count = db.Column(db.Integer, default=0, comment='评论数')
    status = db.Column(db.String(20), default='published', comment='状态：published/deleted')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典格式"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'avatar': self.user.avatar_url if self.user else None,
            'content': self.content,
            'images': json.loads(self.images) if self.images else [],
            'video_url': self.video_url,
            'word_tags': json.loads(self.word_tags) if self.word_tags else [],
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ==================== 评论模型 ====================
class Comment(db.Model):
    """评论表"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'avatar': self.user.avatar_url if self.user else None,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ==================== 方言上传模型 ====================
class DialectUpload(db.Model):
    """方言上传表 - 需审核"""
    __tablename__ = 'dialect_uploads'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    region = db.Column(db.String(50), nullable=False, comment='省份/城市')
    video_url = db.Column(db.String(500), nullable=False, comment='视频存储路径')
    description = db.Column(db.Text, comment='上传说明')
    status = db.Column(db.String(20), default='pending', comment='状态：pending/approved/rejected')
    reject_reason = db.Column(db.Text, comment='驳回原因')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='审核管理员ID')
    reviewed_at = db.Column(db.DateTime, comment='审核时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关系
    word = db.relationship('Word', back_populates='dialect_uploads', lazy=True)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'word_id': self.word_id,
            'word': self.word.word if self.word else None,
            'region': self.region,
            'video_url': self.video_url,
            'description': self.description,
            'status': self.status,
            'reject_reason': self.reject_reason,
            'reviewer': self.reviewer.username if self.reviewer else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ==================== 学习统计模型 ====================
class StudyStat(db.Model):
    """学习统计表 - 用于图表展示"""
    __tablename__ = 'study_stats'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_user_date'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, comment='统计日期')
    minutes = db.Column(db.Integer, default=0, comment='学习时长(分钟)')
    words_count = db.Column(db.Integer, default=0, comment='学习词汇数')
    practice_count = db.Column(db.Integer, default=0, comment='练习次数')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'minutes': self.minutes,
            'words_count': self.words_count,
            'practice_count': self.practice_count
        }

# ==================== 任务模型 ====================
class Task(db.Model):
    """每日任务表"""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment='任务标题')
    description = db.Column(db.Text, comment='任务描述')
    type = db.Column(db.String(20), comment='任务类型：practice/learn/social/review')
    target = db.Column(db.Integer, default=1, comment='目标数量')
    reward_points = db.Column(db.Integer, default=0, comment='奖励积分')
    reward_exp = db.Column(db.Integer, default=0, comment='奖励经验')
    is_daily = db.Column(db.Boolean, default=True, comment='是否每日任务')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'target': self.target,
            'reward_points': self.reward_points,
            'reward_exp': self.reward_exp,
            'is_daily': self.is_daily
        }

class UserTaskProgress(db.Model):
    """用户任务进度表"""
    __tablename__ = 'user_task_progress'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'task_id', 'date', name='unique_user_task_date'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    progress = db.Column(db.Integer, default=0, comment='当前进度')
    is_completed = db.Column(db.Boolean, default=False, comment='是否完成')
    completed_at = db.Column(db.DateTime, comment='完成时间')
    date = db.Column(db.Date, nullable=False, comment='任务日期')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关系
    task = db.relationship('Task', backref='progresses')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'task': self.task.to_dict() if self.task else None,
            'progress': self.progress,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'date': self.date.isoformat()
        }

# ==================== 成就模型 ====================
class Achievement(db.Model):
    """成就表"""
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False, comment='成就标题')
    description = db.Column(db.Text, comment='成就描述')
    icon = db.Column(db.String(100), comment='成就图标')
    type = db.Column(db.String(20), comment='成就类型')
    condition_json = db.Column(db.Text, comment='达成条件(JSON)')
    reward_points = db.Column(db.Integer, default=0, comment='奖励积分')
    reward_exp = db.Column(db.Integer, default=0, comment='奖励经验')
    is_hidden = db.Column(db.Boolean, default=False, comment='是否隐藏成就')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        """转换为字典格式"""
        import json
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'type': self.type,
            'condition': json.loads(self.condition_json) if self.condition_json else {},
            'reward_points': self.reward_points,
            'reward_exp': self.reward_exp,
            'is_hidden': self.is_hidden,
            'sort_order': self.sort_order
        }

class UserAchievement(db.Model):
    """用户成就表"""
    __tablename__ = 'user_achievements'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    progress = db.Column(db.Integer, default=0, comment='当前进度')
    is_unlocked = db.Column(db.Boolean, default=False, comment='是否已解锁')
    unlocked_at = db.Column(db.DateTime, comment='解锁时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关系
    achievement = db.relationship('Achievement', backref='user_achievements')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'achievement': self.achievement.to_dict() if self.achievement else None,
            'progress': self.progress,
            'is_unlocked': self.is_unlocked,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None
        }

# ==================== 学习进度模型 ====================
class LearningProgress(db.Model):
    """学习进度表 - 记录每个词每个阶段的完成状态"""
    __tablename__ = 'learning_progress'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'word_id', 'session_type', name='unique_user_word_session'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id', ondelete='CASCADE'), nullable=False)
    session_type = db.Column(db.String(20), default='learn', comment='learn=学习, review=复习')
    current_stage = db.Column(db.Integer, default=1, comment='当前阶段 1-4')
    stage1_passed = db.Column(db.Boolean, default=False, comment='阶段1: 看视频学习是否通过')
    stage2_passed = db.Column(db.Boolean, default=False, comment='阶段2: 选择题是否通过')
    stage3_passed = db.Column(db.Boolean, default=False, comment='阶段3: 看视频输入是否通过')
    stage4_passed = db.Column(db.Boolean, default=False, comment='阶段4: 手势识别是否通过')
    is_completed = db.Column(db.Boolean, default=False, comment='是否完成全部阶段')
    stage1_skipped = db.Column(db.Boolean, default=False, comment='阶段1是否跳过(复习模式)')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    user = db.relationship('User', backref='learning_progresses')
    word = db.relationship('Word', backref='learning_progresses')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word_id': self.word_id,
            'word': self.word.word if self.word else None,
            'session_type': self.session_type,
            'current_stage': self.current_stage,
            'stage1_passed': self.stage1_passed,
            'stage2_passed': self.stage2_passed,
            'stage3_passed': self.stage3_passed,
            'stage4_passed': self.stage4_passed,
            'stage1_skipped': self.stage1_skipped,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ==================== 用户学习设置模型 ====================
class UserLearningSettings(db.Model):
    """用户学习设置表"""
    __tablename__ = 'user_learning_settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    daily_new_words = db.Column(db.Integer, default=3, comment='每日新词数')
    daily_review_words = db.Column(db.Integer, default=5, comment='每日复习词数')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    user = db.relationship('User', backref='learning_settings')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'daily_new_words': self.daily_new_words,
            'daily_review_words': self.daily_review_words,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ==================== 每日计划模型 ====================
class DailyPlan(db.Model):
    """每日计划表"""
    __tablename__ = 'daily_plans'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'plan_date', name='unique_user_plan_date'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    plan_date = db.Column(db.Date, nullable=False, comment='计划日期')
    new_word_ids = db.Column(db.Text, comment='JSON数组：今日新词ID列表')
    review_word_ids = db.Column(db.Text, comment='JSON数组：今日复习词ID列表')
    learned_count = db.Column(db.Integer, default=0, comment='已完成新词数')
    reviewed_count = db.Column(db.Integer, default=0, comment='已完成复习词数')
    is_completed = db.Column(db.Boolean, default=False, comment='是否完成全部')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关系
    user = db.relationship('User', backref='daily_plans')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_date': self.plan_date.isoformat() if self.plan_date else None,
            'new_word_ids': json.loads(self.new_word_ids) if self.new_word_ids else [],
            'review_word_ids': json.loads(self.review_word_ids) if self.review_word_ids else [],
            'learned_count': self.learned_count,
            'reviewed_count': self.reviewed_count,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ==================== 选择题选项缓存模型 ====================
class LearningChoiceOptions(db.Model):
    """选择题选项缓存表"""
    __tablename__ = 'learning_choice_options'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'word_id', 'session_type', name='unique_user_word_choice'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id', ondelete='CASCADE'), nullable=False)
    session_type = db.Column(db.String(20), comment='learn=学习, review=复习')
    options = db.Column(db.Text, comment='JSON: 4个选项 [{id, word}]')
    correct_index = db.Column(db.Integer, comment='正确答案索引 0-3')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关系
    user = db.relationship('User', backref='choice_options')
    word = db.relationship('Word', backref='choice_options')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word_id': self.word_id,
            'session_type': self.session_type,
            'options': json.loads(self.options) if self.options else [],
            'correct_index': self.correct_index,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
