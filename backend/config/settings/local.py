"""
Local development settings using SQLite (no Supabase needed for quick testing)
Use this for initial testing before connecting to Supabase
"""

from .development import *

# Override database to use SQLite for quick local testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS - For local testing, allow all origins but disable credentials
# (CORS spec doesn't allow CORS_ALLOW_ALL_ORIGINS with credentials)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = False  # Disable credentials for local testing

# Reduce logging verbosity - disable DEBUG autoreload messages
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.utils.autoreload': {
            'handlers': ['console'],
            'level': 'INFO',  # Change from DEBUG to INFO to hide file watching messages
            'propagate': False,
        },
    },
}

print("\n" + "="*60)
print("[LOCAL MODE] Using SQLite database for quick testing")
print("="*60)
print("This mode works without Supabase.")
print("To use Supabase: set DJANGO_SETTINGS_MODULE=config.settings.development")
print("="*60 + "\n")
