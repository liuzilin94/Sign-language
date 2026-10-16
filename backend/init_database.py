"""数据库初始化脚本"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app, db
from backend.models import User, Word, Task, Achievement
from backend.services import hash_password, WordService

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")

        # 检查是否已有管理员
        admin = User.query.filter_by(username='admin').first()
        if not admin:
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
            print("管理员账号创建: admin / admin123")
        else:
            print("管理员账号已存在")

        # 创建测试用户
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                phone='13900000001',
                password_hash=hash_password('test123'),
                level=1,
                points=0,
                role='user'
            )
            db.session.add(test_user)
            print("测试账号创建: testuser / test123")
        else:
            print("测试账号已存在")

        # 检查是否已有词汇
        word_count = Word.query.count()
        print(f"当前词汇数量: {word_count}")

        # 导入词汇表
        corpus_path = os.path.join(app.root_path, '..', 'dataset', 'corpus.txt')
        video_path = os.path.join(app.root_path, '..', 'video')
        
        if os.path.exists(corpus_path):
            # 从corpus.txt导入词汇
            from backend.services import WordService
            count = WordService.import_from_corpus(corpus_path, video_path)
            print(f"从corpus.txt导入词汇: {count}个")
        else:
            print(f"词汇表文件不存在: {corpus_path}")
            # 创建几个测试词汇
            test_words = [
                Word(backend_id='000001', word='你好', category='基础', difficulty=1),
                Word(backend_id='000002', word='谢谢', category='基础', difficulty=1),
                Word(backend_id='000003', word='再见', category='基础', difficulty=1),
                Word(backend_id='000004', word='对不起', category='基础', difficulty=2),
                Word(backend_id='000005', word='请', category='基础', difficulty=1),
            ]
            for w in test_words:
                if not Word.query.filter_by(backend_id=w.backend_id).first():
                    db.session.add(w)
            print("创建测试词汇")

        # 创建默认任务
        default_tasks = [
            Task(title='每日学习', description='学习3个新词', type='learn', target=3, reward_points=10, reward_exp=20),
            Task(title='每日复习', description='复习5个词汇', type='review', target=5, reward_points=5, reward_exp=10),
            Task(title='完成练习', description='完成10次练习', type='practice', target=10, reward_points=8, reward_exp=15),
            Task(title='社交达人', description='发布1条动态', type='social', target=1, reward_points=3, reward_exp=5),
        ]
        for t in default_tasks:
            if not Task.query.filter_by(title=t.title).first():
                db.session.add(t)
        print("默认任务创建完成")

        # 创建默认成就
        default_achievements = [
            Achievement(title='初学者', description='完成首次学习', icon='star', type='learn', reward_points=5, reward_exp=10),
            Achievement(title='连续3天', description='连续学习3天', icon='fire', type='streak', reward_points=10, reward_exp=20),
            Achievement(title='词汇达人', description='学会10个词汇', icon='trophy', type='learn', reward_points=20, reward_exp=50),
        ]
        for a in default_achievements:
            if not Achievement.query.filter_by(title=a.title).first():
                db.session.add(a)
        print("默认成就创建完成")

        db.session.commit()
        print("\n数据库初始化完成!")
        
        # 显示统计
        print("\n=== 数据库统计 ===")
        print(f"用户数: {User.query.count()}")
        print(f"词汇数: {Word.query.count()}")
        print(f"任务数: {Task.query.count()}")
        print(f"成就数: {Achievement.query.count()}")

if __name__ == '__main__':
    init_database()
