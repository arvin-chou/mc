# -*- coding: utf-8 -*-

'''
    Auth-SHA1/HMAC
    ~~~~~~~~~~~~~~

    Securing an Eve-powered API with Basic Authentication (RFC2617).

    Since we are using werkzeug we don't need any extra import (werkzeug being
    one of Flask/Eve prerequisites).

    This snippet by Nicola Iarocci can be used freely for anything you like.
    Consider it public domain.
'''

import os
import json
#import httplib2
#http = httplib2.Http()

from flask import url_for, redirect, request, make_response
from flask.ext.restful import abort
from flask import session

from werkzeug.security import check_password_hash
from uuid import UUID

from config.config import app, port, host, api, _logging, debug, \
       install_secret_salt, install_secret_key,\
       init_db, init_platform_model, settings
from module.pic.cdn import PicCDN
from module.user.users import Users


#
# Init
#
logger = _logging.getLogger(__name__)
logger.warning('Init...')

install_secret_salt(app)
install_secret_key(app)

init_db()
init_platform_model()


DP_ROOT = settings.DP_ROOT
STATIC_ROOT = settings.STATIC_ROOT

#from schema.users import User
#from utils import abort

#
# routing
#
from config.route import route, ConfigRoute
ConfigRoute.set_route(api)

# https://github.com/mitsuhiko/flask
def do_the_login(): pass
def valid_login(username=None, password=None): pass


@app.route(route['AdminLogout'] , methods=['POST'])
def adminlogout():
    Users.DeleteSession()
#return redirect(url_for('static', filename='zetatauri-web/www/index.html'))
    return redirect(url_for('', filename='index.html'))

@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp



# if no define, we pass here
@app.route('/<path:path>')
def static_proxy(path):
    #logger.info('your request path are: %s', os.path.join(path))
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = settings.PIC_PREFIX
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = settings.ALLOWED_EXTENSIONS

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.before_request
def check_valid_login():
    logger.debug("request.get_json(): %s", request.get_json())

    if (request.path.startswith('/img/')):
        logger.debug('pass to img module')
        return PicCDN.trans(app, request)
    elif (
        request.endpoint and
        'rest' not in request.endpoint and
        not request.path.startswith('/rest/')):
        logger.debug('pass to directly access static files')
        return None # pass to static
    #elif ((request.path == '/rest/admin/login' or 
    #     request.path == '/rest/admins') and
    #    request.method == 'POST'):
    elif (request.path.startswith('/rest/admin') and
        request.method in ['POST', 'GET']):
    #elif request.path == '/rest/admin/login':
        logger.debug('we only pass /rest/admin/login for login reqest with POST / GETmethod')
        return None 

    # if cookies alive, it will never timeout
    # session['id'] = 1 # fake
    # session['sid'] = 1 # fake
    access_token = request.headers.get('access_token')
    login_valid = False
    if access_token:
        login_valid = Users.IsSessionAlive(access_token)
    login_valid = True
    #g.user = current_user
    #print("======current_user.is_anonymous:", current_user.is_anonymous,
    #"g.user:", g.user, "g.user.is_authenticated:", g.user.is_authenticated,
    #"login_valid:", login_valid, "request.endpoint:", request.endpoint,
    #"request.cookies:", request.cookies)

    #userinfo = None
    #if access_token:
    #    userinfo = oauth.get_auth_session(access_token=access_token)
    #userinfo = oauth.callback(access_token=access_token)
    #logger.debug('access_token: %s, userinfo: %s', access_token, userinfo)
        

    if login_valid is False:
        logger.debug('not valid, plz login first')
        abort(401)
        #return omitError(ErrorMsg='not Authentication ), 401
    else:
        logger.debug('update alive timer')
        #Users.UpdateAlive()
    #elif (request.endpoint and
    #        'zetatauri-web' in request.endpoint):
    #    #print('ccc', ('zetatauri-web/www/', path))
    #    return app.send_static_file(os.path.join('zetatauri-web/www/', request.endpoint.join('/')))
        #logger.debug('your request path are: %s', os.path.join(request.path))
        logger.warning('NO CHECK FOR VALIDATE API')
        pass


# this could effect all 404
@app.errorhandler(404)
def not_found(error):
    logger.debug('redirect not_found %s', error)
    return app.send_static_file('index.html'), 404
    #return app.send_static_file('static/default/no_image.jpg'), 404

#from googleapiclient import discovery
#from oauth2client import client
#import flask
#@app.route('/')
#def index():
#    if 'credentials' not in flask.session:
#        return flask.redirect(flask.url_for('oauth2callback'))
#    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
#    if credentials.access_token_expired:
#        return flask.redirect(flask.url_for('oauth2callback'))
#    else:
#        http_auth = credentials.authorize(httplib2.Http())
#    drive_service = discovery.build('drive', 'v2', http_auth)
#    files = drive_service.files().list().execute()
#    return json.dumps(files)
#
#
#@app.route('/oauth2callback')
#def oauth2callback():
#    flow = client.flow_from_clientsecrets(
#            'client_secrets.json',
#            scope='https://www.googleapis.com/auth/drive.metadata.readonly',
#            redirect_uri=flask.url_for('oauth2callback', _external=True))
#    flow.params['include_granted_scopes'] = True
#    if 'code' not in flask.request.args:
#        auth_uri = flow.step1_get_authorize_url()
#        return flask.redirect(auth_uri)
#    else:
#        auth_code = flask.request.args.get('code')
#        credentials = flow.step2_exchange(auth_code)
#        flask.session['credentials'] = credentials.to_json()
#    return flask.redirect(flask.url_for('index'))

#from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
##from flask import Flask, request, Response, jsonify, g, session
#from flask import g
#from module.login.oauth2_google import OAuthSignIn
#from module.user.model import Users as obj
#from module.user.users import Users
#login_manager = LoginManager()
#login_manager.init_app(app)
#login_manager.login_view = 'login'
##oauth = OAuthSignIn.get_provider('google')
#@app.route('/authorize/<provider>')
#def oauth_authorize(provider):
#    # Flask-Login function
#    if not current_user.is_anonymous:
#        return redirect(url_for('index'))
#    oauth = OAuthSignIn.get_provider(provider)
#    #print("oauth.authorize()", oauth.authorize())
#    #auth_url, oauth_state = oauth.authorize()
#    #session['oauth_state'] = oauth_state
#    #print("auth_url = ", auth_url, ", state=", state)
#    #return redirect(auth_url)
#    return oauth.authorize()
#
##@login_manager.user_loader
##def get_user(ident):
##    return obj.query.get(int(ident))
#@login_manager.user_loader
#def user_loader(email):
#    logger.debug('check by login_manager.user_loader, email = %s', email)
#    if not Users.user_is_exist(email):
#        return
#
#    user = obj()
#    user.email = email
#    return user
#
#
##@login_manager.request_loader
##def request_loader(request):
##    logger.debug('check by login_manager.request_loader, email = %s', request)
##    email = request.form.get('email')
##    if not Users.user_is_exist(email):
##        return
##
##    user = obj()
##    user.email = email
##
##    # DO NOT ever store passwords in plaintext and always compare password
##    # hashes using constant-time comparison!
##    user.is_authenticated = Users._hash_password(request.form['pw']) == user.passHash
##
##    return user
#
#@app.route('/callback/<provider>')
#def oauth_callback(provider):
#    if not current_user.is_anonymous:
#        return redirect(url_for('index'))
#    #if 'error' in request.args:
#    #    if request.args.get('error') == 'access_denied':
#    #        return 'You denied access.'
#    #    return 'Error encountered.'
#    #if 'code' not in request.args and 'state' not in request.args:
#    #    return redirect(url_for('login'))
#    oauth = OAuthSignIn.get_provider(provider)
#    me = oauth.callback()
#    print("me is:", me, "oauth_state: ", session['oauth_state'])
#    username = me['name']
#    email = me['email']
#    if email is None:
#        # I need a valid email address for my user identification
#        flash('Authentication failed.')
#        return redirect(url_for('index'))
#    # Look if the user already exists
#    user = Users.user_is_exist(email)
#    if not user:
#        # Create the user. Try and use their name returned by Google,
#        # but if it is not set, split the email address at the @.
#        nickname = username
#        if nickname is None or nickname == "":
#            nickname = email.split('@')[0]
#
#        # We can do more work here to ensure a unique nickname, if you 
#        # require that.
#        user=obj()
#        user.name = nickname
#        user.login = email
#        user.email = email
#        user.avatar_url = me['picture']
#        Users.create_or_update_user(user)
#    # Log in the user, by default remembering them for their next visit
#    # unless they log out.
#    login_user(user, remember=True)
#
#    print("1. current_user.is_anonymous:", current_user.is_anonymous,
#    "g.user:", g.user, "g.user.is_authenticated:", g.user.is_authenticated)
#    return redirect(url_for('login2'))
#
#@app.route('/login2', methods=['GET', 'POST'])
#def login():
#    #oauth = OAuthSignIn.get_provider('google')
#    #userinfo = oauth.get_session(access_token=request.args['code'])
#
#    ##me = oauth.callback()
#    ##print("============me is:", me, "oauth_state: ", session['oauth_state'])
#    ##logger.debug('userinfo: %s', userinfo.json())
#    #logger.debug('userinfo: %s', userinfo)
#
#    if request.method == 'GET':
#        return '''
#               <form action='login2' method='POST'>
#                <input type='text' name='email' id='email' placeholder='email'></input>
#                <input type='password' name='pw' id='pw' placeholder='password'></input>
#                <input type='submit' name='submit'></input>
#               </form>
#               '''
#
#    from flask import Response
#    resp = Response(status=200)
#    resp.headers['login'] = request.form['email']
#    resp.headers['passHash'] = request.form['pw']
#
#    return resp
#    return redirect(request.url_root + 'rest/admin/login')
#
#
#@app.route('/protected')
#@login_required
#def protected():
#    return 'Logged in as: ' + current_user.id
#
#@app.route('/logout')
#def logout():
#    flask_login.logout_user()
#    return 'Logged out'
#
#@login_manager.unauthorized_handler
#def unauthorized_handler():
#    return 'Unauthorized'
#
#@app.route('/login3')
#def google_login():
#    token_request_uri = "https://accounts.google.com/o/oauth2/auth"
#    response_type = "code"
#    client_id = settings.GOOGLE_API_CLIENT_ID
#    redirect_uri = url_for('google_authenticate', _external=True)
#    scope = "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
#    url = "{token_request_uri}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}".format(
#        token_request_uri = token_request_uri,
#        response_type = response_type,
#        client_id = client_id,
#        redirect_uri = redirect_uri,
#        scope = scope)
#    return redirect(url)
#@app.route('/login3_auth')
#def google_authenticate():
#    #parser = Http()
#    import urllib.parse as parser
#    import urllib.request as r
#    login_failed_url = '/'
#    if 'error' in request.args or 'code' not in request.args:
#        return redirect('{loginfailed}'.format(loginfailed = login_failed_url))
#
#    access_token_uri = 'https://accounts.google.com/o/oauth2/token'
#    redirect_uri = url_for('google_authenticate', _external=True)
#    params = parser.urlencode({
#        'code': request.args['code'],
#        'redirect_uri':redirect_uri,
#        'client_id': settings.GOOGLE_API_CLIENT_ID,
#        'client_secret': settings.GOOGLE_API_CLIENT_SECRET,
#        'grant_type':'authorization_code'
#    })
#    print("params=", params)
#    params = params.encode('ascii') # params should be bytes
#    headers={'content-type':'application/x-www-form-urlencoded'}
#    resp = r.Request(access_token_uri, method = 'POST', data = params, headers = headers)
#    with r.urlopen(resp) as _resp:
#        content = _resp.read()
#    print("content  =", content)
#    token_data = json.loads(content.decode('utf-8'))
#    print("token_data=", token_data, ", content  =", content)
#    session['access_token'] = token_data['access_token']
#    session['id'] = 1 # fake
#    session['sid'] = 1 # fake
#    resp = r.Request("https://www.googleapis.com/oauth2/v1/userinfo?access_token={accessToken}".format(accessToken=token_data['access_token']))
#    #this gets the google profile!!
#    google_profile = json.loads(content.decode('utf-8'))
#    print("google_profile  =", google_profile)
#    #log the user in-->
#    #HERE YOU LOG THE USER IN, OR ANYTHING ELSE YOU WANT
#    #THEN REDIRECT TO PROTECTED PAGE
#    #return redirect('/access_token')
#    return redirect(url_for('._google_authenticate_by_token', access_token=session['access_token']))
#@app.route('/access_token')
#def google_authenticate_by_token():
#    oauth = OAuthSignIn.get_provider('google')
#    #session['access_token'] = 'ya29.Ci8VA43OwblUKzf7diCatoDGGuOn4untNZTKJNJ4VLkcj6wbA266u-eQd6qrRx3xWQ'
#    userinfo = oauth.get_session(access_token=session['access_token'] )
#    print("session['access_token'] =", session['access_token'] )
#    print("userinfo = ", userinfo)
#    return redirect('/')
#@app.route('/login4')
#def _google_authenticate_by_token():
#    oauth = OAuthSignIn.get_provider('google')
#    access_token = request.args.get('access_token', None)
#    if not access_token:
#        access_token = request.headers.get('access_token')
#    userinfo = oauth.get_session(access_token=access_token)
#    print("userinfo = ", userinfo)
#    return json.dumps(userinfo)

"""
# not monitor test* file
extra_dirs = [DP_ROOT,]
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename) and filename not in 'test':
                extra_files.append(filename)
"""
if __name__ == '__main__':
    app.run(processes=3, host=host, port=port, debug=debug, extra_files=[],\
        use_reloader=True)
