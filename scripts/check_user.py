import sqlite3
conn=sqlite3.connect('db.sqlite3')
cur=conn.cursor()
cur.execute("SELECT username,is_superuser,is_staff,email,password FROM accounts_user WHERE username='admin'")
print(cur.fetchone())
conn.close()
