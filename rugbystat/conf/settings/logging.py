import os
from .common import BASE_DIR

__author__ = 'krnr'


LOG_FILE_PATH = os.path.join(BASE_DIR, "django.log")
open(LOG_FILE_PATH, 'a').close()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(asctime)s %(levelname)-8s] %(message)s',
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        "applogfile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE_PATH,
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 5,
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        # 'django': {
        #     'handlers': ['console'],
        #     'propagate': True,
        # },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['applogfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rugbystat': {
            'handlers': ['applogfile', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
