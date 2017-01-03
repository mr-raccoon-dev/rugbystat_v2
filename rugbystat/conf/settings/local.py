from .common import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
SECRET_KEY = 'Not a secret'
ALLOWED_HOSTS = ["*"]

for config in TEMPLATES:
    config['OPTIONS']['debug'] = DEBUG

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
DEFAULT_FILE_STORAGE = 'storages.backends.dropbox.DropBoxStorage'
DROPBOX_OAUTH2_TOKEN = DROPBOX_ACCESS_TOKEN
