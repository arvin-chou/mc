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
        'CHARSET': '',
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
#CDN_DOMAIN = 'http://mycdnname.cloudfront.net'
#CDN_DOMAIN = 'http://tinyurl.com'
CDN_DOMAIN = ''
PIC_PREFIX = '__pic__'
REST_PIC_PREFIX = '/img'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
MAXWIDTH = 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
PIC_ALLOWED_TYPE = set(['customer'])

########## END STATIC FILE CONFIGURATION

########## STATIC FILE CONFIGURATION
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

# Google oauth2 
GOOGLE_API_CLIENT_ID = '394040761007-s21midufu2nkfnnrl8c34ve8a0d5eje8.apps.googleusercontent.com'
GOOGLE_API_CLIENT_SECRET = '8zvIDIBSElIIzvNJ_1Zu6UWe'
GOOGLE_API_SCOPE = 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'
GOOGLE_OAUTH2_URL = 'https://accounts.google.com/o/oauth2/'
GOOGLE_OAUTH2_USERINFO = 'https://www.googleapis.com/oauth2/v1/userinfo'
GOOGLE_OAUTH2_OAUTH2_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_OAUTH2_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_API_URL = 'https://www.googleapis.com/oauth2/v1/'
OAUTH_CREDENTIALS={
        'google': {
            'id': GOOGLE_API_CLIENT_ID,
            'secret': GOOGLE_API_CLIENT_SECRET
            }
        }

# Facebookoauth2 
FACEBOOK_API_CLIENT_ID = '1006979679370914'
FACEBOOK_API_CLIENT_SECRET = '628fe04576f871ebe81018cd1fd5715b'
FACEBOOK_API_SCOPE = 'email,public_profile,user_friends'
##FACEBOOK_API_SCOPE = 'ads_management'
FACEBOOK_OAUTH2_URL = 'https://accounts.google.com/o/oauth2/'
FACEBOOK_OAUTH2_USERINFO = 'https://graph.facebook.com/v2.6/me'
FACEBOOK_OAUTH2_USERINFO_SCOPE = 'https://graph.facebook.com/v2.6/me?fields=picture,email,name'
#FACEBOOK_OAUTH2_OAUTH2_URL = "https://graph.facebook.com/v2.2/oauth/authorize"
FACEBOOK_OAUTH2_OAUTH2_URL = "https://www.facebook.com/v2.6/dialog/oauth"
#FACEBOOK_OAUTH2_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'
FACEBOOK_OAUTH2_TOKEN_URL = 'https://graph.facebook.com/v2.6/oauth/access_token'

FACEBOOK_API_URL = 'https://www.googleapis.com/oauth2/v1/'

GCM_API_KEY= 'AIzaSyDThjRdly0Gk4zk36lsKyavBo-QubXaQKw'
GCM_MAX_BATCH_SEND = 1000 # the max dev. we could push notification at once
APNS_API_KEY= 'https://www.googleapis.com/oauth2/v1/'
APNS_MAX_BATCH_SEND = 500 # the max dev. we could push notification at once

