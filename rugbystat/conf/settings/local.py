from .common import *

DEBUG = True
SECRET_KEY = 'Not a secret'
ALLOWED_HOSTS = ["*"]

for config in TEMPLATES:
    config['OPTIONS']['debug'] = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rugbystat$staging_db',
        'USER': 'root',
        'PASSWORD': '123',
        'HOST': 'localhost',
    }
}

# Testing
INSTALLED_APPS += ('django_nose',)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    BASE_DIR,
    '-s',
    '--nologcapture',
    '--with-coverage',
    '--with-progressive',
    '--cover-package={}'.format(BASE_DIR)
]

# Mail
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Vesitle Image Field settings
VERSATILEIMAGEFIELD_SETTINGS['create_images_on_demand'] = True

# Django RQ local settings
BROKER_URL = 'redis://localhost:6379'
RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDISTOGO_URL', BROKER_URL),
        'DB': 0,
        'DEFAULT_TIMEOUT': 500,
    },
}

INSTALLED_APPS += ('storages',)

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
