import sqlite3
import hashlib
import base64
import secrets
import time

DB = 'db.sqlite3'
USERNAME = 'admin'
PASSWORD = 'admin123'  # change after login for safety
ITERATIONS = 1200000
SALT_LEN = 12


def make_django_pbkdf2_sha256(password, salt=None, iterations=ITERATIONS):
    if salt is None:
        salt = secrets.token_urlsafe(SALT_LEN)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
    hash_b64 = base64.b64encode(dk).decode('ascii')
    return f"pbkdf2_sha256${iterations}${salt}${hash_b64}"


def upsert_admin(db=DB, username=USERNAME, password=PASSWORD):
    pw_hash = make_django_pbkdf2_sha256(password)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    # check if user exists
    cur.execute("SELECT id FROM accounts_user WHERE username=?", (username,))
    row = cur.fetchone()
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    if row:
        user_id = row[0]
        cur.execute("UPDATE accounts_user SET password=?, is_superuser=1, is_staff=1, is_active=1, role=? WHERE id=?",
                    (pw_hash, 'ADMIN', user_id))
        print(f"Updated existing user '{username}' with new password.")
    else:
        # insert new user; id will be auto
        cur.execute(
            "INSERT INTO accounts_user (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, role) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (pw_hash, None, 1, username, '', '', f'{username}@example.com', 1, 1, now, 'ADMIN')
        )
        print(f"Created new superuser '{username}'.")
    conn.commit()
    conn.close()
    print('Credentials:')
    print('  username:', username)
    print('  password:', password)
    print('\nPlease log in and change this password immediately via the admin or profile settings.')


if __name__ == '__main__':
    upsert_admin()
