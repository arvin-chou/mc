# -*- coding: utf-8 -*-

import os
import sys
import os.path
import imp
import json
import uuid
import logging.config
import shutil
from optparse import OptionParser
#from utils import Api, metadata
from flask.ext.restful import Api
from flask import Flask
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy
from flask import session
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.pool import QueuePool
from passlib.context import CryptContext

__all__ = [
  'port',
  'host',
  'app',
  'api',
  'db',
  'metadata',
  'settings',
  'debug',
  'platform_model_config',
  '_logging',
# export for testing
  'init_db',
  'db',
  'pwd_context',
  'session'
  ]

#
# export for other module
#
platform_model_config = {}
metadata = MetaData()
pwd_context = CryptContext(schemes=["sha512_crypt"], 
        default="sha512_crypt", 
        sha512_crypt__default_rounds=45000)


# http://stackoverflow.com/questions/1009860/command-line-arguments-in-python
parser = OptionParser()
parser.add_option("-f", "--file", dest="settings", default="settings/local.py",
		help="configurations settings, default is settings/local.py"),
parser.add_option("-q", "--quiet",
		action="store_false", dest="verbose", default=True,
		help="don't print status messages to stdout")

(options, args) = parser.parse_args()
# for test evn
options.settings = 'settings/test.py'\
  if 'settings/test.py' == os.environ.get('EVN', None) else options.settings

# hack for wsgi, the possible format like following:
# uwsgi --pyargv "settings=settings/test.py" uwsgiconfig.ini "
if len(sys.argv) > 1 and sys.argv[0] == "uwsgi" and  sys.argv[1].startswith("settings"):
    options.settings = sys.argv[1].split("=")[1]

print ('The args is :', options)

#
# load global settings
#
mod_name,file_ext = os.path.splitext(os.path.split(options.settings)[-1])
settings = imp.load_source("base", os.path.join(os.getcwd(), 'settings/base.py'))
user_settings = imp.load_source(mod_name, os.path.join(os.getcwd(), options.settings))
for col in dir(settings):
    setattr(settings, col, getattr(user_settings, col))
    #print(col, "|>", getattr(settings, col))

#
# copy from http://flask.pocoo.org/snippets/104/
# Configure SECRET_KEY from a file in the instance directory
#
def install_secret_key(app, filename='secret_key'):
    """Configure the SECRET_KEY from a file
    in the instance directory.

    If the file does not exist, print instructions
    to create it from a shell with a random key,
    then exit.

    """
    SECRET_KEY = None

    print ('We re-create secret key with:')
    with open(filename, 'w') as f:
      SECRET_KEY = "%s%s%s" % (uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex)
      f.write(SECRET_KEY)

    app.config['SECRET_KEY'] = SECRET_KEY


def install_secret_salt(app, salt_file='salt_key'):
    """We force that re-generate every server restart"""
    SECURITY_PASSWORD_SALT = None
    with open(salt_file, 'w') as f:
        SECURITY_PASSWORD_SALT = "%s%s%s" % (uuid.uuid4().hex, uuid.uuid4().hex, uuid.uuid4().hex)
        f.write(SECURITY_PASSWORD_SALT)

    app.config['SECURITY_PASSWORD_SALT'] = SECURITY_PASSWORD_SALT


def get_pwd_context():
    print("2. pwd_context", pwd_context)
    return pwd_context

#
# copy from http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python
#
logging.config.dictConfig(settings.LOGGING)

_logging = logging
logger = _logging.getLogger(__name__)
debug = settings.DEBUG
port = int(settings.INTERNAL_PORT)
host = settings.INTERNAL_IP
app = Flask(__name__, static_folder=settings.STATIC_ROOT)
logger.warning("Flask static folder set to {0}".format(settings.STATIC_ROOT))
api = restful.Api(app)

#'postgresql+psycopg2://zeta_ci:zeta_ci@127.0.0.1/zeta_ci'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    ''.join([
        '://'.join([settings.DATABASES['default']['ENGINE'],
          ('@'.join([
              (':'.join([
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']
                ]) ),
              (''.join([
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['PORT']
                ]))
              ]) if settings.DATABASES['default']['USER'] else ''),
          ]),
          settings.DATABASES['default']['NAME'],
          settings.DATABASES['default']['CHARSET']
    ])

print('SQLALCHEMY_DATABASE_URI=', app.config['SQLALCHEMY_DATABASE_URI'])

app.config['CSRF_ENABLED'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'

#
# global setting
#
logger.warning('PLEASE EXTRACT COMMON SETTINGS TO JSON')
salt_file = os.path.join(settings.DP_ROOT, 'salt.key')
platforms_folder = os.path.join(settings.DP_ROOT, 'platform')
current_platform_mode = 'current.json'


# Assuming that gevent monkey patched the builtin
# threading library, we're likely good to use
# SQLAlchemy's QueuePool, which is the default
# pool class. However, we need to make it use
# threadlocal connections
db = SQLAlchemy(app, use_native_unicode="utf8")
db.engine.pool._use_threadlocal = True
db.create_all()
db.session.commit()

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
        pool_size=20, max_overflow=0,
        poolclass=QueuePool,
        echo=settings.DATABASES_DEBUG)

def init_db():
    if "mysql" in settings.DATABASES['default']['ENGINE']:
        db.session.execute("SET FOREIGN_KEY_CHECKS = 0")

    metadata.create_all(engine, checkfirst=True)

    if "mysql" in settings.DATABASES['default']['ENGINE']:
        engine.execute("SET FOREIGN_KEY_CHECKS = 1")

    from module.user.users import Users

    # FIXME: plz use normal register flow
    # create mock data for login

    engine.execute(SchemaAdminGroup.update(),
            {'name': 'group1', 'permission': '110000111110001', 'user_id': 1})

def drop_db():
    metadata.drop_all(engine, checkfirst=False)

def init_platform_model():
    logger.debug('load platforms/models from path: %s', platforms_folder)

    # we get who am i from zeromq or file
    logger.warning('WE CURRENTLY USE DEFAULT PLATFORMS/MODELS')
    path = os.path.join(platforms_folder, current_platform_mode)
    try:
        # 1. we check currently json exist and correct format
        if os.path.exists(path):
            with open(path, 'rt') as f:
                global platform_model_config # Needed to modify global
                platform_model_config = json.load(f)
                logger.warning('we use {0}/{1}'.format(
                        platform_model_config['feature']['platform'],
                        platform_model_config['feature']['model']))
        else:
            # 2. if notthing, we consider that it is first boot.
            logger.warning('first init. we load DEFAULT_PLATFORM_MODE {0}'.format(
                    settings.DEFAULT_PLATFORM_MODE))
            raise IOError

    except Exception as error:
        logger.error('error!!!, {0} \nwe load DEFAULT_PLATFORM_MODE {1}'.format(
                error,
                settings.DEFAULT_PLATFORM_MODE))

        path = os.path.join(platforms_folder, settings.DEFAULT_PLATFORM_MODE)

        # it MUST be succsess
        with open(path, 'rt') as f:
#global platform_model_config # Needed to modify global
            platform_model_config = json.load(f)
            logger.warning('we use {0}/{1}'.format(
                    platform_model_config['feature']['platform'],
                    platform_model_config['feature']['model']))

            current_platform_mode_path = \
                    os.path.join(platforms_folder, current_platform_mode)

            logger.warning('we copy from {0} to {1}'.format(path, current_platform_mode_path))
            shutil.copyfile(path, current_platform_mode_path)

    logger.debug('platform_model_config: %s', platform_model_config)

#
# modules import
#
from module.user.sql import \
        SchemaUsers, SchemaOnline, SchemaAdminGroup
##from module.policy.sql import SchemaPoliciesSecurity,\
##       SchemaPoliciesSecurityIpAddrs, SchemaPoliciesSecurityIpGroups
#from schema.usersmadmingroup import SchemaUsersMAdminGroup
from module.customer.sql import \
        SchemaCustomerBusinesses, \
        SchemaCustomerBusinessgrps, \
        SchemaCustomerBusinessDetails, \
        SchemaCustomerBusinessPics, \
        SchemaCustomerBusinessDetailsComments, \
        SchemaCustomerBusinessRates, \
        SchemaCustomerBusinessFavorite, \
        SchemaCustomerBusinessDeals, \
        SchemaCustomerBusinessComments, \
        SchemaCustomerBusinessDetailsComments
from module.customer.sql import SchemaCustomerBusinessesBusinessgrps
from module.pushno.sql import SchemaPushno

# end modules import



