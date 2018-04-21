# -*- coding: utf-8 -*-

import os
import imp

settings = os.environ.get('EVN', 'settings/test.py')
mod_name,file_ext = os.path.splitext(os.path.split(settings)[-1])
settings = imp.load_source(mod_name, os.path.join(os.getcwd(), settings))
# FIXME: 
# 1. please use :memory: to test.
# 2. remove file after tested if we only use file-based tested.
#
# http://stackoverflow.com/questions/15681387/sqlite-works-with-file-dies-with-memory
#try:
#  # remove old db and create new for test
#  os.remove(settings.DATABASES['default']['NAME'])
#except Exception as error:
#  print('maybe no file, error=', error)

from config.config import db, settings

# for go through every api.add_resourc
from run import app, host, port
test_app = app.test_client()
base_url = 'http://%s:%s' % (host, port)


def teardown():
    db.session.remove()
