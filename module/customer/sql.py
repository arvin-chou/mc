# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, Float, MetaData, \
        ForeignKey, DateTime, UniqueConstraint
from config.config import _logging, metadata

from .model import CustomerBusinesses, CustomerBusinessgrps

from .__init__ import \
        __customer_businesses_businessgrps_tablename__, \
        __customer_businesses_tablename__, \
        __customer_businessgrps_tablename__


logger = _logging.getLogger(__name__)

SchemaCustomerBusinesses = Table(__customer_businesses_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(64), unique=True, nullable=False),
    Column('cat', Integer),
    Column('lat', Float()),
    Column('long', Float()),
    Column('deal', Integer),
    Column('description', String(255)),
    Column('image_url', String(255)),
    UniqueConstraint('name')
)

SchemaCustomerBusinessgrps = Table(__customer_businessgrps_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(64), unique=True, nullable=False),
    Column('description', String(255)),
    UniqueConstraint('name')
)

SchemaCustomerBusinessesBusinessgrps = Table(__customer_businesses_businessgrps_tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('business_id', None, ForeignKey(CustomerBusinesses.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('businessgrp_id', None, ForeignKey(CustomerBusinessgrps.id,
        onupdate="CASCADE", ondelete="CASCADE")),
    UniqueConstraint('business_id', 'businessgrp_id')
)
