# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from utils import Api, metadata
from config.config import db, _logging

from .__init__ import __objects_ipaddrs_ipgroups_tablename__, \
        __objects_ipaddrs_tablename__, __objects_ipgroups_tablename__

logger = _logging.getLogger(__name__)


class ObjectsIpaddrs(db.Model):
    __tablename__ = __objects_ipaddrs_tablename__
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(64), unique=True)
    type =  db.Column(db.String(6))
    ipVersion =  db.Column(db.String(4))
    addr1 =  db.Column(db.String(46))
    addr2 =  db.Column(db.String(46))
    description =  db.Column(db.String(255))

    def __init__(self):
        pass

    def __repr__(self):
        return '<Name %r>' % self.name

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name


class ObjectsIpgroups(db.Model):
    __tablename__ = __objects_ipgroups_tablename__
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(64), unique=True)
    description =  db.Column(db.String(255))

    # directly access secondary entities,
    # such as group -> mapping -> objs
    ipaddrs = relationship(ObjectsIpaddrs,
            backref='ObjectsIpgroups',
            secondary=lambda: ObjectsIpaddrsIpgroups.__table__)

    ipaddr_id = association_proxy('ipaddrs', 'id')
    ipaddr_name = association_proxy('ipaddrs', 'name')

    # auto update mapping table
    mapping = relationship('ObjectsIpaddrsIpgroups',
            backref='ObjectsIpgroups',
            cascade='save-update, delete, delete-orphan, merge')

    def __init__(self):


        pass

    def __repr__(self):
        return '<Name %r>' % self.name

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name

class ObjectsIpaddrsIpgroups(db.Model):
    __tablename__ = __objects_ipaddrs_ipgroups_tablename__
    id = db.Column(db.Integer, primary_key=True)
    ipaddr_id = Column(db.Integer, ForeignKey(ObjectsIpaddrs.id), primary_key=True)
    ipgroup_id = Column(db.Integer, ForeignKey(ObjectsIpgroups.id), primary_key=True)

    def __init__(self, ipaddr_id, ipgroup_id):
        self.ipaddr_id = ipaddr_id
        self.ipgroup_id = ipgroup_id

    def __repr__(self):
        return '<Name %r>' % self.__tablename__

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name
