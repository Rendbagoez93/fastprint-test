from .base import *

# Local development settings

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# SQLite database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development-specific settings
INTERNAL_IPS = [
    '127.0.0.1',
]
