import urllib.request, json, urllib.error

base = 'http://127.0.0.1:8000/api'

def api(method, path, body=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8'))

# Login as admin (first user)
try:
    data = api('POST', '/auth/register', {'username': 'admin2', 'password': '123456'})
except:
    pass
data = api('POST', '/auth/login', {'username': 'admin2', 'password': '123456'})
token = data['access_token']
print("Login admin: OK")

# 1. CREATE activity with input_data + expected_output (no solution_code)
new_act = api('POST', '/admin/activities', {
    'phase': 11,
    'title': 'Test Input Debug',
    'description': 'Testing input_data and expected_output fields',
    'difficulty': 'EASY',
    'xp_reward': 50,
    'initial_code': '#codigo\n',
    'solution_code': None,
    'input_data': '10\n20',
    'expected_output': 'Energia total: 30'
}, token)
act_id = new_act['id']
print("\nCREATE activity:")
print("  id:", act_id)
print("  test_cases:", new_act.get('test_cases'))
tc_id = new_act['test_cases'][0]['id'] if new_act.get('test_cases') else None
print("  test_case id:", tc_id)

# 2. EDIT activity - update expected_output
updated = api('PUT', f'/admin/activities/{act_id}', {
    'input_data': '5\n7',
    'expected_output': 'Energia total: 12'
}, token)
print("\nUPDATE activity (edit expected_output):")
print("  test_cases:", updated.get('test_cases'))

# 3. GET full activity to verify
full = api('GET', f'/admin/activities/{act_id}/full', None, token)
print("\nGET full:")
print("  test_cases:", full.get('test_cases'))

# 4. Test submit with solution code matching expected_output
code = 'n1 = int(input())\nn2 = int(input())\nprint("Energia total:", n1 + n2)'
# First set solution_code so test_solution can work, and test the submit
submit = api('POST', '/activities/submit', {'activity_id': act_id, 'code': code}, token)
print("\nSUBMIT activity (input() code):")
print("  passed:", submit.get('passed'))
print("  message:", 'OK' if submit.get('passed') else submit.get('message','')[:80])
