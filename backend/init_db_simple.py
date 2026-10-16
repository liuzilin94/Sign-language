"""简化数据库初始化脚本"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app, db
from backend.models import User, Word, Task, Achievement
from backend.services import hash_password

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("[OK] Database tables created")

        # 检查是否已有管理员
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                phone='13800000000',
                password_hash=hash_password('admin123'),
                level=10,
                points=9999,
                role='admin'
            )
            db.session.add(admin)
            print("[OK] Admin created: admin/admin123")
        else:
            print("[OK] Admin exists")

        # 检查词汇数量
        word_count = Word.query.count()
        print(f"[INFO] Current words: {word_count}")

        # 创建测试词汇
        test_words = [
            {'backend_id': '000001', 'word': '你好', 'category': '基础', 'difficulty': 1, 'tips': '["手掌向上","五指伸直"]', 'steps': '["步骤1: 手掌向上","步骤2: 五指伸直并拢"]'},
            {'backend_id': '000002', 'word': '谢谢', 'category': '基础', 'difficulty': 1, 'tips': '["手指并拢","前后摆动"]', 'steps': '["步骤1: 手指并拢","步骤2: 前后摆动"]'},
            {'backend_id': '000003', 'word': '再见', 'category': '基础', 'difficulty': 1, 'tips': '["手掌挥动"]', 'steps': '["步骤1: 手掌向外挥动"]'},
            {'backend_id': '000004', 'word': '对不起', 'category': '基础', 'difficulty': 2, 'tips': '["拳头上下移动"]', 'steps': '["步骤1: 握拳","步骤2: 上下移动"]'},
            {'backend_id': '000005', 'word': '请', 'category': '基础', 'difficulty': 1, 'tips': '["手掌放在胸前"]', 'steps': '["步骤1: 手掌向上","步骤2: 放在胸前"]'},
            {'backend_id': '000006', 'word': '去', 'category': '基础', 'difficulty': 1, 'tips': '["手掌向前推出"]', 'steps': '["步骤1: 手掌向前","步骤2: 向前推出"]'},
            {'backend_id': '000007', 'word': '来', 'category': '基础', 'difficulty': 1, 'tips': '["手掌向身体方向移动"]', 'steps': '["步骤1: 手掌向外","步骤2: 向身体方向移动"]'},
            {'backend_id': '000008', 'word': '中国', 'category': '地区', 'difficulty': 2, 'tips': '["双手比划"]', 'steps': '["步骤1: 双手比划方形","步骤2: 象征中国"]'},
        ]

        added = 0
        for wdata in test_words:
            if not Word.query.filter_by(backend_id=wdata['backend_id']).first():
                word = Word(**wdata)
                db.session.add(word)
                added += 1

        if added > 0:
            print(f"[OK] Added {added} test words")

        # 创建默认任务
        default_tasks = [
            {'title': '每日学习', 'description': '学习3个新词', 'type': 'learn', 'target': 3, 'reward_points': 10, 'reward_exp': 20},
            {'title': '每日复习', 'description': '复习5个词汇', 'type': 'review', 'target': 5, 'reward_points': 5, 'reward_exp': 10},
            {'title': '完成练习', 'description': '完成10次练习', 'type': 'practice', 'target': 10, 'reward_points': 8, 'reward_exp': 15},
        ]
        for tdata in default_tasks:
            if not Task.query.filter_by(title=tdata['title']).first():
                task = Task(**tdata)
                db.session.add(task)
                print(f"[OK] Task: {tdata['title']}")

        # 创建默认成就
        default_achievements = [
            {'title': '初学者', 'description': '完成首次学习', 'icon': 'star', 'type': 'learn', 'reward_points': 5, 'reward_exp': 10},
            {'title': '连续3天', 'description': '连续学习3天', 'icon': 'fire', 'type': 'streak', 'reward_points': 10, 'reward_exp': 20},
        ]
        for adata in default_achievements:
            if not Achievement.query.filter_by(title=adata['title']).first():
                ach = Achievement(**adata)
                db.session.add(ach)
                print(f"[OK] Achievement: {adata['title']}")

        db.session.commit()
        print("\n=== Database Stats ===")
        print(f"Users: {User.query.count()}")
        print(f"Words: {Word.query.count()}")
        print(f"Tasks: {Task.query.count()}")
        print(f"Achievements: {Achievement.query.count()}")
        print("\n[SUCCESS] Database initialized!")

if __name__ == '__main__':
    init_database()
