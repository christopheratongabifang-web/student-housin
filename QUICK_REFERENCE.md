# Quick Reference: Running the System

## 🚀 Getting Started

### 1. Apply Database Migrations
```bash
cd "c:\Users\Ultra Tech\Desktop\student housin"
python manage.py migrate
```

**What this does**:
- Creates `phone_number` field on User table
- Creates `SystemLog` table for audit tracking
- Sets up database indexes for performance

### 2. Start Development Server
```bash
python manage.py runserver
```

Server runs at: `http://localhost:8000`

---

## 📍 Key URLs

| URL | Purpose |
|-----|---------|
| `/` | Home page |
| `/signup/` | User registration (with phone field) |
| `/login/` | Login page (with forgot password link) |
| `/forgot-password/` | Forgot password request |
| `/reset/<token>/` | Password reset page |
| `/dashboard/` | User dashboard |
| `/admin/` | Django admin panel |
| `/admin/accounts/systemlog/` | **System logs viewer** ⭐ |

---

## 🔍 Viewing System Logs

### Option 1: Admin Interface (Recommended)
1. Go to: `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Click: **Accounts** → **System logs**

**Features**:
- Filter by level (INFO, WARNING, ERROR, etc.)
- Filter by category (AUTH, PROPERTY, LANDLORD, etc.)
- Search by action, message, or username
- Sort by timestamp
- Color-coded severity levels

### Option 2: Log Files
```bash
# View audit log (user actions)
type logs\audit.log

# View security log (access & events)
type logs\security.log

# View error log (django errors)
type logs\errors.log

# Stream logs in real-time (Windows)
Get-Content logs\audit.log -Wait

# Stream logs in real-time (Mac/Linux)
tail -f logs/audit.log
```

---

## 🧪 Testing Features

### Test Phone Number Field
1. Go to: `/signup/`
2. Enter phone number: `+1234567890`
3. Submit registration
4. Check admin users list - phone field visible

**Try invalid formats**:
- `abc123` → Rejected ❌
- `<script>alert('xss')</script>` → Rejected ❌
- `1' OR '1'='1` → Rejected ❌

### Test Forgot Password
1. Go to: `/forgot-password/`
2. Enter email of existing account
3. Check Django console for password reset email
4. Click reset link in email
5. Enter new password
6. Login with new password

### Test Logging
1. Create new account → Check logs for "User Registration"
2. Try failed login → Check logs for "Login Failed"
3. Successful login → Check logs for "Login Successful"
4. Create property → Check logs for "Property Created"

---

## 📋 Log Event Types

### Authentication Events
- `User Registration` - New user created
- `Failed Registration` - Validation failed
- `Login Successful` - User logged in
- `Login Failed` - Bad credentials

### Property Management
- `Property Created` - New property listed
- `Property Updated` - Property edited
- `Property Deleted` - Property removed

### Admin Operations
- `Landlord Deleted` - Landlord removed from system

### System Events
- HTTP 4xx/5xx responses
- Admin/Dashboard access

---

## 🛡️ Security Features

### Phone Number Validation
✅ Strict regex pattern: `^[+]?[0-9]{7,20}$`
- Only digits and optional + prefix
- No special characters
- Prevents SQL injection and XSS
- Optional field (not required)

### Forgot Password
✅ Secure token-based reset
- 24-hour expiration
- One-time use tokens
- User enumeration prevention
- Email verification

### Logging
✅ Comprehensive audit trail
- IP address capture
- User agent tracking
- Timestamp for all events
- Searchable database
- Role-based display

---

## 🔧 Configuration

### Email (Password Reset)
For production, set environment variables:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

Development uses console backend (emails printed to console).

### Logging
Automatic configuration in `housing_project/settings.py`:
- File rotation: 10MB per file
- Backup count: 5 previous files
- Log location: `logs/` directory
- Database: SystemLog table

---

## 📊 Log Analysis Examples

### View Recent Login Attempts
Admin interface:
1. Filter by Category: **AUTH**
2. Filter by Level: **INFO** and **WARNING**
3. Sort by Timestamp (newest first)

Command line:
```bash
grep "Login" logs/audit.log
```

### View Property Activity
Admin interface:
1. Filter by Category: **PROPERTY**
2. Search for specific property name
3. Check timestamps for activity timeline

### View User-Specific Activity
Admin interface:
1. Filter by User dropdown
2. Select specific user
3. Shows all their actions

---

## ⚠️ Common Issues

### "SystemLog table does not exist"
```bash
python manage.py migrate accounts
```

### Phone number not showing in admin
```bash
python manage.py migrate accounts
# Then reload admin page
```

### No logs being created
1. Check `logs/` directory exists
2. Check file permissions (should be writable)
3. Check `housing_project/settings.py` LOGGING config
4. Check console for errors

### Password reset emails not received
**Development**: Check Django console output (print statements)
**Production**: Check email credentials in `.env` file

---

## 📈 Performance Tips

### Log Maintenance
```bash
# Archive old logs periodically
# Windows: Move logs older than 30 days to archive folder

# Database: Archive/delete old SystemLog entries
# SELECT COUNT(*) FROM accounts_systemlog WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
# DELETE FROM accounts_systemlog WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

### Optimize Log Queries
Admin filters are indexed:
- By timestamp (fastest)
- By level (fast)
- By category (fast)
- By user (fast)
- Full text search (slower)

---

## 🎯 Quick Checklist

- [ ] Run `python manage.py migrate`
- [ ] Start server `python manage.py runserver`
- [ ] Test registration at `/signup/` with phone number
- [ ] Test forgot password at `/forgot-password/`
- [ ] Check logs at `/admin/accounts/systemlog/`
- [ ] View log files in `logs/` directory
- [ ] Verify phone field in admin user list
- [ ] Test invalid phone formats (should reject)

---

## 📚 Documentation

For detailed information, see:
- **IMPLEMENTATION_SUMMARY.md** - Full feature list and OWASP analysis
- **LOGGING_AND_SECURITY.md** - Detailed security documentation
- **SETUP_AND_TESTING.md** - Complete setup and testing guide

---

## 💬 Examples

### Log Entry in Admin
```
2026-06-05 14:30:45 | INFO | USER | User Registration
User 'john_doe' registered successfully with email john@example.com
IP: 127.0.0.1
```

### Log Entry in File
```
[2026-06-05 14:30:45] INFO accounts.logging_utils User Registration [john_doe] User 'john_doe' registered successfully with email john@example.com
```

### Phone Number Format
```
✅ Valid:   +1234567890
✅ Valid:   1234567890
✅ Valid:   +1 (234) 567-8901 (spaces/hyphens removed automatically)
❌ Invalid: abc123
❌ Invalid: <script>alert('xss')</script>
❌ Invalid: 123 (too short)
```

---

**Last Updated**: 2026-06-05  
**Quick Start Time**: ~2 minutes
