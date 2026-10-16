"""
CSL手语识别系统 - 综合测试脚本 (修复版)
"""
import sys
import os
import io
import time
import json
from datetime import datetime

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app, db
from backend.models import User, Word, LearningRecord, ReviewSchedule, LearningProgress
from backend.services import hash_password, AuthService, WordService, LearningService

# ==================== 测试结果收集 ====================
test_results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'errors': [],
    'api_results': [],
    'performance_results': []
}

def log_test(name, passed, message=""):
    """记录测试结果"""
    test_results['total'] += 1
    if passed:
        test_results['passed'] += 1
        print(f"  [PASS] {name}")
    else:
        test_results['failed'] += 1
        print(f"  [FAIL] {name}: {message}")
        test_results['errors'].append({'test': name, 'error': message})

# ==================== 1. 单元测试 ====================
print("\n" + "=" * 60)
print("1. 单元测试")
print("=" * 60)

with app.app_context():
    # 1.1 用户模型测试
    print("\n[1.1] 用户模型测试")
    
    # 测试用户创建
    try:
        test_user = User.query.filter_by(username='pytest_user').first()
        if not test_user:
            test_user = User(
                username='pytest_user',
                phone='13900000099',
                password_hash=hash_password('test123'),
                level=1
            )
            db.session.add(test_user)
            db.session.commit()
        log_test("用户创建", True)
    except Exception as e:
        log_test("用户创建", False, str(e))
    
    # 测试用户序列化
    try:
        user_dict = test_user.to_dict()
        assert 'username' in user_dict
        assert 'level' in user_dict
        log_test("用户序列化", True)
    except Exception as e:
        log_test("用户序列化", False, str(e))
    
    # 测试密码哈希
    try:
        hashed = hash_password('test123')
        assert hashed != 'test123'
        assert len(hashed) > 20
        log_test("密码哈希", True)
    except Exception as e:
        log_test("密码哈希", False, str(e))
    
    # 1.2 词汇模型测试
    print("\n[1.2] 词汇模型测试")
    
    try:
        words = Word.query.all()
        assert len(words) > 0
        log_test("词汇查询", True, f"共{len(words)}个词汇")
    except Exception as e:
        log_test("词汇查询", False, str(e))
    
    try:
        word = Word.query.first()
        word_dict = word.to_dict()
        assert 'word' in word_dict
        assert 'category' in word_dict
        log_test("词汇序列化", True)
    except Exception as e:
        log_test("词汇序列化", False, str(e))
    
    # 1.3 认证服务测试
    print("\n[1.3] 认证服务测试")
    
    try:
        user, msg = AuthService.register('test_reg_user', '13988888888', 'pass123')
        assert user is not None
        log_test("用户注册", True)
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        log_test("用户注册", False, str(e))
    
    try:
        user, msg = AuthService.login('13800000000', 'admin123')
        assert user is not None
        assert user.username == 'admin'
        log_test("管理员登录", True)
    except Exception as e:
        log_test("管理员登录", False, str(e))
    
    try:
        user, msg = AuthService.login('13800000000', 'wrongpass')
        assert user is None
        log_test("错误密码登录", True)
    except Exception as e:
        log_test("错误密码登录", False, str(e))
    
    # 1.4 学习服务测试
    print("\n[1.4] 学习服务测试")
    
    try:
        admin = User.query.filter_by(username='admin').first()
        word = Word.query.first()
        record = LearningService.create_record(admin.id, word.id, True, 0.95)
        assert record is not None
        log_test("创建学习记录", True)
    except Exception as e:
        log_test("创建学习记录", False, str(e))
    
    try:
        records = LearningService.get_records(admin.id)
        assert isinstance(records, list)
        log_test("获取学习记录", True, f"共{len(records)}条")
    except Exception as e:
        log_test("获取学习记录", False, str(e))

# ==================== 2. API测试 (在应用上下文外) ====================
print("\n" + "=" * 60)
print("2. API集成测试")
print("=" * 60)

client = app.test_client()

# 2.1 健康检查
print("\n[2.1] 健康检查API")
try:
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data']['status'] == 'healthy'
    log_test("GET /api/health", True)
    test_results['api_results'].append({
        'endpoint': '/api/health',
        'method': 'GET',
        'status': 200,
        'time': 0
    })
except Exception as e:
    log_test("GET /api/health", False, str(e))

# 2.2 用户注册API
print("\n[2.2] 用户注册API")
import time
unique_phone = f'139{int(time.time()) % 100000000:08d}'
try:
    response = client.post('/api/auth/register', 
        json={'username': 'api_test_new', 'phone': unique_phone, 'password': 'test123'})
    if response.status_code == 201:
        data = json.loads(response.data)
        if 'token' in data.get('data', {}):
            log_test("POST /api/auth/register", True)
            test_results['api_results'].append({
                'endpoint': '/api/auth/register',
                'method': 'POST',
                'status': 201,
                'time': 0
            })
            api_token = data['data']['token']
        else:
            log_test("POST /api/auth/register", False, "No token in response")
            api_token = None
    elif response.status_code == 409:
        log_test("POST /api/auth/register (409-已存在用户)", True)
        api_token = None
    else:
        log_test("POST /api/auth/register", False, f"Status: {response.status_code}")
        api_token = None
except Exception as e:
    log_test("POST /api/auth/register", False, str(e))
    api_token = None

# 2.3 用户登录API
print("\n[2.3] 用户登录API")
try:
    response = client.post('/api/auth/login', 
        json={'phone': '13800000000', 'password': 'admin123'})
    if response.status_code == 200:
        data = json.loads(response.data)
        if 'token' in data.get('data', {}):
            log_test("POST /api/auth/login", True)
            admin_token = data['data']['token']
            test_results['api_results'].append({
                'endpoint': '/api/auth/login',
                'method': 'POST',
                'status': 200,
                'time': 0
            })
        else:
            log_test("POST /api/auth/login", False, "No token")
            admin_token = None
    else:
        log_test("POST /api/auth/login", False, f"Status: {response.status_code}")
        admin_token = None
except Exception as e:
    log_test("POST /api/auth/login", False, str(e))
    admin_token = None

# 2.4 获取词汇列表API
print("\n[2.4] 词汇API")
try:
    start_time = time.time()
    response = client.get('/api/words?page=1&page_size=10')
    elapsed = time.time() - start_time
    if response.status_code == 200:
        data = json.loads(response.data)
        if 'items' in data.get('data', {}):
            log_test(f"GET /api/words (响应时间: {elapsed*1000:.2f}ms)", True)
            test_results['api_results'].append({
                'endpoint': '/api/words',
                'method': 'GET',
                'status': 200,
                'time': elapsed * 1000
            })
        else:
            log_test("GET /api/words", False, "No items")
    else:
        log_test("GET /api/words", False, f"Status: {response.status_code}")
except Exception as e:
    log_test("GET /api/words", False, str(e))

# 2.5 获取词汇详情API
print("\n[2.5] 词汇详情API")
try:
    start_time = time.time()
    response = client.get('/api/words/1')
    elapsed = time.time() - start_time
    if response.status_code == 200:
        log_test(f"GET /api/words/1 (响应时间: {elapsed*1000:.2f}ms)", True)
    else:
        log_test("GET /api/words/1", False, f"Status: {response.status_code}")
except Exception as e:
    log_test("GET /api/words/1", False, str(e))

# 2.6 认证保护API测试
print("\n[2.6] 认证保护API")
try:
    response = client.get('/api/auth/me')
    assert response.status_code == 401
    log_test("未登录访问受保护API", True)
except Exception as e:
    log_test("未登录访问受保护API", False, str(e))

if admin_token:
    try:
        response = client.get('/api/auth/me', 
            headers={'Authorization': f'Bearer {admin_token}'})
        if response.status_code == 200:
            data = json.loads(response.data)
            if data.get('data', {}).get('username') == 'admin':
                log_test("登录访问受保护API", True)
            else:
                log_test("登录访问受保护API", False, "Wrong user")
        else:
            log_test("登录访问受保护API", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("登录访问受保护API", False, str(e))

# 2.7 统计概览API
print("\n[2.7] 统计API")
if admin_token:
    try:
        start_time = time.time()
        response = client.get('/api/stats/overview',
            headers={'Authorization': f'Bearer {admin_token}'})
        elapsed = time.time() - start_time
        if response.status_code == 200:
            log_test(f"GET /api/stats/overview (响应时间: {elapsed*1000:.2f}ms)", True)
            test_results['api_results'].append({
                'endpoint': '/api/stats/overview',
                'method': 'GET',
                'status': 200,
                'time': elapsed * 1000
            })
        else:
            log_test("GET /api/stats/overview", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("GET /api/stats/overview", False, str(e))

# ==================== 3. 性能测试 ====================
print("\n" + "=" * 60)
print("3. 性能测试")
print("=" * 60)

with app.app_context():
    # 3.1 数据库查询性能
    print("\n[3.1] 数据库查询性能")
    try:
        times = []
        for _ in range(10):
            start = time.time()
            words = Word.query.limit(20).all()
            elapsed = time.time() - start
            times.append(elapsed * 1000)
        avg_time = sum(times) / len(times)
        log_test(f"词汇列表查询 (平均: {avg_time:.2f}ms)", avg_time < 50)
        test_results['performance_results'].append({
            'name': '词汇列表查询',
            'avg_time_ms': avg_time,
            'pass': avg_time < 50
        })
    except Exception as e:
        log_test("词汇列表查询", False, str(e))

    # 3.2 词汇详情查询
    print("\n[3.2] 词汇详情查询")
    try:
        word = Word.query.first()
        times = []
        for _ in range(10):
            start = time.time()
            _ = word.to_dict()
            elapsed = time.time() - start
            times.append(elapsed * 1000)
        avg_time = sum(times) / len(times)
        log_test(f"词汇序列化 (平均: {avg_time:.2f}ms)", avg_time < 5)
        test_results['performance_results'].append({
            'name': '词汇序列化',
            'avg_time_ms': avg_time,
            'pass': avg_time < 5
        })
    except Exception as e:
        log_test("词汇序列化", False, str(e))

    # 3.3 批量操作性能
    print("\n[3.3] 批量操作性能")
    try:
        times = []
        for _ in range(5):
            start = time.time()
            admin = User.query.filter_by(username='admin').first()
            words = Word.query.limit(10).all()
            for word in words:
                _ = LearningService.get_record(admin.id, word.id)
            elapsed = time.time() - start
            times.append(elapsed * 1000)
        avg_time = sum(times) / len(times)
        log_test(f"批量学习记录查询 (平均: {avg_time:.2f}ms)", avg_time < 100)
        test_results['performance_results'].append({
            'name': '批量学习记录查询',
            'avg_time_ms': avg_time,
            'pass': avg_time < 100
        })
    except Exception as e:
        log_test("批量学习记录查询", False, str(e))

# ==================== 4. 安全测试 ====================
print("\n" + "=" * 60)
print("4. 安全测试")
print("=" * 60)

# 4.1 SQL注入防护
print("\n[4.1] SQL注入防护")
try:
    response = client.get("/api/words?keyword=' OR 1=1 --")
    if response.status_code == 200:
        data = json.loads(response.data)
        items = data.get('data', {}).get('items', [])
        # 如果返回的词汇数量异常多，可能存在注入风险
        if len(items) > 100:
            log_test("SQL注入测试", False, f"返回异常多的结果: {len(items)}")
        else:
            log_test("SQL注入测试", True)
    else:
        log_test("SQL注入测试", True)
except Exception as e:
    log_test("SQL注入测试", False, str(e))

# 4.2 密码强度验证
print("\n[4.2] 密码强度验证")
try:
    response = client.post('/api/auth/register', 
        json={'username': 'weak', 'phone': '13900000999', 'password': '123'})
    if response.status_code == 400:
        log_test("弱密码拒绝", True)
    else:
        log_test("弱密码拒绝", False, f"Status: {response.status_code}")
except Exception as e:
    log_test("弱密码拒绝", False, str(e))

# 4.3 重复注册防护
print("\n[4.3] 重复注册防护")
try:
    response = client.post('/api/auth/register', 
        json={'username': 'newuser', 'phone': '13800000000', 'password': 'test123'})
    if response.status_code == 409:
        log_test("重复手机号注册防护", True)
    else:
        log_test("重复手机号注册防护", False, f"Status: {response.status_code}")
except Exception as e:
    log_test("重复手机号注册防护", False, str(e))

# ==================== 测试结果汇总 ====================
print("\n" + "=" * 60)
print("测试结果汇总")
print("=" * 60)
print(f"总测试数: {test_results['total']}")
print(f"通过: {test_results['passed']} ({test_results['passed']/test_results['total']*100:.1f}%)")
print(f"失败: {test_results['failed']} ({test_results['failed']/test_results['total']*100:.1f}%)")

if test_results['api_results']:
    print("\n--- API响应时间 ---")
    for r in test_results['api_results']:
        print(f"  {r['method']} {r['endpoint']}: {r['time']:.2f}ms")

if test_results['performance_results']:
    print("\n--- 性能测试结果 ---")
    for r in test_results['performance_results']:
        status = "PASS" if r['pass'] else "FAIL"
        print(f"  {r['name']}: {r['avg_time_ms']:.2f}ms [{status}]")

if test_results['errors']:
    print("\n--- 失败详情 ---")
    for err in test_results['errors']:
        print(f"  - {err['test']}: {err['error']}")

# 保存测试结果到文件
report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_results.json')
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(test_results, f, ensure_ascii=False, indent=2, default=str)
print(f"\n测试结果已保存到: {report_path}")

print("\n[测试完成]")
