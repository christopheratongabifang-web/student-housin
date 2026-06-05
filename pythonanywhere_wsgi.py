"""
PythonAnywhere WSGI configuration for Student Housing Finder.

INSTRUCTIONS:
1. On PythonAnywhere, go to Web tab → click the WSGI file link
2. Delete all existing content and paste THIS entire file
3. Replace 'Afanwi' with your actual PythonAnywhere username
4. Replace the SECRET_KEY value with a strong random key
5. Click Save, then Reload
"""

import os
import sys

# ── Path configuration ──────────────────────────────────────────────────────
# Replace 'Afanwi' with your PythonAnywhere username
USERNAME = 'Afanwi'
PROJECT_FOLDER = f'/home/{USERNAME}/student-housing'

if PROJECT_FOLDER not in sys.path:
    sys.path.insert(0, PROJECT_FOLDER)

# ── Environment variables ───────────────────────────────────────────────────
# Replace the SECRET_KEY with your own — generate one at https://djecrety.ir
os.environ['DJANGO_SETTINGS_MODULE'] = 'housing_project.settings'
os.environ['DJANGO_SECRET_KEY'] = 'replace-this-with-your-real-secret-key-at-least-50-chars'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = f'{USERNAME}.pythonanywhere.com'

# ── Optional: Email (uncomment and fill in if you want password reset emails)
# os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
# os.environ['EMAIL_HOST_USER'] = 'your-email@gmail.com'
# os.environ['EMAIL_HOST_PASSWORD'] = 'your-app-password'
# os.environ['DEFAULT_FROM_EMAIL'] = 'your-email@gmail.com'

# ── WSGI application ────────────────────────────────────────────────────────
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
