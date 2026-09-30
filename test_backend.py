from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Login as admin (first user with is_admin=1)
import sqlite3
conn = sqlite3.connect('robocode.db')
cursor = conn.cursor()
cursor.execute("SELECT username FROM users WHERE is_admin = 1 LIMIT 1")
admin_user = cursor.fetchone()[0]
conn.close()

login_resp = client.post('/api/auth/login', json={'username': admin_user, 'password': '123456'})
print("Login:", login_resp.status_code, 'OK' if login_resp.status_code == 200 else 'FAIL')
token = login_resp.json().get('access_token', '')
headers = {'Authorization': f'Bearer {token}'}

# 1. CREATE activity with input_data + expected_output (no solution_code)
new_act = client.post('/api/admin/activities', headers=headers, json={
    'phase': 11,
    'title': 'Test Input Debug',
    'description': 'Testing new fields',
    'difficulty': 'EASY',
    'xp_reward': 50,
    'initial_code': '#codigo\n',
    'input_data': '10\n20',
    'expected_output': 'Energia total: 30'
})
print("\nCREATE activity:", new_act.status_code)
if new_act.status_code == 200:
    data = new_act.json()
    print("  id:", data.get('id'))
    print("  test_cases:", data.get('test_cases'))
    act_id = data['id']
else:
    print("  error:", new_act.json())
    exit()

# 2. EDIT activity - update test case
updated = client.put(f'/api/admin/activities/{act_id}', headers=headers, json={
    'input_data': '5\n7',
    'expected_output': 'Energia total: 12'
})
print("\nUPDATE activity:", updated.status_code)
if updated.status_code == 200:
    data = updated.json()
    print("  test_cases:", data.get('test_cases'))

# 3. GET full
full = client.get(f'/api/admin/activities/{act_id}/full', headers=headers)
print("\nGET full:", full.status_code)
if full.status_code == 200:
    data = full.json()
    print("  test_cases:", data.get('test_cases'))

# 4. SUBMIT with input() code
code = 'n1 = int(input())\nn2 = int(input())\nprint("Energia total:", n1 + n2)'
submit = client.post('/api/activities/submit', json={'activity_id': act_id, 'code': code}, headers=headers)
print("\nSUBMIT:", submit.status_code)
if submit.status_code == 200:
    data = submit.json()
    print("  passed:", data.get('passed'))
    for r in data.get('results', []):
        print(f"  tc {r.get('test_case_id')}: passed={r.get('passed')} input={repr(r.get('input_data'))}")
else:
    print("  error:", submit.json())

# Cleanup
client.delete(f'/api/admin/activities/{act_id}', headers=headers)
print("\nCleanup: activity deleted")
