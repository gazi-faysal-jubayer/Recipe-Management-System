"""
Development settings
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Development-specific installed apps
INSTALLED_APPS += [
    'django_extensions',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'recipe_management_dev'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        # Note: Extensions like pgvector must be enabled via SQL migrations, not via OPTIONS
    }
}

# CORS - Explicit origins required when using credentials
# Cannot use CORS_ALLOW_ALL_ORIGINS with CORS_ALLOW_CREDENTIALS (violates CORS spec)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',  # Alternative port
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery - Use eager mode for development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Additional logging for development
LOGGING['loggers'] = {
    'django': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'apps': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
