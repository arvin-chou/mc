# -*- coding: utf-8 -*-

from sqlalchemy import \
        Table, Column, Integer, String, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from utils import Api, metadata
from config.config import db, _logging

from .__init__ import \
    __customer_businesses_businessgrps_tablename__, \
    __customer_businesses_tablename__, \
    __customer_businessgrps_tablename__

logger = _logging.getLogger(__name__)


class CustomerBusinesses(db.Model):
    __tablename__ = __customer_businesses_tablename__
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    cat = db.Column(db.Integer)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    deal = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    description =  db.Column(db.String(255))

    def __init__(self):
        pass

    def __repr__(self):
        return '<Name %r>' % self.name

    #def value(self):
    #    return self.admingroup and self.admingroup.name


class CustomerBusinessgrps(db.Model):
    __tablename__ = __customer_businessgrps_tablename__
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(64), unique=True)
    description =  db.Column(db.String(255))

    # directly access secondary entities,
    # such as group -> mapping -> objs
    businesses = relationship('CustomerBusinesses',
            backref='CustomerBusinessgrps',
            secondary=lambda: CustomerBusinessesBusinessgrps.__table__)

    business_id = association_proxy('businesses', 'id')
    business_name = association_proxy('businesses', 'name')

    # auto update mapping table
    mapping = relationship('CustomerBusinessesBusinessgrps',
            backref='CustomerBusinessgrps',
            cascade='save-update, delete, delete-orphan, merge')

    def __init__(self):
        pass

    def __repr__(self):
        return '<Name %r>' % self.name

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name

class CustomerBusinessesBusinessgrps(db.Model):
    __tablename__ = __customer_businesses_businessgrps_tablename__
    id = db.Column(db.Integer, primary_key=True)
    business_id = Column(db.Integer, ForeignKey(CustomerBusinesses.id), primary_key=True)
    businessgrp_id = Column(db.Integer, ForeignKey(CustomerBusinessgrps.id), primary_key=True)

    def __init__(self, business_id, businessgrp_id):
        self.business_id = business_id
        self.businessgrp_id = businessgrp_id

    def __repr__(self):
        return '<Name %r>' % self.__tablename__

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name
