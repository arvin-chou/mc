# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from config.config import _logging, metadata

from .model import ObjectsIpaddrs, ObjectsIpgroups
from .__init__ import __objects_ipaddrs_ipgroups_tablename__, \
        __objects_ipaddrs_tablename__, __objects_ipgroups_tablename__


logger = _logging.getLogger(__name__)

SchemaObjectsIpaddrs = Table(__objects_ipaddrs_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(64), unique=True, nullable=False),
    Column('type', String(6)), # tuple (Single, Range, Subnet)
    Column('ipVersion', String(4)), # tuple (IPv4, IPv6)
    Column('addr1', String(46)), # INET6_ADDRSTRLEN to be 46
    Column('addr2', String(46)), # INET6_ADDRSTRLEN to be 46
    Column('description', String(255)),
    UniqueConstraint('name')
)

SchemaObjectsIpgroups = Table(__objects_ipgroups_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(64), unique=True, nullable=False),
    Column('description', String(255)),
    UniqueConstraint('name')
)

SchemaObjectsIpaddrsIpgroups = Table(__objects_ipaddrs_ipgroups_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('ipaddr_id', None, ForeignKey(ObjectsIpaddrs.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('ipgroup_id', None, ForeignKey(ObjectsIpgroups.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    UniqueConstraint('ipaddr_id', 'ipgroup_id')
)
