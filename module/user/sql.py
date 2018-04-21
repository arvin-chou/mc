# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, Float, Boolean, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from datetime import datetime, timedelta
from config.config import _logging, metadata

from .__init__ import \
        __user_users_tablename__, \
        __user_users_head__, \
        __user_online_tablename__, \
        __user_online_head__, \
        __user_admingroup_tablename__, \
        __user_admingroup_head__


logger = _logging.getLogger(__name__)

SchemaUsers = Table(__user_users_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(64)),
    Column('login', String(64), nullable=False),
    #Column('email', String(255)),
    Column('passHash', String(64)),
    Column('preferences', String(64)),
    Column('description', String(255)),
    Column('avatar_url', String(255)),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
)

SchemaOnline = Table(__user_online_tablename__, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sid', String(64)),
    Column('latest', DateTime, default=datetime.utcnow()),
    Column('user_id', None, ForeignKey('users.id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

SchemaAdminGroup= Table(__user_admingroup_tablename__, metadata,
    Column('id', Integer, primary_key=True, unique=True),
    Column('name', String(64)),
    Column('permission', String(64)),
    Column('user_id', None, ForeignKey('users.id')),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
)
