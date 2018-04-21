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

# http://stackoverflow.com/questions/13018298/cannot-connect-to-in-memory-sqlite-db-using-sqlalchemy-with-python-2-7-3-on-wind
DATABASES = {
    "default": {
        'ENGINE': 'sqlite',
# 'NAME': '/:memory:',
        'NAME': '//tmp/qq',
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}
