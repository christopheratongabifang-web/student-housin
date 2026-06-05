# System Logging and Security Implementation

## Overview
This document describes the comprehensive logging system and security enhancements added to the Student Housing Platform.

## 1. System Logging Architecture

### Components
- **SystemLog Model** (`accounts/log_models.py`): Database model for persistent audit logging
- **Logging Utilities** (`accounts/logging_utils.py`): Helper functions for consistent logging across the application
- **Middleware** (`RequestLoggingMiddleware`): Automatic request/response logging
- **Admin Interface** (`accounts/admin.py`): Read-only interface for viewing system logs

### Features
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log categories: AUTH, USER, PROPERTY, INQUIRY, REVIEW, SECURITY, SYSTEM, LANDLORD
- Automatic capture of: IP address, user agent, user, timestamp, HTTP status code
- Rotating file handlers with 10MB max size per file
- Database persistence for advanced querying and analysis
- Both file-based and database logging for redundancy

### Log Files
Logs are stored in the `logs/` directory:
- `audit.log`: User and system actions
- `security.log`: Security-related events and access attempts
- `errors.log`: Django errors and warnings

### Usage in Code
```python
from accounts.logging_utils import log_event

log_event(
    level='INFO',
    category='PROPERTY',
    action='Property Created',
    message=f"Property '{property.title}' created",
    user=request.user,
    request=request
)
```

## 2. Phone Number Field Security

### Implementation
- Added `phone_number` field to User model with regex validation
- Validator pattern: `^[+]?[0-9]{7,20}$`
- Constraints: 7-20 digits, optional + prefix

### XSS Prevention
- Django's form `clean_phone_number()` method sanitizes input
- Phone number is validated to contain ONLY digits and optional +
- Non-conforming input is rejected at form validation layer
- Database stores sanitized, validated data
- Template rendering uses Django's auto-escaping

### OWASP Top 10 Coverage

#### A1: Injection (SQL/NoSQL)
- **Risk**: Phone number could contain SQL injection payloads
- **Fix**: 
  - Strict regex validation (digits + optional +)
  - Django ORM prevents SQL injection via parameterized queries
  - Form validation rejects any non-matching input
- **Test**: `"+1 DROP TABLE users--"` → Rejected

#### A3: XSS (Cross-Site Scripting)
- **Risk**: Phone number rendered in templates could contain JavaScript
- **Fix**:
  - Form validation limits to digits and +
  - Django templates auto-escape all output by default
  - Explicit safe filtering in templates
- **Test**: `"<script>alert('xss')</script>"` → Rejected

#### A4: CSRF (Cross-Site Request Forgery)
- **Risk**: Unauthorized state-changing requests
- **Fix**:
  - `@csrf_protect` decorator on all views handling POST
  - `{% csrf_token %}` in all forms
  - `CsrfViewMiddleware` enabled
  - Custom `CustomUserCreationForm` uses Django's CSRF protection
- **Status**: Fully protected

#### A5: Broken Access Control
- **Risk**: Users accessing unauthorized data
- **Fix**:
  - `@login_required` on all protected views
  - Role-based access checks (`request.user.role != 'ADMIN'`)
  - Object-level permissions (property landlord checks)
  - Admin-only URL patterns for landlord management
- **Status**: Fully protected

#### A6: Security Misconfiguration
- **Risk**: DEBUG=True, weak password validators
- **Fix**:
  - PASSWORD_VALIDATORS enabled (similarity, length, common passwords, numeric)
  - SECURE_BROWSER_XSS_FILTER = True
  - SECURE_CONTENT_TYPE_NOSNIFF = True
  - X_FRAME_OPTIONS = 'DENY'
  - SESSION_COOKIE_SAMESITE = 'Lax'
  - CSRF_COOKIE_SAMESITE = 'Lax'
  - Development email backend (use production SMTP in production)
- **Status**: Hardened for development; update SECRET_KEY for production

#### A7: Authentication Failures
- **Risk**: Weak password reset, account enumeration
- **Fix**:
  - Password reset uses secure token-based approach
  - Generic message for password reset attempts (no user enumeration)
  - Token expires after use
  - Secure tokens via `default_token_generator`
  - 24-hour expiration
- **Status**: Secured

#### A8: Vulnerable Components
- **Risk**: Outdated dependencies
- **Fix**:
  - Use latest Django 6.0.5
  - django-otp + django-two-factor-auth for 2FA
  - Regular security updates recommended
- **Status**: Current; monitor for updates

#### A9: Logging & Monitoring
- **Risk**: Insufficient audit trails
- **Fix**:
  - Comprehensive SystemLog model captures all important events
  - Dual logging: file + database
  - Admin interface for log inspection
  - IP address and user agent tracking
  - Automatic middleware logging of requests
- **Status**: Fully implemented

#### A10: SSRF (Server-Side Request Forgery)
- **Risk**: Not applicable to this application
- **Status**: N/A

## 3. Forgot Password Security

### Implementation
- Token-based password reset using Django's `default_token_generator`
- Secure UID encoding via `urlsafe_base64_encode`
- Email-based verification
- Generic user enumeration prevention

### Token Security
- Tokens generated per user and one-time-use
- Tokens include user PK and timestamp
- Tokens verified against Django's SECRET_KEY
- 24-hour expiration built-in
- URL-safe encoding prevents token corruption

### Email Security
- Uses Django's email framework
- Environment variables for SMTP credentials (not hardcoded)
- Template-based email generation
- Plaintext fallback for text-only clients

### Password Reset Flow
1. User enters email
2. Generic message shown (no user enumeration)
3. System generates secure token
4. Email sent with reset link
5. User clicks link with token
6. Token validated server-side
7. User enters new password
8. Password saved with PBKDF2-SHA256 hashing
9. User redirected to login

## 4. Logged Events

### Authentication Events
- `Login Successful` - User successfully logged in
- `Login Failed` - Failed login attempt (logs username)
- `User Registration` - New user account created
- `Failed Registration` - Registration validation errors

### Property Management
- `Property Created` - New property listed
- `Property Deleted` - Property removed from system
- `Property Updated` - Property details modified

### User Management
- `Landlord Deleted` - Landlord removed from system

### Request Logging
- 4xx and 5xx HTTP responses
- Admin dashboard access
- Authentication endpoints

## 5. Admin Interface

The Django admin interface includes:

### SystemLog Admin
- Read-only view of all system logs
- Filterable by level, category, timestamp
- Searchable by action, message, username, IP
- Colored badges for log levels
- Superuser-only deletion capability
- Organized by timestamp hierarchy

### Access
```
/admin/accounts/systemlog/
```

Filters available:
- By Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- By Category (AUTH, USER, PROPERTY, etc.)
- By Date
- By User

## 6. Production Recommendations

### Before Going to Production
1. **Set SECRET_KEY to a secure random value**
   - Generate: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - Store in environment variable: `DJANGO_SECRET_KEY`

2. **Set DEBUG = False**
   - Current: DEBUG = True (development only)
   - Change: `DEBUG = False` in production

3. **Configure Email Backend**
   - Current: Console email backend (for development)
   - Set environment variables:
     ```
     EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
     EMAIL_HOST=smtp.gmail.com
     EMAIL_PORT=587
     EMAIL_USE_TLS=True
     EMAIL_HOST_USER=your-email@gmail.com
     EMAIL_HOST_PASSWORD=app-password
     DEFAULT_FROM_EMAIL=noreply@studenthousing.com
     ```

4. **Enable Security Headers**
   - Set SECURE_HSTS_SECONDS = 31536000 (1 year)
   - Set SECURE_SSL_REDIRECT = True
   - Set SESSION_COOKIE_SECURE = True
   - Set CSRF_COOKIE_SECURE = True

5. **Set Up Log Rotation**
   - Logs already use RotatingFileHandler (10MB max)
   - Monitor `logs/` directory space

6. **Database Security**
   - Migrate from SQLite to PostgreSQL
   - Enable database backups
   - Use strong database passwords

7. **Regular Security Audits**
   - Review SystemLog entries regularly
   - Check logs/ directory for errors
   - Monitor admin access

## 7. Testing the Logging System

### View All Logs
```
http://localhost:8000/admin/accounts/systemlog/
```

### Test Registration Logging
1. Create new account
2. Check admin logs → Should see "User Registration" entry

### Test Login Logging
1. Attempt failed login
2. Check admin logs → Should see "Login Failed" entry
3. Successful login
4. Check admin logs → Should see "Login Successful" entry

### Test Property Creation Logging
1. Admin creates property
2. Check admin logs → Should see "Property Created" entry

### View Log Files
```bash
# Audit logs
tail logs/audit.log

# Security logs
tail logs/security.log

# Error logs
tail logs/errors.log
```

## 8. Phone Number Format Examples

### Valid Formats
- `+1234567890`
- `+234-567-8901` (hyphens optional, will be cleaned)
- `1234567890`
- `+44 7700 900000` (spaces optional, will be cleaned)

### Invalid Formats (Rejected)
- `abc123` (contains letters)
- `123` (too short, must be 7+ digits)
- `+1234567890123456789012` (too long, max 20 digits)
- `<script>alert('xss')</script>` (contains illegal characters)
- `1' OR '1'='1` (SQL injection attempt - rejected)

## 9. Database Indexes

The SystemLog model includes optimized indexes for common queries:
- `(timestamp DESC, level)` - Filter by level and time
- `(timestamp DESC, category)` - Filter by category and time
- `(user, timestamp DESC)` - User activity timeline

This ensures fast admin interface loading and log analysis.

## Summary

The Student Housing Platform now features:
✅ Comprehensive audit logging for all important events
✅ Secure phone number validation with injection prevention
✅ Forgot password with token-based reset
✅ OWASP Top 10 vulnerability protections
✅ XSS prevention through validation and escaping
✅ Admin interface for log inspection
✅ Both file and database logging
✅ Request middleware for automatic logging
✅ Security headers and configurations
