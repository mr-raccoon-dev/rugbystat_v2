import redislite

from .common import *
from .logging import *

ALLOWED_HOSTS = ['rugbystat.pythonanywhere.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR , 'rugbystat.sqlite.db'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

BROKER_URL = 'redis://redis-15544.c8.us-east-1-3.ec2.cloud.redislabs.com:15544'

RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDISTOGO_URL', BROKER_URL),
        'DB': 0,
        'DEFAULT_TIMEOUT': 500,
    },
}

CACHE_DIR = os.path.join(BASE_DIR, '.diskcache')
if not os.path.isdir(CACHE_DIR):
    try:
        os.makedirs(CACHE_DIR)  # race condition!
    except OSError:
        pass

CACHES = {
    'default': {
        'BACKEND': 'diskcache.DjangoCache',
        'LOCATION': CACHE_DIR,
        'SHARDS': 4,
        'DATABASE_TIMEOUT': 1.0,
    },
}
