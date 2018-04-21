# -*- coding: utf-8 -*-

from sqlalchemy import \
        Table, Column, Integer, String, Boolean, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime

from utils import Api, metadata
from config.config import db, _logging
from module.customer.model import CustomerBusinesses

from .__init__ import __pushno_tablename__

logger = _logging.getLogger(__name__)


class Pushno(db.Model):
    __tablename__ = __pushno_tablename__
    id = db.Column(db.Integer, primary_key=True)
    # (1, 'andriod'), (2, 'ios')
    type = db.Column(db.Integer)
    dev_id = db.Column(db.String(254))
    user_id = db.Column(db.Integer, 
            ForeignKey('users.id'), primary_key=True)
    business_id = db.Column(db.Integer, 
            ForeignKey(CustomerBusinesses.id), primary_key=True)

    mtime = db.Column(DateTime, default=datetime.utcnow())
    ctime = db.Column(DateTime, default=datetime.utcnow())
    isdel = db.Column(db.Boolean, default=False) 

    def __init__(self):
        pass

    def __repr__(self):
        return '<Name %r>' % self.__tablename__

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name
