from .base import *

# Local development settings

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Use local database
DATABASES['default']['NAME'] = env('DB_NAME', default='fastprint_local')

# Development-specific settings
INTERNAL_IPS = [
    '127.0.0.1',
]
