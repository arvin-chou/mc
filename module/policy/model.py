# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from config.config import db, _logging

from ..object.model import ObjectsIpaddrs, ObjectsIpgroups
from .__init__ import __policies_security_tablename__,\
    __policies_security_ipaddrs_table__, __policies_security_ipgroups_table__

logger = _logging.getLogger(__name__)


class PoliciesSecurities(db.Model):
    __tablename__ = __policies_security_tablename__

    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(64), unique=True)

    # directly access secondary entities,
    # such as group -> mapping -> objs
    srcIpAddrs = relationship('ObjectsIpaddrs',
                              backref='ObjectsIpaddrs',
                              secondary=\
                              lambda: PoliciesSecuritiesIpAddrs.__table__)
    # auto get mapping value
    srcIpAddrs_id = association_proxy('srcIpAddrs', 'id')
    srcIpAddrs_name = association_proxy('srcIpAddrs', 'name')

    # auto update mapping table in Create
    srcIpAddrsMapping = relationship('PoliciesSecuritiesIpAddrs',
                                     backref='ObjectsIpaddrs',
                                     cascade='save-update, delete,'\
                                     ' delete-orphan, merge')




    srcIpGroups = relationship('ObjectsIpgroups',
                              backref='ObjectsIpgroups',
                              secondary=\
                              lambda: PoliciesSecuritiesIpGroups.__table__)
    # auto get mapping value
    srcIpGroups_id = association_proxy('srcIpGroups', 'id')
    srcIpGroups_name = association_proxy('srcIpGroups', 'name')

    # auto update mapping table in Create
    srcIpGroupsMapping = relationship('PoliciesSecuritiesIpGroups',
                                     backref='ObjectsIpgroups',
                                     cascade='save-update, delete,'\
                                     ' delete-orphan, merge')


    #dstIpAddrs= Column(db.Integer, ForeignKey('ObjectsIpaddrs.id'), primary_key=True)
    #dstIpGroups = Column(db.Integer, ForeignKey('ObjectsIpgroups.id'), primary_key=True)

    action = db.Column('action', Integer)
    logging = db.Column('logging', Integer)
    enabled = db.Column('enabled', Integer)
    ipprofileLogOnly = db.Column('ipprofileLogOnly', Boolean)

    description =  db.Column(db.String(255))

    def __init__(self):
        pass

    def __repr__(self):
        return '<Name %r>' % self.name

    #@property
    #def value(self):
    #    return self.admingroup and self.admingroup.name


class PoliciesSecuritiesIpAddrs(db.Model):
    __tablename__ = __policies_security_ipaddrs_table__
    id = db.Column(db.Integer, primary_key=True)
    security_id = Column(db.Integer, ForeignKey(PoliciesSecurities.id),
                       primary_key=True)
    ipaddr_id = Column(db.Integer, ForeignKey(ObjectsIpaddrs.id),
                       primary_key=True)

    def __init__(self, security_id, ipaddr_id):
        self.security_id = security_id
        self.ipaddr_id = ipaddr_id

    def __repr__(self):
        return '<Name %r>' % self.__tablename__

class PoliciesSecuritiesIpGroups(db.Model):
    __tablename__ = __policies_security_ipgroups_table__
    id = db.Column(db.Integer, primary_key=True)
    security_id = Column(db.Integer, ForeignKey(PoliciesSecurities.id),
                       primary_key=True)
    ipgroup_id = Column(db.Integer, ForeignKey(ObjectsIpgroups.id),
                       primary_key=True)

    def __init__(self, security_id, ipgroup_id):
        self.security_id = security_id
        self.ipgroup_id = ipgroup_id

    def __repr__(self):
        return '<Name %r>' % self.__tablename__

