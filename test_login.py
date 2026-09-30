import urllib.request, json, urllib.error

base = 'http://127.0.0.1:8000/api'

# Login
body = json.dumps({'username': 'Ronan josé', 'password': '123456'}).encode()
req = urllib.request.Request(base + '/auth/login', data=body, headers={'Content-Type': 'application/json'})
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode('utf-8'))
    print("Login resp:", data)
    token = data.get('access_token', '')
    print("Login: OK" if token else "Login: FAIL - no token")
except urllib.error.HTTPError as e:
    print("Login HTTP error:", e.code, e.read().decode('utf-8'))
