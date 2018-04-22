# -*- coding: utf-8 -*-

"""Development settings and globals."""

from __future__ import absolute_import
from settings.base import *

########## DEBUG CONFIGURATION
# Flask debug
DEBUG = True
########## END DEBUG CONFIGURATION

########## IN-MEMORY TEST DATABASE
DATABASES_DEBUG = True

INTERNAL_IP = '0.0.0.0'
INTERNAL_PORT = 8082
# http://stackoverflow.com/questions/13018298/cannot-connect-to-in-memory-sqlite-db-using-sqlalchemy-with-python-2-7-3-on-wind
DATABASES = {
    'default': {
        'ENGINE': 'mysql+pymysql',
        'NAME': '/Merchant',
        'USER': 'Merchant_user',
        'PASSWORD': "7--.<B*n^)",
        'HOST': 'localhost',
        'PORT': '',
        'CHARSET': '?charset=utf8',
    }
}
