import sys
sys.path.insert(0, '.')
import sqlite3
from app.auth import hash_password

conn = sqlite3.connect('robocode.db')
cursor = conn.cursor()

# Search for the user by name
cursor.execute("SELECT id, username, name FROM users WHERE name = 'EDUARDA SILVA DE ARAÚJO'")
row = cursor.fetchone()

if row:
    user_id, username, name = row
    new_hash = hash_password('123456')
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))
    conn.commit()
    print(f'Password updated for user: {name} (ID: {user_id}, username: {username})')
else:
    print('User not found. Searching for similar names...')
    cursor.execute("SELECT id, username, name FROM users WHERE name LIKE '%eduarda%' OR name LIKE '%araujo%' COLLATE NOCASE")
    rows = cursor.fetchall()
    for r in rows:
        print(f'Found: ID={r[0]}, username={r[1]}, name={r[2]}')

conn.close()
