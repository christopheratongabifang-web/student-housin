"""
Cleanup script: keep only users with role ADMIN or LANDLORD and properties listed by ADMIN.
This will:
 - backup db.sqlite3 -> db.sqlite3.bak.TIMESTAMP
 - delete messages, inquiries, reviews, properties not owned by ADMIN
 - delete users with role STUDENT

Run from project root: python scripts/cleanup_keep_admin_landlords.py
"""
import shutil
import sqlite3
import time
from pathlib import Path

DB = Path('db.sqlite3')
if not DB.exists():
    print('Database db.sqlite3 not found in current directory.')
    raise SystemExit(1)

bak = DB.with_suffix('.sqlite3.bak')
ts = time.strftime('%Y%m%d%H%M%S')
backup = DB.with_name(f'db.sqlite3.bak_{ts}')
shutil.copy2(DB, backup)
print('Backup created at', backup)

conn = sqlite3.connect(str(DB))
# Disable FK enforcement for cleanup to avoid constraint errors; backup was created.
conn.execute('PRAGMA foreign_keys = OFF')
cur = conn.cursor()

# 1) Delete messages for inquiries that belong to properties not owned by ADMIN
cur.execute("DELETE FROM properties_message WHERE inquiry_id IN (SELECT pi.id FROM properties_inquiry pi JOIN properties_property pp ON pi.property_id = pp.id JOIN accounts_user au ON pp.landlord_id = au.id WHERE au.role != 'ADMIN')")
print('Deleted messages for inquiries on non-admin properties')

# 2) Delete inquiries on properties not owned by ADMIN
cur.execute("DELETE FROM properties_inquiry WHERE property_id IN (SELECT pp.id FROM properties_property pp JOIN accounts_user au ON pp.landlord_id = au.id WHERE au.role != 'ADMIN')")
print('Deleted inquiries for non-admin properties')

# 3) Delete reviews for properties not owned by ADMIN (if reviews table exists)
try:
    cur.execute("DELETE FROM reviews_review WHERE property_id IN (SELECT pp.id FROM properties_property pp JOIN accounts_user au ON pp.landlord_id = au.id WHERE au.role != 'ADMIN')")
    print('Deleted reviews for non-admin properties')
except Exception:
    pass

# 4) Delete properties where landlord is not ADMIN
cur.execute("DELETE FROM properties_property WHERE landlord_id IN (SELECT id FROM accounts_user WHERE role != 'ADMIN')")
print('Deleted properties not owned by ADMIN')

# 5) Delete inquiries and messages created by students (in case any remain)
cur.execute("DELETE FROM properties_message WHERE sender_id IN (SELECT id FROM accounts_user WHERE role = 'STUDENT')")
cur.execute("DELETE FROM properties_inquiry WHERE student_id IN (SELECT id FROM accounts_user WHERE role = 'STUDENT')")
print('Deleted messages and inquiries created by students')

# 6) Delete student users
cur.execute("DELETE FROM accounts_user WHERE role = 'STUDENT'")
print('Deleted student user accounts')

# 7) Optionally clean sessions
try:
    cur.execute("DELETE FROM django_session")
    print('Cleared django_session table')
except Exception:
    pass

conn.commit()
try:
    # Re-enable foreign keys
    conn.execute('PRAGMA foreign_keys = ON')
except Exception:
    pass
conn.close()
print('Cleanup complete. Login as admin to verify remaining data.')
