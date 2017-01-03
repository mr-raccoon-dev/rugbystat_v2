import redislite

from .common import *


ALLOWED_HOSTS = ['rugbystat.pythonanywhere.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rugbystat$staging_db',
        'USER': 'rugbystat',
        'PASSWORD': '1111@staging',
        'HOST': 'rugbystat.mysql.pythonanywhere-services.com',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

RSL = redislite.Redis(os.path.join(BASE_DIR, '../redis.db'))
BROKER_URL = 'redis+socket://' + RSL.socket_file

RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDISTOGO_URL', BROKER_URL),
        'DB': 0,
        'DEFAULT_TIMEOUT': 500,
    },
}
