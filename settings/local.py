# -*- coding: utf-8 -*-

"""Development settings and globals."""

from __future__ import absolute_import

from os.path import join, normpath

from settings.base import *


########## DEBUG CONFIGURATION
# Flask debug
DEBUG = True
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
DATABASES_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'sqlite',
        'NAME': '//tmp/test.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'CHARSET': '',
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
