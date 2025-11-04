# Security Documentation

## Overview

Security is a top priority for the Recipe Management System. This document outlines our security measures and best practices.

## Authentication & Authorization

### User Authentication
- **Method**: Supabase Auth + JWT tokens
- **Password Requirements**:
  - Minimum 6 characters
  - Must be different from email
  - Stored securely (hashed by Supabase)

### Token Management
- **Access Token**: 60-minute lifetime
- **Refresh Token**: 7-day lifetime
- **Storage**: httpOnly cookies (frontend)
- **Transmission**: HTTPS only

### Authorization
- **Row Level Security (RLS)**: Enabled on all tables
- **User Isolation**: Users can only access their own data
- **Service Role**: Backend uses service key for admin operations

## Data Security

### Database Security
- **Encryption**: Data encrypted at rest (Supabase)
- **Connections**: SSL/TLS required
- **Backups**: Automatic encrypted backups
- **RLS Policies**: Strict access control

### File Storage
- **Upload Validation**: File type and size checks
- **Virus Scanning**: Recommended for production
- **Access Control**: Signed URLs for private files
- **Encryption**: Files encrypted at rest

### API Security
- **HTTPS**: Required in production
- **CORS**: Restricted to known origins
- **Rate Limiting**: 60 requests/minute per user
- **Input Validation**: All inputs sanitized

## Common Vulnerabilities & Protection

### SQL Injection
✅ **Protected**: Django ORM parameterized queries
- Never use raw SQL with user input
- All queries use ORM or parameterized raw SQL

### XSS (Cross-Site Scripting)
✅ **Protected**: React automatic escaping
- React escapes all rendered content
- Explicit HTML rendering avoided
- CSP headers configured

### CSRF (Cross-Site Request Forgery)
✅ **Protected**: Django CSRF middleware
- CSRF tokens on all forms
- SameSite cookie attribute
- Origin/Referer validation

### Authentication Bypass
✅ **Protected**: Multiple layers
- JWT signature verification
- Token expiration checks
- User session validation
- RLS database policies

### File Upload Attacks
✅ **Protected**: Strict validation
- File type whitelist
- Size limits enforced
- Filename sanitization
- Separate storage domain

## Environment Variables

### Never Commit
- ❌ API keys
- ❌ Database passwords
- ❌ Secret keys
- ❌ Access tokens

### Always Use
- ✅ `.env` files (gitignored)
- ✅ Environment variable managers
- ✅ Different keys per environment
- ✅ Rotate keys regularly

## Production Security Checklist

### Before Deployment

- [ ] Change DEBUG to False
- [ ] Generate new SECRET_KEY
- [ ] Update ALLOWED_HOSTS
- [ ] Configure CORS properly
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Review RLS policies
- [ ] Enable rate limiting
- [ ] Configure CSP headers
- [ ] Set up monitoring
- [ ] Enable logging
- [ ] Audit dependencies

### Django Settings

```python
# Production security settings
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')  # Strong random key
ALLOWED_HOSTS = ['your-domain.com']

# Security middleware
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

## Rate Limiting

### API Rate Limits

| Endpoint | Limit |
|----------|-------|
| Authentication | 10/minute |
| Recipe parsing | 5/minute |
| File uploads | 10/minute |
| General API | 60/minute |
| Chatbot | 20/minute |

### Groq API Limits
- Free tier: 30 requests/minute
- Daily: 14,400 requests
- Monitor usage in Groq dashboard

## Data Privacy

### User Data
- **Personal Information**: Email only (minimum)
- **Recipe Data**: User-owned, private by default
- **Chat History**: Stored securely, user-accessible
- **Deletion**: Users can delete their account and all data

### GDPR Compliance
- Right to access data
- Right to deletion
- Data export capability
- Privacy policy required

## Incident Response

### If Security Breach Detected

1. **Immediate Actions**:
   - Isolate affected systems
   - Rotate all credentials
   - Review access logs
   - Notify users if data compromised

2. **Investigation**:
   - Analyze attack vector
   - Identify affected data
   - Document timeline
   - Preserve evidence

3. **Remediation**:
   - Patch vulnerabilities
   - Update security measures
   - Monitor for further attacks
   - Communicate with stakeholders

4. **Prevention**:
   - Update security policies
   - Enhance monitoring
   - Train team
   - Regular security audits

## Security Best Practices

### For Developers

1. **Never log sensitive data**
   - No passwords in logs
   - Mask API keys
   - Sanitize user data

2. **Validate all inputs**
   - Server-side validation required
   - Client-side is convenience only
   - Use serializers/validators

3. **Use parameterized queries**
   - Always use ORM
   - Never concatenate SQL
   - Escape when necessary

4. **Keep dependencies updated**
   ```bash
   pip list --outdated
   npm outdated
   ```

5. **Review code for security**
   - Use linters (bandit, eslint)
   - Code reviews required
   - Security-focused testing

### For Users

1. **Use strong passwords**
   - Minimum 12 characters
   - Mix of letters, numbers, symbols
   - Unique per service
   - Use password manager

2. **Keep software updated**
   - Update browser regularly
   - Keep OS patched
   - Update mobile apps

3. **Be cautious with sharing**
   - Don't share account credentials
   - Review third-party access
   - Log out on shared devices

## Security Contacts

### Reporting Vulnerabilities

Please report security issues to:
- Email: security@yourproject.com
- GitHub: Private security advisory

Do NOT:
- Open public issues for security bugs
- Exploit vulnerabilities
- Share vulnerabilities publicly before fix

We will:
- Acknowledge within 48 hours
- Provide timeline for fix
- Credit you in security advisory (optional)
- Keep you updated on progress

## Compliance

### Standards
- OWASP Top 10 compliance
- SOC 2 considerations
- GDPR ready
- HIPAA not applicable

### Regular Security Tasks

**Weekly**:
- Review access logs
- Check error rates
- Monitor for anomalies

**Monthly**:
- Dependency updates
- Security patch review
- Access audit

**Quarterly**:
- Penetration testing
- Security training
- Policy review

**Annually**:
- Full security audit
- Disaster recovery test
- Compliance review
