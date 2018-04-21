# -*- coding: utf-8 -*-

import os

from flask import Flask, request, Response, jsonify, g, session

"""
copy from https://gist.github.com/988363.git
"""
from functools import wraps
#import config.config
from config.config import _logging, api, app, db
from utils import reqparse, abort, Resource
from utils.error import ErrorCode, omitError
from schema.users import User
#app = config.config.app
#api = Api(app)
#logger = config.config._logging.getLogger(__name__)
logger = _logging.getLogger(__name__)
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'username' and password == 'pass'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    response = jsonify({'code': 404,'message': 'No interface defined for URL'})
    response.status_code = 404
    return response
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        print(auth, 'xxx')
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def get_auth():
    return {
            'login': request.headers.get('login'),
            'passHash': request.headers.get('passHash'),
            'Authentication': request.headers.get('Authentication')
            }


# AdminLogin
#   validate login user, routing from /rest/admin/login
class AdminLogin(Resource):
    def post(self):
        logger.debug('request.header: \n%s', request.headers)

        AuthParams = get_auth()
        user = User(AuthParams.get('login'), AuthParams.get('passHash'))

        if not AuthParams.get('login') or not AuthParams.get('passHash') or not AuthParams.get('Authentication'):
            return omitError(ErrorMsg=\
                    'Not Found: login(%s)/passHash(%s)/Authentication(%s)' %
                        (
                            AuthParams.get('login'),
                            AuthParams.get('passHash'),
                            AuthParams.get('Authentication'))
                    ), 400
        elif ('ZETA' not in AuthParams.get('Authentication') or
             'ZETA' not in AuthParams.get('Authentication') ):
            return omitError(ErrorMsg='ZETA not in Authentication header(%s)'\
                    % AuthParams.get('Authentication')), 400

        elif not user.verify_password():
            #db.session.add(user)
            #db.session.commit()
            abort(401)

        else:
            return user.GetLoginInfo(), 201


        return parser.parse_args(), 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


#http://www.vurt.ru/eng/2013/06/using-flask-and-rauth-for-github-authentication/
#github = OAuth2Service(
#    name='github',
#    base_url='https://api.github.com/',
#    access_token_url='https://github.com/login/oauth/access_token',
#    authorize_url='https://github.com/login/oauth/authorize',
#    client_id= '477151a6a9a9a25853de',
#    client_secret= '23b97cc6de3bea712fddbef70a5f5780517449e4',
#)
