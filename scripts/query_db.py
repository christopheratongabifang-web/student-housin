import sqlite3
import sys

DB = 'db.sqlite3'
try:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cur.fetchall()]
    print('tables:', tables)
    candidates = [t for t in tables if 'user' in t.lower()]
    print('user-like tables:', candidates)
    for t in candidates:
        print('\nTable', t)
        cur.execute(f"PRAGMA table_info('{t}')")
        print('schema:', cur.fetchall())
        try:
            cur.execute(f"SELECT username,is_superuser,is_staff,email FROM '{t}' LIMIT 20")
            rows = cur.fetchall()
            print('rows sample:', rows)
        except Exception as e:
            print('select error', e)
except Exception as e:
    print('error connecting or reading DB', e)
    sys.exit(1)
finally:
    try:
        conn.close()
    except:
        pass
