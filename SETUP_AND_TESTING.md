# Quick Setup and Testing Guide

## Apply Database Migrations

Run these commands to apply the new database changes:

```bash
cd "c:\Users\Ultra Tech\Desktop\student housin"

# Apply migrations
python manage.py migrate

# Create superuser if needed (for admin access)
python manage.py createsuperuser
```

## Database Changes

The following changes are applied:
1. **New field**: `phone_number` on User model
2. **New model**: `SystemLog` with audit trail tracking
3. **Indexes**: Optimized indexes for log queries

## Test the System

### 1. Run Development Server
```bash
python manage.py runserver
```

### 2. Test Phone Number Registration
- Go to: http://localhost:8000/signup/
- Try registration with phone number: `+1234567890`
- Invalid attempts will be rejected

### 3. Access Admin Panel
- Go to: http://localhost:8000/admin/
- Login with superuser credentials
- Navigate to: Accounts → System logs
- You should see registration and login events

### 4. Test Forgot Password
- Go to: http://localhost:8000/forgot-password/
- Enter an email address
- Check console output for password reset email (development mode)

### 5. View Log Files
```bash
# Check audit logs
tail logs/audit.log

# Check security logs  
tail logs/security.log

# Check error logs
tail logs/errors.log
```

## Log Entry Examples

### Successful Registration
```
[2026-06-05 14:30:45] INFO accounts.logging_utils User Registration [john_doe] User 'john_doe' registered successfully with email john@example.com
```

### Successful Login
```
[2026-06-05 14:31:12] INFO accounts.logging_utils Login Successful [john_doe] User 'john_doe' logged in successfully
```

### Failed Login Attempt
```
[2026-06-05 14:32:00] WARNING accounts.logging_utils Login Failed Failed login attempt for username 'admin'
```

### Property Creation
```
[2026-06-05 14:35:22] INFO accounts.logging_utils Property Created [admin] Property 'Downtown Studio Apt' created - Price: 200frs
```

### Landlord Deletion
```
[2026-06-05 14:40:15] WARNING accounts.logging_utils Landlord Deleted [admin] Landlord 'landlord_user' and their 5 properties deleted
```

## Security Features Summary

### Phone Number Validation
- Regex: `^[+]?[0-9]{7,20}$`
- Prevents SQL injection and XSS through strict validation
- Format: +1234567890 or 1234567890

### Password Reset Security
- Token-based reset (not email-based links without verification)
- Secure token generation using Django's `default_token_generator`
- 24-hour token expiration
- Email verification flow

### Logging Security
- Automatic IP address capture
- User agent tracking
- Timestamp for all events
- Dual persistence (file + database)

### OWASP Top 10 Protection
1. ✅ Injection Prevention - Strict input validation, ORM parameterization
2. ✅ Authentication - 2FA, password reset, login logging
3. ✅ Sensitive Data - No plaintext passwords, token-based reset
4. ✅ XML/XXE - Not applicable
5. ✅ Broken Access Control - Role-based checks, object permissions
6. ✅ Security Misconfiguration - Hardened defaults, security headers
7. ✅ XSS Prevention - Input validation, auto-escaping templates
8. ✅ Insecure Deserialization - Not applicable
9. ✅ Using Components with Known Vulnerabilities - Current dependencies
10. ✅ Insufficient Logging - Comprehensive logging system

## Environment Variables (Production)

Create a `.env` file for production deployment:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

## Performance Notes

### Log Retention
- File logs rotate at 10MB each
- Database logs can grow indefinitely - recommend archival policy
- Consider cleaning old logs: `SystemLog.objects.filter(timestamp__lt=timezone.now() - timedelta(days=90)).delete()`

### Database Queries
- SystemLog queries use optimized indexes
- Admin list view is paginated (100 entries per page)
- Use filters and search for faster lookups

## Troubleshooting

### "SystemLog relation does not exist"
- Run `python manage.py migrate`
- Ensure migration 0002 was applied

### Phone number field empty on old users
- Existing users will have NULL phone numbers
- They can add later via profile update (if implemented)

### No emails being sent
- Development: Check console output (console backend)
- Production: Verify SMTP credentials and firewall
- Check `logs/errors.log` for email errors

### Logs directory permission error
- Ensure `logs/` directory exists and is writable
- Run: `mkdir logs` (if missing)
- Windows: Right-click → Properties → Security → Full Control for your user

## Support

For more details on:
- **Logging System**: See `LOGGING_AND_SECURITY.md`
- **Admin Usage**: See Django admin documentation
- **Security Best Practices**: See LOGGING_AND_SECURITY.md section 6
