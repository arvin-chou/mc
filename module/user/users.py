# -*- coding: utf-8 -*-

#class User(db.Model):
#    #__user_users_tablename__ = 'users'
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(32), index=True)
#    password_hash = db.Column(db.String(64))
#    def hash_password(self, password):
#        self.password_hash = pwd_context.encrypt(password)
#    def sign(self, password):
#        return pwd_context.verify(password, self.password_hash)
#    def generate_auth_token(self, expiration=600):
#        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
#        return s.dumps({'id': self.id})
#    @staticmethod
#    def verify_auth_token(token):
#        s = Serializer(app.config['SECRET_KEY'])
#        try:
#            data = s.loads(token)
#        except SignatureExpired:
#            return None # valid token, but expired
#        except BadSignature:
#            return None # invalid token
#
#        user = User.query.get(data['id'])
#        return user

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm.collections import mapped_collection
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from config.config import db, _logging, metadata, pwd_context, app
from flask import g, request, jsonify
from flask import session
from hashlib import sha1

import json
from .model import Users as obj, Online
from module.login.oauth2_google import OAuthSignIn

logger = _logging.getLogger(__name__)


class Users():
    """registered user information
    """
    def GetLoginInfo(self):
        return {
                'admin': {
                        'id':  self.user.id,
                        'name':  self.user.name,
                        'login':  self.user.login,
                        'email':  self.user.email,
                        'sid': session['sid'],
                        #'passHash':  self.user.passHash,
                        'preferences':  self.user.preferences,
                        'clientIp': request.remote_addr,
                        'admingroup': admingroupStr
                }
            }


    @staticmethod
    def _hash_password(password):
        return pwd_context.encrypt(password)

    def hash_password(self, password):
        self.password_hash = Users._hash_password(password)

    @staticmethod
    def DeleteSession(r=None):
        if r is None:
            r = Online.query.filter_by(
                    user_id == session['id'],
                    #sid == session['sid'],
                    latest + 6 <= datetime.utcnow()).first()

        if (r is not None):
            logger.info('session timeout, your latest are %s', r.latest)
            db.session.delete(r)
            session.clear()

    @staticmethod
    def IsSessionAlive(login_or_token, passHash=None):
        # local
        user = obj.verify_auth_token(login_or_token)
        if not user:
        # try to authenticate with username/password
            user = Users.get_by_loginpass(login_or_token, passHash)
            logger.debug('loggin with local')
            if not user:
                return False
                #logger.debug('loggin with google')
                #oauth = OAuthSignIn.get_provider('google')
                #user = oauth.get_session(access_token=login_or_token)
                #logger.debug("user = ", user)
                #if user['email'] is None:
                #    return False

                #user = self.regist_by_google(user):

        # TODO: fb / google
        # else:
        g.user = user
        return True

        #if not session:
        #    logger.debug('no session dict')
        #    return False

        #login_valid = 'sid' in session # or whatever you use to check valid login
        #if login_valid is None:
        #    logger.debug('no session["sid"]')
        #    return False
        #else:
        #    #r = db.session.query(Online).one()
        #    # this could raise keynotfound error when we use Online.query.filter()
        #    # i guess that it result from lazy search in sqlalchemy
        #    #r = Online.query.filter_by(
        #    #        id == session['id'],
        #    #        sid == session['sid'],
        #    #        latest + 6 <= datetime.utcnow()).first()
        #    #r = db.session.query(Online).filter(
        #    #        Online.user_id == session['id'],
        #    #        Online.sid == session['sid'],
        #    #        Online.latest + 600 <= datetime.utcnow()).one()
        #    current_time = datetime.utcnow()
        #    ten_min_ago = current_time - timedelta(seconds=600)
        #    logger.debug('check timeout before 600s')

        #    r = Online.query.filter(
        #            Online.user_id == session['id'],
        #            Online.sid == session['sid'],
        #            Online.latest < ten_min_ago).first()
        #    if (r is not None):
        #        Users.DeleteSession(r)
        #        #logger.info('session timeout, your latest are %s', r.latest)
        #        #db.session.delete(r)
        #        #session.clear()
        #        return False

        return True

    @staticmethod
    def UpdateAlive():
        r = Online.query.filter(
                Online.user_id == session['id'], Online.sid == session['sid']).first()
        if (r is None):
            r = Online()

        r.latest = datetime.utcnow()
        r.user_id = session['id']
        r.sid = session['sid']

        db.session.merge(r)
        db.session.flush()
        db.session.commit()
        logger.debug('UpdateAlive done')

    @staticmethod
    def _sign(id, login, passHash):
        # first try to authenticate by token
        #token = Users.generate_auth_token(id)
        #user = Users.verify_auth_token(token)
        #logger.debug('user: %s, token = %s', user, token)
        
        if not user :
            return False

        g.user = user
        session['id'] = user.id
        session['login'] = login
        session['sid'] = sha1().hexdigest()
        #self.admingroup = dict(json.dumps(repr(self.user.admingroup)))
        #self.admingroupStr = (repr(self.user.admingroup)).replace('[', '{').replace(']', '}')
        #Users.UpdateAlive()
        
        return True

    
    @staticmethod
    def create_or_update_user(user):
        try:
            db.session.add(user)
            db.session.flush()
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            return None
            #return omitError(ErrorMsg=repr(error)), 400
        return user

    @staticmethod
    def user_is_exist(email):
        user = obj.query.filter_by(email=email).first()
        return user

    @staticmethod
    def get_by_loginpass(login, passwd):
        user = obj.query.filter_by(login=login, passHash=passwd, isdel = False).scalar()
        return user

    @staticmethod
    def _regist(username, email, avatar_url):
        # Look if the user already exists
        _user = Users.user_is_exist(email)
        if not _user:
            # Create the user. Try and use their name returned by Google,
            # but if it is not set, split the email address at the @.
            nickname = username
            if nickname is None or nickname == "":
                nickname = email.split('@')[0]
    
            # We can do more work here to ensure a unique nickname, if you 
            # require that.
            user = obj()
            user.name = nickname
            user.login = email
            user.email = email
            user.avatar_url = avatar_url
            Users.create_or_update_user(user)
            _user = user

        return _user

    @staticmethod
    def regist_by_google(user):
        username = user['name']
        email = user['email']
        avatar_url = user['picture']
        return Users._regist(username, email, avatar_url)

    @staticmethod
    def regist_by_facebook(user):
        username = user['name']
        email = user['email']
        avatar_url = user['picture']['data']['url']
        return Users._regist(username, email, avatar_url)

