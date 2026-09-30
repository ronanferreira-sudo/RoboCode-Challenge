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
        err = e.read().decode('utf-8')
        return {'_error': err[:500]}

# Login as admin
data = api('POST', '/auth/login', {'username': 'Ronan josé', 'password': '123456'})
token = data.get('access_token', '')
print("Login admin:", 'OK' if token else 'FAILED')

# 1. CREATE activity with input_data + expected_output (NO solution_code)
new_act = api('POST', '/admin/activities', {
    'phase': 11,
    'title': 'Test Input Debug',
    'description': 'Testing new fields',
    'difficulty': 'EASY',
    'xp_reward': 50,
    'initial_code': '#codigo\n',
    'input_data': '10\n20',
    'expected_output': 'Energia total: 30'
}, token)
print("\nCREATE activity:")
print("  _error:", new_act.get('_error', 'NONE'))
print("  id:", new_act.get('id'))
print("  test_cases:", new_act.get('test_cases'))
act_id = new_act.get('id')

if act_id:
    tc_id = new_act['test_cases'][0]['id'] if new_act.get('test_cases') else None
    print("  test_case id:", tc_id)

    # 2. EDIT activity - update expected_output and input_data
    updated = api('PUT', f'/admin/activities/{act_id}', {
        'input_data': '5\n7',
        'expected_output': 'Energia total: 12'
    }, token)
    print("\nUPDATE activity (edit test case):")
    print("  _error:", updated.get('_error', 'NONE'))
    print("  test_cases:", updated.get('test_cases'))

    # 3. GET full activity
    full = api('GET', f'/admin/activities/{act_id}/full', None, token)
    print("\nGET full:")
    print("  test_cases:", full.get('test_cases'))

    # 4. Test submit with code using input()
    code = 'n1 = int(input())\nn2 = int(input())\nprint("Energia total:", n1 + n2)'
    # Need to set solution_code for test to pass - but we removed it from modal
    # The submit should use test_cases which have input_data/expected_output
    submit = api('POST', '/activities/submit', {'activity_id': act_id, 'code': code}, token)
    print("\nSUBMIT activity (input() code):")
    print("  _error:", submit.get('_error', 'NONE'))
    print("  passed:", submit.get('passed'))
    if submit.get('results'):
        for r in submit['results']:
            print(f"  tc {r.get('test_case_id')}: passed={r.get('passed')} input={repr(r.get('input_data'))}")
