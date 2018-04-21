# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, Float, Boolean, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from config.config import _logging, metadata
from datetime import datetime

from module.user.model import Users
from module.customer.model import CustomerBusinesses

from .__init__ import __pushno_tablename__

logger = _logging.getLogger(__name__)


SchemaPushno = Table(__pushno_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('type', Integer),
    Column('dev_id', String(254)),
    Column('user_id', None, ForeignKey(Users.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('business_id', None, ForeignKey(CustomerBusinesses.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('ctime', DateTime, default=datetime.utcnow()),
    Column('mtime', DateTime, default=datetime.utcnow()),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    UniqueConstraint('user_id', 'id', 'dev_id'),
    mysql_charset='utf8'
)
