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

BROKER_URL = 'redis://redis-15544.c8.us-east-1-3.ec2.cloud.redislabs.com:15544'

RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDISTOGO_URL', BROKER_URL),
        'DB': 0,
        'DEFAULT_TIMEOUT': 500,
    },
}
