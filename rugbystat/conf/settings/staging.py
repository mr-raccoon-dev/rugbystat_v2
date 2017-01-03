from .common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rugbystat$staging_db',
        'USER': 'rugbystat',
        'PASSWORD': '1111@staging',
        'HOST': 'rugbystat.mysql.pythonanywhere-services.com',
    }
}
