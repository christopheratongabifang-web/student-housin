"""Reset or create a Django admin user password.

Usage:
  python scripts/reset_admin.py --username admin --password newpass
  python scripts/reset_admin.py --username admin  # prompts for password
  python scripts/reset_admin.py --username admin --create  # create if missing

Note: Run this with your project's virtualenv activated so Django is available.
"""
import os
import sys
import argparse
import getpass
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Reset or create an admin user's password")
    parser.add_argument('--username', '-u', default='admin', help='Username to update/create')
    parser.add_argument('--password', '-p', help='New password (if omitted, will prompt)')
    parser.add_argument('--create', action='store_true', help='Create the user if it does not exist')
    args = parser.parse_args()

    # Ensure project root is on sys.path so Django settings package can be imported
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing_project.settings')
    try:
        import django
    except ModuleNotFoundError:
        print("Error: Django is not installed in the current Python environment.")
        print("Install dependencies, then re-run. Example:")
        print("  pip install -r requirements.txt")
        print("or at minimum:")
        print("  pip install Django django-otp django-two-factor-auth")
        sys.exit(2)

    try:
        django.setup()
    except Exception as e:
        print('Error: Django settings module failed to load:', e)
        print('Ensure you are running this script from the project root or that')
        print('the project package (housing_project) is importable (check PYTHONPATH).')
        sys.exit(2)

    from django.contrib.auth import get_user_model
    from django.db import transaction

    User = get_user_model()
    password = args.password
    if not password:
        password = getpass.getpass('New password: ')
        password2 = getpass.getpass('Confirm password: ')
        if password != password2:
            print('Passwords do not match')
            sys.exit(3)

    try:
        with transaction.atomic():
            user = User.objects.filter(username=args.username).first()
            if user:
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.save()
                print(f"Updated password for existing user '{args.username}'")
            else:
                if not args.create:
                    print(f"User '{args.username}' does not exist. Use --create to create it.")
                    sys.exit(4)
                user = User.objects.create_user(username=args.username, email=f"{args.username}@example.com", password=password)
                user.is_staff = True
                user.is_superuser = True
                user.role = getattr(user, 'role', 'ADMIN')
                user.save()
                print(f"Created superuser '{args.username}'")
    except Exception as e:
        print('Database error:', e)
        sys.exit(5)


if __name__ == '__main__':
    main()
