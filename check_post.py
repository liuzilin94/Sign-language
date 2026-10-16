#!/usr/bin/env python3
"""
Check community post issue
"""
import sys
import os
import paramiko

SERVER = "101.201.59.20"
USER = "root"
PASSWORD = "Liu8287860"
REMOTE_PATH = "/opt/csl-recognition"

def run_command(client, command, sudo=False, timeout=60):
    if sudo:
        command = f"echo {PASSWORD} | sudo -S {command}"
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    if sudo:
        stdin.write(PASSWORD + "\n")
        stdin.flush()
    return stdout.read().decode('utf-8', errors='replace'), stderr.read().decode('utf-8', errors='replace')

def main():
    print("=" * 60)
    print("Checking Community Post Issue")
    print("=" * 60)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

    # Check posts route
    print("\n[1] Checking posts route...")
    stdout, _ = run_command(client, f"grep -n 'posts\\|/api/posts' {REMOTE_PATH}/backend/app.py | head -20")
    print(f"  {stdout}")

    # Check recent logs for post errors
    print("\n[2] Checking recent logs...")
    stdout, _ = run_command(client, "journalctl -u csl-backend -n 30 --since '10 minutes ago' --no-pager 2>&1 | grep -i 'post\\|error\\|403\\|401'", sudo=True)
    print(f"  {stdout[:600] if stdout else 'No relevant logs'}")

    # Check users in database
    print("\n[3] Checking users...")
    check_script = f'''#!/usr/bin/env python3
import sys
sys.path.insert(0, "{REMOTE_PATH}")

from backend.app import app, db
from backend.models import User

with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"ID: {{u.id}}, Username: {{u.username}}, Phone: {{u.phone}}, Role: {{u.role}}")
'''
    cmd = f"cat > {REMOTE_PATH}/check_users.py << 'TESTEOF'\n{check_script}TESTEOF"
    run_command(client, cmd)

    stdout, _ = run_command(client, f"cd {REMOTE_PATH} && python3 check_users.py 2>&1")
    print(f"  {stdout}")

    # Test create post with new user
    print("\n[4] Testing create post...")
    test_script = f'''#!/usr/bin/env python3
import sys
sys.path.insert(0, "{REMOTE_PATH}")

from backend.app import app

with app.test_client() as client:
    # Login as first user (admin)
    resp = client.post('/api/auth/login',
        json={{"phone": "13800000000", "password": "admin123"}},
        content_type='application/json')
    data = resp.get_json()
    if data and data.get('code') == 200:
        token = data['data']['token']
        print(f"Login OK, token: {{token[:30]}}...")

        # Try to create post
        resp = client.post('/api/posts',
            json={{"title": "Test Post", "content": "Test content"}},
            headers={{"Authorization": f"Bearer {{token}}"}})
        print(f"Create post status: {{resp.status_code}}")
        print(f"Response: {{resp.get_json()}}")
'''
    cmd = f"cat > {REMOTE_PATH}/test_post.py << 'TESTEOF'\n{test_script}TESTEOF"
    run_command(client, cmd)

    stdout, _ = run_command(client, f"cd {REMOTE_PATH} && python3 test_post.py 2>&1")
    print(stdout)

    # Cleanup
    run_command(client, f"rm -f {REMOTE_PATH}/check_users.py {REMOTE_PATH}/test_post.py")

    client.close()

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
