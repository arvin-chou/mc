# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, \
        MetaData, ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from config.config import db, metadata
from schema.users import User
from schema.admingroup import AdminGroup

__tablename__ = 'usersmadmingroup'

class UsersMAdminGroup(db.Model):
    __tablename__ = __tablename__
    id = Column(Integer, primary_key=True)
    #user_id = Column(Integer)
    #admingroup_id = Column(Integer)
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    admingroup_id = Column(Integer, ForeignKey(AdminGroup.id), primary_key=True)
    #user_id = Column(Integer, ForeignKey(User.id))
    #admingroup_id = Column(Integer, ForeignKey(AdminGroup.id))
    __table_args__ = (UniqueConstraint('user_id', 'admingroup_id',
        name='_user_admingroup'),
        )
    # if user delete, this mapping also delete too.
    user_obj = relationship('User', backref=backref('users', uselist=True,
                                 cascade='delete,all', lazy='dynamic'))
    admingroup_obj = relationship('AdminGroup',
            backref=backref('admingroups', lazy='dynamic'))

    #user_obj = relationship('User', lazy='dynamic', cascade='all')
    #admingroup_obj = relationship('AdminGroup', lazy='dynamic', cascade='all')
    #__table_args__ = (ForeignKeyConstraint(
    #    #[user_id, admingroup_id],[User.id, AdminGroup.id]), {})
    #    [user_id, admingroup_id],['user.id', 'admingroup.id']), {})


SchemaUsersMAdminGroup = Table(__tablename__, metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', None, ForeignKey('users.id')),
            #ForeignKey("new.new_id", onupdate="CASCADE",
            #    ondelete="CASCADE"),
                #Column('location_code', Unicode(10)),


    Column('admingroup_id', None, ForeignKey('admingroup.id')),
    UniqueConstraint('user_id', 'admingroup_id')
    #ForeignKeyConstraint(['user_id', 'admingroup_id'], ['user.id',
    #    'admingroup.id'])

)
