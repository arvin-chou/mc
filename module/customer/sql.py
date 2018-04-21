# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, Float, Boolean, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from config.config import _logging, metadata
from datetime import datetime

from .model import CustomerBusinesses, CustomerBusinessgrps, \
        CustomerBusinessDetails, CustomerBusinessComments, CustomerBusinessRates

from module.user.model import Users

from .__init__ import \
        __customer_businesses_businessgrps_tablename__, \
        __customer_businesses_tablename__, \
        __customer_businessgrps_tablename__, \
        __customer_business_details_tablename__, \
        __customer_business_comments_tablename__, \
        __customer_business_pics_tablename__, \
        __customer_business_deals_tablename__, \
        __customer_business_details_comments_tablename__, \
        __customer_business_rates_tablename__, \
        __customer_business_favorite_tablename__

logger = _logging.getLogger(__name__)

SchemaCustomerBusinesses = Table(__customer_businesses_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(64), nullable=False),
    Column('cat', Integer),
    Column('lat', Float()),
    Column('long', Float()),
    Column('deal', Integer),
    Column('description', String(254)),
    Column('ctime', DateTime, default=datetime.utcnow()),
    Column('mtime', DateTime, default=datetime.utcnow()),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    mysql_charset='utf8'
)

SchemaCustomerBusinessgrps = Table(__customer_businessgrps_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(64), nullable=False),
    Column('description', String(254)),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    mysql_charset='utf8'
)

SchemaCustomerBusinessesBusinessgrps = Table(__customer_businesses_businessgrps_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('business_id', None, ForeignKey(CustomerBusinesses.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('businessgrp_id', None, ForeignKey(CustomerBusinessgrps.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    UniqueConstraint('business_id', 'businessgrp_id'),
    mysql_charset='utf8'
)

SchemaCustomerBusinessDetails = Table(__customer_business_details_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('business_id', None, ForeignKey(CustomerBusinesses.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('open', String(4)),
    Column('close', String(4)),
    Column('address', String(254)),
    Column('dist', Integer),
    Column('meals', String(254)),
    Column('features', String(254)),
    Column('ctime', DateTime, default=datetime.utcnow()),
    Column('mtime', DateTime, default=datetime.utcnow()),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    mysql_charset='utf8'
)

SchemaCustomerBusinessComments = Table(__customer_business_comments_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('business_id', None, ForeignKey(CustomerBusinesses.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', None, ForeignKey(Users.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('content', String(254)),
    Column('ctime', DateTime, default=datetime.utcnow()),
    Column('mtime', DateTime, default=datetime.utcnow()),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    mysql_charset='utf8'
)

SchemaCustomerBusinessDeals = Table(__customer_business_deals_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('business_id', None, ForeignKey(CustomerBusinesses.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('title', String(254)),
    Column('description', String(254)),
    Column('ctime', DateTime, default=datetime.utcnow()),
    Column('mtime', DateTime, default=datetime.utcnow()),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    mysql_charset='utf8'
)

SchemaCustomerBusinessPics = Table(__customer_business_pics_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('business_id', None, ForeignKey(CustomerBusinesses.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    # (1, 'icon'), (2, 'bg'), (3, 'gallery')
    Column('type', Integer),
    Column('path', String(254)),
    Column('width', Integer),
    Column('height', Integer),
    Column('ctime', DateTime, default=datetime.utcnow()),
    Column('mtime', DateTime, default=datetime.utcnow()),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    mysql_charset='utf8'
)

SchemaCustomerBusinessDetailsComments = Table(__customer_business_details_comments_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('detail_id', None, ForeignKey(CustomerBusinessDetails.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('comment_id', None, ForeignKey(CustomerBusinessComments.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    UniqueConstraint('detail_id', 'comment_id'),
    mysql_charset='utf8'
)


SchemaCustomerBusinessRates = Table(__customer_business_rates_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('rate', Float()),
    Column('business_id', None, ForeignKey(CustomerBusinesses.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', None, ForeignKey(Users.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('ctime', DateTime, default=datetime.utcnow()),
    Column('mtime', DateTime, default=datetime.utcnow()),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    UniqueConstraint('business_id', 'user_id', 'id'),
    mysql_charset='utf8'
)

SchemaCustomerBusinessFavorite = Table(__customer_business_favorite_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('business_id', None, ForeignKey(CustomerBusinesses.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', None, ForeignKey(Users.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('isdel', Boolean(), default=False, server_default="0", nullable=False),
    mysql_charset='utf8'
)
