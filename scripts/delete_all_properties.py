import sqlite3
import shutil
import time
from pathlib import Path

DB = Path('db.sqlite3')
if not DB.exists():
    print('Database db.sqlite3 not found.')
    raise SystemExit(1)

# Backup first
ts = time.strftime('%Y%m%d%H%M%S')
backup = DB.with_name(f'db.sqlite3.bak_{ts}')
shutil.copy2(DB, backup)
print(f'Backup created at {backup}')

conn = sqlite3.connect(str(DB))
conn.execute('PRAGMA foreign_keys = OFF')
cur = conn.cursor()

# Delete all messages and inquiries (which are tied to properties)
cur.execute("DELETE FROM properties_message")
print('Deleted all messages')

cur.execute("DELETE FROM properties_inquiry")
print('Deleted all inquiries')

# Delete all reviews
try:
    cur.execute("DELETE FROM reviews_review")
    print('Deleted all reviews')
except Exception:
    pass

# Delete all properties
cur.execute("DELETE FROM properties_property")
print('Deleted all properties')

# Clear sessions
try:
    cur.execute("DELETE FROM django_session")
    print('Cleared sessions')
except Exception:
    pass

conn.commit()
conn.close()
print('All properties and related data deleted. Admin and landlord accounts remain.')
