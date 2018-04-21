# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, Boolean,\
    ForeignKey, UniqueConstraint

from config.config import _logging, metadata
from ..object.model import ObjectsIpaddrs, ObjectsIpgroups

from .model import PoliciesSecurities
from .__init__ import __policies_security_tablename__,\
    __policies_security_ipaddrs_table__, __policies_security_ipgroups_table__

logger = _logging.getLogger(__name__)

SchemaPoliciesSecurity = Table(__policies_security_tablename__, metadata,
                               Column('id', Integer, primary_key=True),
                               Column('name', String(64), unique=True,
                                      nullable=False),
                               Column('action', Integer),
                               Column('logging', Integer),
                               Column('enabled', Integer),
                               Column('ipprofileLogOnly', Boolean),
                               Column('description', String(255)),
                               UniqueConstraint('name')
                               )

SchemaPoliciesSecurityIpAddrs = Table(__policies_security_ipaddrs_table__, metadata,
    Column('id', Integer, primary_key=True),
    Column('ipaddr_id', None, ForeignKey(ObjectsIpaddrs.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('security_id', None, ForeignKey(PoliciesSecurities.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    UniqueConstraint('ipaddr_id', 'security_id')
)

SchemaPoliciesSecurityIpGroups = Table(__policies_security_ipgroups_table__, metadata,
    Column('id', Integer, primary_key=True),
    Column('ipgroup_id', None, ForeignKey(ObjectsIpgroups.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('security_id', None, ForeignKey(PoliciesSecurities.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    UniqueConstraint('ipgroup_id', 'security_id')
)
