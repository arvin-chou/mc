# -*- coding: utf-8 -*-

from flask.ext.login import UserMixin
from sqlalchemy import \
        Table, Column, Integer, String, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime

from utils import Api, metadata
from config.config import db, _logging, app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from .__init__ import \
        __user_users_tablename__, \
        __user_users_head__, \
        __user_online_tablename__, \
        __user_online_head__, \
        __user_admingroup_tablename__, \
        __user_admingroup_head__

from module.customer.model import CustomerBusinessDetails, CustomerBusinessComments

logger = _logging.getLogger(__name__)

class Users(db.Model, UserMixin):
    __tablename__ = __user_users_tablename__
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(64))
    login =  db.Column(db.String(64), unique=True)
    #email =  db.Column(db.String(255))
    description =  db.Column(db.String(255))
    avatar_url =  db.Column(db.String(254))
    passHash =  db.Column(db.String(64))
    preferences =  db.Column(db.String(64))
    #sid = db.Column(db.String(64))
    #latest = db.Column(db.DateTime, ForeignKey(Online.id))
    user = None

    #admingroup_id = Column(db.Integer, ForeignKey(User.id), primary_key=True)
    admingroup = relationship('AdminGroup', foreign_keys='AdminGroup.user_id',
            # we dont need delete all->readd
            cascade='save-update, delete-orphan',
            backref=__user_users_tablename__, lazy='joined')
    #admingroup = relationship('AdminGroup', foreign_keys='AdminGroup.user_id', backref=__user_users_tablename__, lazy='dynamic')
    #admingroup = relationship('AdminGroup', foreign_keys='AdminGroup.user_id', backref=__user_users_tablename__, lazy='joined', collection_class=mapped_collection(lambda user: {'admingroup': user.__dict__}))
    online = relationship('Online', foreign_keys='Online.user_id', backref=__user_users_tablename__, lazy='joined')
    online_id = relationship('Online', cascade='all,delete,delete-orphan', backref='User')
    admingroupStr = None
    #comment_id = Column(db.Integer, ForeignKey(CustomerBusinessComments.id))
    isdel = db.Column(db.Boolean, default=False) 
    # LEFT OUTER JOIN
    #admingroup_obj = relationship('AdminGroup', lazy='joined', cascade='all')


    def __init__(self):
        pass

    def __repr__(self):
        return '<Name %r>' % self.name

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_authenticated(self):
        """
        Returns `True`. User is always authenticated. Herp Derp.
        """
        return True

    def is_anonymous(self):
        """
        Returns `False`. There are no Anonymous here.
        """
        return False

    def get_id(self):
        """
        Assuming that the user object has an `id` attribute, this will take
        that and convert it to `unicode`.
        """
        try:
            #return unicode(self.id)
            return str(self.id).encode('utf-8')
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override get_id")

    def __eq__(self, other):
        """
        Checks the equality of two `UserMixin` objects using `get_id`.
        """
        if isinstance(other, UserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Checks the inequality of two `UserMixin` objects using `get_id`.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal
    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        #print("s=", s)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        logger.debug('verify_auth_token s: %s', s)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token

        user = Users.query.get(data['id'])
        return user



class Online(db.Model):
    __tablename__ = __user_online_tablename__
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sid = db.Column(db.String(64))
    latest = db.Column(DateTime, default=datetime.utcnow())
    user_id = Column(db.Integer, ForeignKey(Users.id), primary_key=True)
    #user_id = relationship('', cascade='all,delete', backref='User')

    def __init__(self):
        pass

    def __repr__(self):
        return '<latest: %r>' % self.latest

class AdminGroup(db.Model):
    __tablename__ = __user_admingroup_tablename__
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(64))
    permission =  db.Column(db.String(64))
    user_id = db.Column(db.Integer, ForeignKey(Users.id), primary_key=True)
    isdel = db.Column(db.Boolean, default=False) 

    #LEFT OUTER JOIN `User`
    #user_obj = relationship('User', lazy='joined', cascade='all')
    #user_obj = relationship('User', lazy='dynamic', cascade='all')
    #username = Column(String(32), index=True, server_default='', nullable=False)
    #friends = relationship('Friend', backref='Friend.friend_id',primaryjoin='User.id==Friend.user_id', lazy='dynamic')
    #chat_memb = db.relationship('user', secondary=chat_members,
    #                                    backref=db.backref('chats', lazy='dynamic'))
    #chat.query.join(user.chats).filter(user.id == 1).all()
    #subq = sess.query(Score.user_id, func.sum(Score.amount).label('score_increase')).\
    #        filter(Score.created_at > someday).\
    #        group_by(Score.user_id).subquery()
    #sess.query(User).join((subq, subq.c.user_id==User.user_id)).order_by(subq.c.score_increase)

    def __init__(self):
        pass

    def serialize():
        return {
                '_id': 1,
                'username': self.name,
                'fullname': u'George Washington'
                # other fields that you need in the json
                }
    def __repr__(self):
    #    return self.__dict__
    #    return "<"+self.__tablename__+"('{}','{}','{}')>".format(
    #            self.id, self.permission, self.name)

    #    return '"{Name:%r}"' % self.name
    #    return '<Name: %r>' % self.name
    #    #return { 'id': self.id, 'permission': self.permission, 'name': self.name }
    #    #return '<id: %r, permission: %r, name:%r>' % self.id, self.permission, self.name
    #    #return '<id: %r, permission: %r, name:%r>' % self.id, self.permission, self.name
        return 'id: "{}", permission: "{}", name: "{}"'.format(self.id, self.permission, self.name)
    #    return '{id: %d, permission: %s, name:%s}'.format(self.id, self.permission, self.name)
    #    #return '"Name %r"' % self.name
    #    #return '<Name %r>' % self.name

    @staticmethod
    def verify_auth_token(token):
        pass

    #@validates('email')
    #def validate_email(self, key, address):
    #    assert '@' in address
    #    return address

    #def __init__(self, name, surname):
    #    self.name = name
    #    self.surname = surname

    #def __repr__(self):
    #    return u'%s %s, %s' % (self.name, self.surname, self.pesel)



