import sqlite3
conn=sqlite3.connect('db.sqlite3')
cur=conn.cursor()
cur.execute("SELECT username, role, is_superuser, is_staff FROM accounts_user")
rows=cur.fetchall()
for r in rows:
    print(r)
conn.close()
