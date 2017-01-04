from .common import *

try:
    # Python 2.x
    import urlparse
except ImportError:
    # Python 3.x
    from urllib import parse as urlparse


# Honor the 'X-Forwarded-Proto' header for request.is_secure()
# https://devcenter.heroku.com/articles/getting-started-with-django
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# django-secure
# http://django-secure.readthedocs.org/en/v0.1.2/settings.html
INSTALLED_APPS += (
    "djangosecure",
    "gunicorn",
)

SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = True

# Site
# https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# Template
# https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

# Media files
# http://django-storages.readthedocs.org/en/latest/index.html
INSTALLED_APPS += ('storages',)
DROPBOX_OAUTH2_TOKEN = DROPBOX_ACCESS_TOKEN

# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# AWS_ACCESS_KEY_ID = os.environ.get('DJANGO_AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('DJANGO_AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('DJANGO_AWS_STORAGE_BUCKET_NAME')
# AWS_DEFAULT_ACL = 'public-read'
# AWS_AUTO_CREATE_BUCKET = True
# AWS_QUERYSTRING_AUTH = False
# MEDIA_URL = 'https://s3.amazonaws.com/{}/'.format(AWS_STORAGE_BUCKET_NAME)
# AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()

# https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching#cache-control
# Response can be cached by browser and any intermediary caches (i.e. it is
# "public") for up to 1 day
# 86400 = (60 seconds x 60 minutes x 24 hours)
# AWS_HEADERS = {
#     'Cache-Control': 'max-age=86400, s-maxage=86400, must-revalidate',
# }

# Static files
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# Caching
REDIS_PORT = 6379
REDIS_HOST = '127.0.0.1'
REDIS_PASSWORD = 'R@DIS'
BROKER_URL = 'redis://:%s@%s:%d' % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': BROKER_URL,
        'OPTIONS': {
            'DB': 0,
            'PASSWORD': REDIS_PASSWORD,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            }
        }
    }
}

# Django RQ production settings
RQ_QUEUES = {
    'default': {
        'URL': BROKER_URL,
        'DB': 0,
        'DEFAULT_TIMEOUT': 500,
    },
}

VERSATILEIMAGEFIELD_SETTINGS['create_images_on_demand'] = False
