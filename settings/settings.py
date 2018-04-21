import os
from schema._users import users
from schema.onlineMapping import online

if os.environ.get('PORT'):
    # We're hosted on Heroku! Use the MongoHQ sandbox as our backend.
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    MONGO_USERNAME = 'admin'
    MONGO_PASSWORD = 'trendmicro'
    MONGO_DBNAME = 'zeta'
else:
    # Running on local machine. Let's just use the local mongod instance.

    # Please note that MONGO_HOST and MONGO_PORT could very well be left
    # out as they already default to a bare bones local 'mongod' instance.
    MONGO_HOST = 'localhost'
    MONGO_PORT = 27017
    MONGO_USERNAME = 'admin'
    MONGO_PASSWORD = 'trendmicro'
    MONGO_DBNAME = 'zeta'


# let's not forget the API entry point (not really needed anyway)
#SERVER_NAME = '127.0.0.1:5000'

# We enable standard client cache directives for all resources exposed by the
# API. We can always override these global settings later.
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20

# Our API will expose two resources (MongoDB collections): 'people' and
# 'works'. In order to allow for proper data validation, we define beaviour
# and structure.

blog_posts = {
    # 'title' tag used in item links.
    #'item_title': 'blog_post',

    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/nicolaiarocci/cerberus) for details.
    'schema': {
        'title': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 50,
        },

        # 'role' is a list, and can only contain values from 'allowed'.
        'text': {
            'type': 'string'
        },

        'author': {
            'type': 'objectid',
            'data_relation': {
                 'resource': 'users'
                 #'field': '_id',
                 #'embeddable': True
             }
        }
    }
}


comments = {
    # 'title' tag used in item links.
    #'item_title': 'comment',

    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/nicolaiarocci/cerberus) for details.
    'schema': {
        'text': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 140,
        },

        'author': {
            'type': 'objectid',
            'data_relation': {
                 'resource': 'users'
            }
        },

        'target_post': {
            'type': 'objectid',
            'data_relation': {
                 'resource': 'blog_posts'
            }
        }
    }
}

# The DOMAIN dict explains which resources will be available and how they will
# be accessible to the API consumer.
DOMAIN = {
    'users': users,
    'online': online
    #,
    #'blog_posts': blog_posts,
    #'comments': comments
}
DOMAIN = {}

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

