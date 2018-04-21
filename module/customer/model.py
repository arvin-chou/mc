# -*- coding: utf-8 -*-

from sqlalchemy import \
        Table, Column, Integer, String, Boolean, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime

from utils import Api, metadata
from config.config import db, _logging

from .__init__ import \
        __customer_businesses_businessgrps_tablename__, \
        __customer_businesses_tablename__, \
        __customer_businessgrps_tablename__, \
        __customer_business_details_tablename__, \
        __customer_business_comments_tablename__, \
        __customer_business_deals_tablename__, \
        __customer_business_pics_tablename__,\
        __customer_business_details_comments_tablename__, \
        __customer_business_rates_tablename__, \
        __customer_business_favorite_tablename__

from module.user.__init__ import \
        __user_users_tablename__

logger = _logging.getLogger(__name__)


class CustomerBusinesses(db.Model):
    __tablename__ = __customer_businesses_tablename__
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    cat = db.Column(db.Integer)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    deal = db.Column(db.Integer)
    #image_url = db.Column(db.String(254))
    description = db.Column(db.String(254))

    #detail_id = db.Column(db.Integer, db.ForeignKey('CustomerBusinessDetails.id'))
    #detail = db.relationship('CustomerBusinessDetails', backref='CustomerBusinesses')
    detail = db.relationship('CustomerBusinessDetails', backref='CustomerBusinessDetails.business_id', primaryjoin='CustomerBusinesses.id==CustomerBusinessDetails.business_id', lazy='joined', uselist=False)

    #detail = db.relationship('CustomerBusinessDetails', foreign_keys='CustomerBusinessDetails.business_id', backref=__customer_businesses_tablename__, lazy='joined')
    #detail_id = relationship('CustomerBusinessDetails', cascade='all,delete,delete-orphan', backref='CustomerBusinessDetails')


    #description = relationship('CustomerBusinessDetails', uselist=False,
    #        backref="CustomerBusinesses")
    #description = relationship('CustomerBusinessDetails', foreign_keys='CustomerBusinessDetails.description', backref=__customer_business_details_tablename__, lazy='joined')

    isdel = db.Column(db.Boolean, default=False) 

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
    description =  db.Column(db.String(254))
    isdel = db.Column(db.Boolean, default=False) 

    # directly access secondary entities,
    # such as group -> mapping -> objs
    businesses = relationship(CustomerBusinesses,
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
    isdel = db.Column(db.Boolean, default=False) 

    def __init__(self, business_id, businessgrp_id):
        self.business_id = business_id
        self.businessgrp_id = businessgrp_id

    def __repr__(self):
        return '<Name %r>' % self.__tablename__

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name


class CustomerBusinessDetails(db.Model):
    __tablename__ = __customer_business_details_tablename__
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, 
            ForeignKey(CustomerBusinesses.id), primary_key=True)

    meta = db.relationship(CustomerBusinesses, backref='CustomerBusinesses.id', primaryjoin='CustomerBusinesses.id==CustomerBusinessDetails.business_id', lazy='joined', uselist=False)

    #business_id = relationship('CustomerBusinesses', 
    #        foreign_keys='CustomerBusinessDetails.business_id',
    #        backref=__customer_businesses_tablename__, lazy='joined')
    #name = relationship('CustomerBusinesses', 
    #        foreign_keys='CustomerBusinessDetails.name',
    #        backref=__customer_businesses_tablename__, lazy='joined')
    #cat = relationship('CustomerBusinesses', 
    #        foreign_keys='CustomerBusinessDetails.cat',
    #        backref=__customer_businesses_tablename__, lazy='joined')
    #lat = relationship('CustomerBusinesses', 
    #        foreign_keys='CustomerBusinessDetails.lat',
    #        backref=__customer_businesses_tablename__, lazy='joined')
    #long = relationship('CustomerBusinesses', 
    #        foreign_keys='CustomerBusinessDetails.long',
    #        backref=__customer_businesses_tablename__, lazy='joined')
    #deal = relationship('CustomerBusinesses', 
    #        foreign_keys='CustomerBusinessDetails.deal',
    #        backref=__customer_businesses_tablename__, lazy='joined')
    #image_url = relationship('CustomerBusinesses', 
    #        foreign_keys='CustomerBusinessDetails.image_url',
    #        backref=__customer_businesses_tablename__, lazy='joined')

    open = db.Column(db.String(4))
    close = db.Column(db.String(4))
    dist = db.Column(db.Integer)
    address = db.Column(db.String(254))
    meals = db.Column(db.String(253))
    features = db.Column(db.String(254))

    #like_users = relationship('Users', backref="CustomerBusinessDetails")
    #like_users = db.relationship('Users', backref='Users.like_id', primaryjoin='CustomerBusinesses.id==Users.like_id', lazy='joined')

    #likes_user_avatar = relationship('Users', 
    #        foreign_keys='Users.avatar',
    #        backref=__user_users_tablename__, lazy='joined')


    #comments = db.relationship('CustomerBusinessComments', 
    #        backref='CustomerBusinessComments.business_id', 
    #        primaryjoin='CustomerBusinessComments.business_id==CustomerBusinessDetails.business_id', lazy='joined')
    #rates = relationship('CustomerBusinessRates',
    #        backref='CustomerBusinessDetails',
    #        secondary=lambda: CustomerBusinessDetailsRates.__table__)
    # directly access secondary entities,
    # such as group -> mapping -> objs
    comments = relationship('CustomerBusinessComments',
            backref='CustomerBusinessDetails',
            secondary=lambda: CustomerBusinessDetailsComments.__table__)

    #business_id = association_proxy('businesses', 'id')
    #business_name = association_proxy('businesses', 'name')

    ## auto update mapping table
    #mapping = relationship('CustomerBusinessDetailsComments',
    #        backref='CustomerBusinessDetails',
    #        cascade='save-update, delete, delete-orphan, merge')

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


class CustomerBusinessComments(db.Model):
    __tablename__ = __customer_business_comments_tablename__
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, 
            ForeignKey(CustomerBusinesses.id), primary_key=True)
    # FIXME: not use hard code in ForeignKey('users.id'))
    user_id = db.Column(db.Integer, 
            ForeignKey('users.id'), primary_key=True)


    #user = db.relationship('Users')
    #user = db.relationship('Users', backref='CustomerBusinessComments')
    #user = db.relationship('Users', backref='CustomerBusinessComments', primaryjoin='Users.comment_id==CustomerBusinessComments.id', lazy='joined')
    #user = relationship('Users', foreign_keys='Users.comment_id',
    #        # we dont need delete all->readd
    #        cascade='save-update, delete-orphan',
    #        backref=__user_users_tablename__, lazy='joined')
    #user = relationship('Users',
    #            #primaryjoin='CustomerBusinessComments.user_id == Users.id',
    #                backref=backref(__customer_business_comments_tablename__, lazy='joined'))

    content = db.Column(db.String(254))
    #rate = db.Column(db.Integer)

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

class CustomerBusinessDetailsComments(db.Model):
    __tablename__ = __customer_business_details_comments_tablename__
    id = db.Column(db.Integer, primary_key=True)
    detail_id = db.Column(db.Integer, 
            ForeignKey(CustomerBusinessDetails.id), primary_key=True)
    comment_id = db.Column(db.Integer, 
            ForeignKey(CustomerBusinessComments.id), primary_key=True)

    isdel = db.Column(db.Boolean, default=False) 

    def __init__(self, detail_id, comment_id):
        self.detail_id = detail_id
        self.comment_id = comment_id
        #self.list_type = list_type
        #        if created_at is None:
        #                        created_at = datetime.utcnow()
        #                                self.created_at = created_at

    def __repr__(self):
        return '<Name %r>' % self.__tablename__

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name




class CustomerBusinessDeals(db.Model):
    __tablename__ = __customer_business_deals_tablename__
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, 
            ForeignKey(CustomerBusinesses.id), primary_key=True)
    title = db.Column(db.String(254))
    description = db.Column(db.String(254))

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

class CustomerBusinessPics(db.Model):
    __tablename__ = __customer_business_pics_tablename__
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, 
            ForeignKey(CustomerBusinesses.id), primary_key=True)
    # (1, 'icon'), (2, 'bg'), (3, 'gallery')
    type = db.Column(db.Integer)
    height = db.Column(db.Integer)
    width = db.Column(db.Integer)
    path = db.Column(db.String(254))
    #icon = db.Column(db.String(254))
    #bg = db.Column(db.String(254))

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

class CustomerBusinessRates(db.Model):
    __tablename__ = __customer_business_rates_tablename__
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Float)
    business_id = db.Column(db.Integer, 
            ForeignKey(CustomerBusinesses.id), primary_key=True)
    user_id = db.Column(db.Integer, 
            ForeignKey('users.id'), primary_key=True)

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

class CustomerBusinessFavorite(db.Model):
    __tablename__ = __customer_business_favorite_tablename__
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, 
            ForeignKey(CustomerBusinesses.id), primary_key=True)
    user_id = db.Column(db.Integer, 
            ForeignKey('users.id'), primary_key=True)
    isdel = db.Column(db.Boolean, default=False) 

    def __init__(self):
        pass

    def __repr__(self):
        return '<Name %r>' % self.__tablename__

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name


