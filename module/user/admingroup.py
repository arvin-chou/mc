# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import relationship
from config.config import db, metadata
from .users import Users

from .__init__ import \
        __user_users_tablename__, \
        __user_users_head__, \
        __user_online_tablename__, \
        __user_online_head__, \
        __user_admingroup_tablename__, \
        __user_admingroup_head__
