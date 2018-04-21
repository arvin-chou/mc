# -*- coding: utf-8 -*-

import os
import urllib
import json

from flask import Flask, request, Response, jsonify, g, session, redirect

"""
copy from https://gist.github.com/988363.git
"""
from functools import wraps
#import config.config
from config.config import _logging, api, app, db, settings
from module.login.oauth2_google import OAuthSignIn
from utils import reqparse, Resource, fields, marshal, inputs, abort
from utils.error import ErrorCode, omitError
from module.common import field_inputs_wrap_head
from module.user.users import Users
from module.user.users_valid import field_inputs, resource_fields, resource_fields_wrap,\
        resource_fields_post, field_inputs_wrap
from module.user.__init__ import \
        __user_users_head__ as __head__

logger = _logging.getLogger(__name__)

def signin(user):
    g.user = user
    _resource_fields = {}
    _resource_fields_wrap = resource_fields_wrap.copy()
    for col in resource_fields_wrap:
        if col not in ['type', 'subtype']:
            _resource_fields_wrap.pop(col, None) 

    _resource_fields_wrap[field_inputs_wrap_head] = fields.Nested(resource_fields)

    args = {}
    args[field_inputs_wrap_head] = dict((col, getattr(user, col)) for col in user.__table__.columns.keys())
    token = user.generate_auth_token()
    args[field_inputs_wrap_head]['access_token'] = token.decode('ascii')
    args[field_inputs_wrap_head]['clientIp'] = request.environ['REMOTE_ADDR']

    logger.debug("args[field_inputs_wrap_head]: %s", args[field_inputs_wrap_head])
    args['type'] = "admin"
    args['subtype'] = "login"

    return args, _resource_fields_wrap


class AdminLogin(Resource):
    """validate login user, routing from /rest/admin/login
    """
    """login for local user

        @api {post} /rest/admin/login login for get authentication token with local account
        @apiVersion 0.0.5
        @apiName LoginToGetAuthWithLocal
        @apiGroup account

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo validation<br />
        todo error / success return code in api

        @apiHeader {String} Authentication Authentication secret key
        @apiHeader {String} login email for user login account 
        @apiHeader {String} passHash password with sha1 encode

        @apiExample {curl} Example usage:
        curl -i -X POST -H 'Authentication:SAGITTARIUS' -H 'login:testlogin@gmail.com' -H 'passHash:c4f9375f9834b4e7f0a528cc65c055702bf5f24a' -H 'mTag: xx' http://localhost/rest/admin/login
        """
    def post(self):
        logger.debug('request.header: \n%s', request.headers)

        login = request.headers.get('login')
        passHash = request.headers.get('passHash')
        Authentication = request.headers.get('Authentication')

        if not login or not passHash or not Authentication:
            return omitError(ErrorMsg=\
                    'Not Found: login(%s)/passHash(%s)/Authentication(%s)' %
                        ( login, passHash, Authentication)
                    ), 400
        elif ('SAGITTARIUS' not in Authentication):
            return omitError(ErrorMsg='SAGITTARIUS not in Authentication header(%s)'\
                    % Authentication), 400

        user = Users.get_by_loginpass(login, passHash)

        if not user:
            logger.debug("user %s not found with password %s", login, passHash)
            #return omitError(ErrorMsg='not Authentication ), 401
            abort(401)
        #elif not Users.sign(user.id, login, passHash):
        #    logger.debug("Users.sign fail")
        #    return omitError(ErrorMsg='not Authentication ), 401
        else:
            if user.passHash == "": # no passHash, not use email to login
                logger.debug("user %s not found with password %s, use non email login", login, passHash)
                abort(401)
            self.args, _resource_fields_wrap = signin(user)
#            g.user = user
#            _resource_fields = {}
#            _resource_fields_wrap = resource_fields_wrap.copy()
#            for col in resource_fields_wrap:
#                if col not in ['type', 'subtype']:
#                    _resource_fields_wrap.pop(col, None) 
#
#            _resource_fields_wrap[field_inputs_wrap_head] = fields.Nested(resource_fields)
#
#            self.args = {}
#            self.args[field_inputs_wrap_head] = dict((col, getattr(user, col)) for col in user.__table__.columns.keys())
#            #self.args[field_inputs_wrap_head]['sid'] = session['sid']
#            token = user.generate_auth_token()
#            self.args[field_inputs_wrap_head]['access_token'] = token.decode('ascii')
#            self.args[field_inputs_wrap_head]['clientIp'] = request.environ['REMOTE_ADDR']
#
#            logger.debug("self.args[field_inputs_wrap_head]: %s", self.args[field_inputs_wrap_head])
#            self.args['type'] = "admin"
#            self.args['subtype'] = "login"
            return marshal(self.args, _resource_fields_wrap), 200

    """regist google/fb user

        @api {get} /rest/admin/login login for get authentication token with local account
        @apiVersion 0.0.5
        @apiName LoginToGetAuthWithGooOrFB
        @apiGroup account

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo validation<br />
        todo error / success return code in api

        @apiParam {String{..6}="google", "fb"} q for request type from facebook or google
        @apiParam {String{..254}} code parameter for oauth 2.0
        @apiParam {String{..254}} access_token parameter for oauth 2.0

        @apiExample {curl} Example usage:
        curl -X GET -H "mTag: xx" -H "Content-Type:application/json" http://localhost/rest/admin/login?q=google?access_token=eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ3MjM1MTY3NiwiaWF0IjoxNDcyMz%20UxMDc2fQ.eyJpZCI6MTA3fQ.cDHFCDCoB7CI-eWzsDaPlRMX0fW28LZfQeh0lUPZLH0&code=4/_KbWiqHR1chP1oMCQGfqq77MoF9WNnDkkAVcpim7he4#


        @apiSuccess {Object}          data        oauth2's body
        @apiSuccess {Number}          data.id  user id
        @apiSuccess {String{..254}}   data.email  user's email
        @apiSuccess {String{..254}}   data.login  user's login name
        @apiSuccess {String{..254}}   data.name   user's display name
        @apiSuccess {String{..254}}   data.access_token   user's auth token
        @apiSuccessExample {json} Success-Response:
            HTTP/1.1 200 OK
            {  
                "data":{  
                    "id":107,
                    "email":"testlogin@gmail.com",
                    "login":"testlogin@gmail.com",
                    "name":"tester",
                    "access_token":"eyJpYXQiOjE0NzI0MjI1NzEsImFsZyI6IkhTMjU2IiwiZXhwIjoxNDcyNDIzMTcxfQ.eyJpZCI6MTA3fQ.0C38-zLfbfd3dcRTQVv39PHeRMMYpjDIpBXGi5zHcIQ",
                },
                "subtype":"login",
                "type":"admin"
            }
        """

    def get(self):
        """google / fb
        """
        # fix route hardcode
        _request = request.args.get('q', None)
        code = request.args.get('code', None)
        access_token = request.args.get('access_token', None)
        logger.debug("login code %s, q=%s access_token=%s", code, _request, access_token)
        if 1: # for debug
            if not access_token:
                return omitError('CE_UNAUTHORIZED', 'no route, permission deny'), 400

            if _request == 'google' or request.path == '/rest/admin/login/google':
                oauth = OAuthSignIn.get_provider('google')
                userinfo = oauth.get_session(access_token=access_token)
                user = Users.regist_by_google(userinfo)
                #log the user in-->
                #HERE YOU LOG THE USER IN, OR ANYTHING ELSE YOU WANT
                #THEN REDIRECT TO PROTECTED PAGE
                self.args, _resource_fields_wrap = signin(user)
                return marshal(self.args, _resource_fields_wrap), 200
            elif _request == 'facebook' or request.path == '/rest/admin/login/facebook':
                resp = urllib.request.Request(settings.FACEBOOK_OAUTH2_USERINFO_SCOPE + "&access_token={accessToken}".format(accessToken=access_token))
                    #this gets the facebook profile!!
                content = None
                try:
                    with urllib.request.urlopen(resp) as _resp:
                        content = _resp.read()
                except urllib.error.URLError as e:
                    logger.debug('path %s, %s encounter urllib.error.URLError.reason %s', resp.get_full_url(), resp, e.reason)
                    return omitError('CE_UNAUTHORIZED', ',, permission deny'), 400
                facebook_profile = json.loads(content.decode('utf-8'))
                print("facebook_profile  =", facebook_profile)

                userinfo = facebook_profile
                user = Users.regist_by_facebook(userinfo)
                #log the user in-->
                #HERE YOU LOG THE USER IN, OR ANYTHING ELSE YOU WANT
                #THEN REDIRECT TO PROTECTED PAGE
                self.args, _resource_fields_wrap = signin(user)
                return marshal(self.args, _resource_fields_wrap), 200

            return omitError('CE_UNAUTHORIZED', 'no route, permission deny'), 400


        else:
            #
            # the folloing are auto login without get access_token
            #
            if _request == 'google' or request.path == '/rest/admin/login/google':
                if code is None: # request auth
                    # TODO: use OAuthSignIn.get_provider
                    logger.debug("login with google")
                    token_request_uri = settings.GOOGLE_OAUTH2_OAUTH2_URL
                    response_type = "code"
                    client_id = settings.GOOGLE_API_CLIENT_ID
                    redirect_uri = urllib.parse.urljoin(request.url_root, '/rest/admin/login/google')
                    scope = settings.GOOGLE_API_SCOPE
        
                    url = "{token_request_uri}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}".format(
                        token_request_uri = token_request_uri,
                        response_type = response_type,
                        client_id = client_id,
                        redirect_uri = redirect_uri,
                        scope = scope)
                    return redirect(url)
                else: #validate

                    login_failed_url = '/'
                    if 'error' in request.args or 'code' not in request.args:
                        logger.debug("'error' in request.args or 'code' not in request.args")
                        return omitError('CE_UNAUTHORIZED', 'permission deny'), 400
            
                    access_token_uri = settings.GOOGLE_OAUTH2_TOKEN_URL
                    redirect_uri = urllib.parse.urljoin(request.url_root, '/rest/admin/login/google')
                    #redirect_uri = request.url_root + '/rest/admin/login?q=google'
                    params = urllib.parse.urlencode({
                        'code': code,
                        'redirect_uri':redirect_uri,
                        'client_id': settings.GOOGLE_API_CLIENT_ID,
                        'client_secret': settings.GOOGLE_API_CLIENT_SECRET,
                        'grant_type':'authorization_code'
                    })
                    print("params=", params)
                    params = params.encode('ascii') # params should be bytes
                    headers={'content-type':'application/x-www-form-urlencoded'}
                    resp = urllib.request.Request(access_token_uri, method = 'POST', data = params, headers = headers)
                    content = None
                    try:
                        with urllib.request.urlopen(resp) as _resp:
                            content = _resp.read()
                    except urllib.error.URLError as e:
                        logger.debug('%s encounter urllib.error.URLError.reason %s', resp, e.reason)
                        return omitError('CE_UNAUTHORIZED', ', permission deny'), 400
     

                    token_data = json.loads(content.decode('utf-8'))
                    print("token_data=", token_data, ", content  =", content)
                    #session['access_token'] = token_data['access_token']

                    resp = urllib.request.Request(settings.GOOGLE_OAUTH2_USERINFO + "?access_token={accessToken}".format(accessToken=token_data['access_token']))

                    try:
                        with urllib.request.urlopen(resp) as _resp:
                            content = _resp.read()
                    except urllib.error.URLError as e:
                        logger.debug('%s encounter urllib.error.URLError.reason %s', resp, e.reason)
                        return omitError('CE_UNAUTHORIZED', ',, permission deny'), 400
                    #this gets the google profile!!
                    google_profile = json.loads(content.decode('utf-8'))
                    print("google_profile  =", google_profile)

                    oauth = OAuthSignIn.get_provider('google')
                    #session['access_token'] = 'ya29.Ci8VA43OwblUKzf7diCatoDGGuOn4untNZTKJNJ4VLkcj6wbA266u-eQd6qrRx3xWQ'
                    userinfo = oauth.get_session(access_token=token_data['access_token'] )
                    user = Users.regist_by_google(userinfo)
                    #log the user in-->
                    #HERE YOU LOG THE USER IN, OR ANYTHING ELSE YOU WANT
                    #THEN REDIRECT TO PROTECTED PAGE
                    self.args, _resource_fields_wrap = signin(user)
                    return marshal(self.args, _resource_fields_wrap), 200

            elif _request == 'facebook' or request.path == '/rest/admin/login/facebook':
                if code is None: # request auth
                    # TODO: use OAuthSignIn.get_provider
                    logger.debug("login with facebook")
                    token_request_uri = settings.FACEBOOK_OAUTH2_OAUTH2_URL
                    client_id = settings.FACEBOOK_API_CLIENT_ID
                    redirect_uri = urllib.parse.urljoin(request.url_root, '/rest/admin/login/facebook')
                    scope = settings.FACEBOOK_API_SCOPE
                    response_type = "code"
        
                    url = "{token_request_uri}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}".format(
                        token_request_uri = token_request_uri,
                        response_type = response_type,
                        client_id = client_id,
                        redirect_uri = redirect_uri,
                        scope = scope)

                    print("redirect url=", url)
                    return redirect(url)
                else: #validate

                    login_failed_url = '/'
                    if 'error' in request.args or 'code' not in request.args:
                        logger.debug("'error' in request.args or 'code' not in request.args")
                        return omitError('CE_UNAUTHORIZED', 'permission deny'), 400
            
                    access_token_uri = settings.FACEBOOK_OAUTH2_TOKEN_URL
                    redirect_uri = urllib.parse.urljoin(request.url_root, '/rest/admin/login/facebook')
                    #redirect_uri = request.url_root + '/rest/admin/login?q=facebook'
                    params = urllib.parse.urlencode({
                        'code': code,
                        'redirect_uri':redirect_uri,
                        'client_id': settings.FACEBOOK_API_CLIENT_ID,
                        'client_secret': settings.FACEBOOK_API_CLIENT_SECRET,
                        'grant_type':'authorization_code'
                    })
                    print("params=", params)
                    params = params.encode('ascii') # params should be bytes
                    headers={'content-type':'application/x-www-form-urlencoded'}
                    resp = urllib.request.Request(access_token_uri, method = 'POST', data = params, headers = headers)
                    content = None
                    try:
                        with urllib.request.urlopen(resp) as _resp:
                            content = _resp.read()
                    except urllib.error.URLError as e:
                        logger.debug('%s encounter urllib.error.URLError.reason %s', resp, e.reason)
                        return omitError('CE_UNAUTHORIZED', ', permission deny'), 400
     

                    print(", content  =", content)
                    token_data = json.loads(content.decode('utf-8'))
                    print("token_data=", token_data, ", content  =", content)
                    #session['access_token'] = token_data['access_token']

                    resp = urllib.request.Request(settings.FACEBOOK_OAUTH2_USERINFO_SCOPE + "&access_token={accessToken}".format(accessToken=token_data['access_token']))
                    #this gets the facebook profile!!

                    try:
                        with urllib.request.urlopen(resp) as _resp:
                            content = _resp.read()
                    except urllib.error.URLError as e:
                        logger.debug('path %s, %s encounter urllib.error.URLError.reason %s', resp.get_full_url(), resp, e.reason)
                        return omitError('CE_UNAUTHORIZED', ',, permission deny'), 400
                    facebook_profile = json.loads(content.decode('utf-8'))
                    print("facebook_profile  =", facebook_profile)

                    #oauth = OAuthSignIn.get_provider('facebook')
                    ##session['access_token'] = 'ya29.Ci8VA43OwblUKzf7diCatoDGGuOn4untNZTKJNJ4VLkcj6wbA266u-eQd6qrRx3xWQ'
                    #userinfo = oauth.get_session(access_token=token_data['access_token'] )
                    userinfo = facebook_profile
                    user = Users.regist_by_facebook(userinfo)
                    #log the user in-->
                    #HERE YOU LOG THE USER IN, OR ANYTHING ELSE YOU WANT
                    #THEN REDIRECT TO PROTECTED PAGE
                    self.args, _resource_fields_wrap = signin(user)
                    return marshal(self.args, _resource_fields_wrap), 200

            return omitError('CE_UNAUTHORIZED', 'no route, permission deny'), 400
