# -*- coding: utf-8 -*-

"""Common settings and globals."""


from os.path import abspath, basename, dirname, join, normpath
from sys import path

########## DEBUG CONFIGURATION
# Flask debug
DEBUG = False
########## END DEBUG CONFIGURATION

########## PATH CONFIGURATION
# Absolute filesystem path to the NGIPS-DP project directory:
DP_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DP_ROOT)

# Site name:
SITE_NAME = basename(DP_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DP_ROOT)
########## END PATH CONFIGURATION

########## MANAGER CONFIGURATION
ADMINS = (
    ('admin', 'trendmicro'),
)

MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## DATABASE CONFIGURATION
DATABASES_DEBUG = False

DATABASES = {
    'default': {
        #'SQLALCHEMY_DATABASE_URI': 'postgresql+psycopg2://zeta_ci:zeta_ci@127.0.0.1/zeta_ci'
        'ENGINE': 'postgresql+psycopg2',
        'NAME': 'zeta_ci',
        'USER': 'zeta_ci',
        'PASSWORD': 'zeta_ci',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION


########## GENERAL CONFIGURATION
TIME_ZONE = 'America/Los_Angeles'

LANGUAGE_CODE = 'en-us'

INTERNAL_IP = '127.0.0.1'
INTERNAL_PORT = 5000

########## END GENERAL CONFIGURATION

########## PORTING CONFIGURATION
DEFAULT_PLATFORM_MODE = 'ZT-200.FW-7573A.json'
########## END PORTING CONFIGURATION


########## STATIC FILE CONFIGURATION
#STATIC_ROOT = normpath(join(SITE_ROOT, 'zetatauri-web/www/'))
STATIC_ROOT = join(DP_ROOT, 'www')
########## END STATIC FILE CONFIGURATION


########## SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []
########## END SITE CONFIGURATION


########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "info.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },

        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": "errors.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },

    "loggers": {
        "my_module": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": "no"
        },
        "sqlalchemy.engine": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": "no"
        }
    },

    "root": {
        "level": "DEBUG",
        "handlers": ["console", "info_file_handler", "error_file_handler"]
    }
}
########## END LOGGING CONFIGURATION
