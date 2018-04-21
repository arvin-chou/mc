# -*- coding: utf-8 -*-

"""Development settings and globals."""

from __future__ import absolute_import

from os.path import join, normpath

from settings.base import *


########## DEBUG CONFIGURATION
# Flask debug
DEBUG = False
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
DATABASES_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'mysql+pymysql',
        'NAME': '/Merchant',
        'USER': 'Merchant_user',
        'PASSWORD': "jB?Tm=AVT@]GPNrpLxW-}(8J>'Q6.[7g,}uYy6~ePxT;M7mZkQ)YhkL&Z[WGW4",
        'HOST': 'localhost',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION

########## GENERAL CONFIGURATION
INTERNAL_IP = '0.0.0.0'
########## END GENERAL CONFIGURATION

########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION
