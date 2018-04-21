# -*- coding: utf-8 -*-

import os
import json
import traceback
import sys
#import re

from flask import Flask, request, Response, jsonify, g, session
from sqlalchemy.orm import lazyload, joinedload, subqueryload, contains_eager
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import mapped_collection
from config.config import _logging, api, app, db
from utils import reqparse, abort, Resource, fields, marshal, inputs
from utils.error import ErrorCode, omitError
from module.common import add_argument
from schema.users import User
from schema.usersmadmingroup import UsersMAdminGroup
from schema.admingroup import AdminGroup

logger = _logging.getLogger(__name__)

__head__ = 'admin'
__heads__ = 'admins'
# Admins
#   validate admins setting, routing from /rest/admin/
#def str_range(value, name, op, argument):
#    low, high = argument.split(',')
#    print(low, 'x', high, value)
#    return inputs.str_range(low, high, value)


field_inputs = {
    'id': {
        'type': fields.Integer},
    'login': {
        'type': fields.String,
        'validator': {'name': inputs.wrap_str_range, 'argument': '1,64'}},
    'passHash': {
        'type': fields.String},
    'name': {
        'type': fields.String,
        'validator': {'name': inputs.wrap_str_range, 'argument': '1,64'}},
    'email': {
        'type': fields.String,
        'validator': {'name': inputs.email}},
    'admingroup': {
        'type': fields.List(fields.Nested({'id': fields.Integer(attribute='id')}))},
    'preferences': {
        'type': fields.String},
    'description': {
        'type': fields.String,
        'validator': {'name': inputs.wrap_str_range, 'argument': '0,254'}},
}

field_inputs_wrap = {
    'total': {'type': fields.Integer},
    'itemsPerPage': {'type': fields.Integer(default=25),
            'validator': {'name': inputs.str_in_list, 'argument': []}},
    'page': {'type': fields.Integer(default=1),
            'validator': {'name': inputs.int_in_list, 'argument': [0, 25, 50, 100]}},
    'orderBy': {'type': fields.String(default='login'),
            'validator': {'name': inputs.str_in_list,
                'argument': ['name', 'login', 'email', 'description']}},
    'desc': {'type': fields.Boolean(default=False),
            'validator': {'name': inputs.boolean}}
}

resource_fields = dict((k, v['type']) for k,v in field_inputs.items())
resource_fields_wrap = dict((k, v['type']) for k,v in field_inputs_wrap.items())
resource_fields_wrap[__heads__] = fields.List(fields.Nested(resource_fields))

dataDict = None
message = {
        'errorId': ErrorCode['CE_INVALID_PARAM'],
        'message': ''
        }
_reqparse = reqparse.RequestParser()

class Admin(Resource):
    def __init__(self):
        self.dataDict = request.get_json()
        #self.dataDict = json.loads(repr(request.data))

        # downgrand one layer, from {admin:{a:1, b:2}} to {a:1, b:2}
        request.dataDict = self.dataDict[__head__]
        add_argument(_reqparse, field_inputs)
        super(Admin, self).__init__()

    #@marshal_with(task_list_format)
    def put(self, id):
        
        try:
            args = _reqparse.parse_args()
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            message['message'] = ' '.join(error.args)
            return message, 400

        #task = {}
        #print(args, 'xxxx')
        #r = User.query.filter(
        #        User.id == id).options(lazyload('AdminGroup').first()
        # one to many
        r = UsersMAdminGroup.query.filter(
                UsersMAdminGroup.user_id == id).all()
        #print(_r.user_obj.login, 'xxxx')
        #r = User.query.filter(
        #        User.id == id).first()

        #rr = UsersMAdminGroup.query.filter(
        #        UsersMAdminGroup.user_id == id).all()

        if len(r) is 0:
            message['message'] = 'user id {} not found'.format(id)
            return message, 400

        else:
            for k, v in args.items():
                if v != None :
                    if k == 'admingroup':
                        continue

                    #print(k, v, 'v', type(v) is dict, type(v))
                    setattr(r[0].user_obj, k, v)

                    #data = json.loads(repr(v))
            db.session.add(r[0].user_obj)

            # update foreign table
        # delete all mapping
        if args['admingroup']:
            #print("args['admingroup']",
            #        json.loads(args['admingroup'][1].replace('\'', '"')))
            try:

                for _r in r:
                    # 1. delete all
                    db.session.delete(_r)

                db.session.flush()

                for entity in args['admingroup']:
                    # 2. re-add it
                    rr = UsersMAdminGroup()
                    rr.admingroup_id = json.loads((entity.replace('\'', '"'))).get('id')
                    rr.user_id = id
                    db.session.add(rr)
                
            except Exception as error:
                # for ambiguous
                #(TypeError, ValueError) as err:
                logger.debug('impossible that parsing json %s error(%s)',
                        args['admingroup'], error)
                pass
        #return message, 400

        #db.session.commit()
        try:
            db.session.commit()
        except Exception as error:
            logger.warning('session commit error(%s)', error)
            db.session.rollback()
            return message, 400

        #print(dict((k, v['type']) for k,v in field_inputs.items()))
        # http://stackoverflow.com/questions/7389759/memory-efficient-built-in-sqlalchemy-iterator-generator
        #args['admingroup'] = dict(('id', getattr(_r,'id')) for _r in rr)
        #r = UsersMAdminGroup.query.filter(UsersMAdminGroup.user_id == id) \
        #    .with_entities(UsersMAdminGroup.admingroup_id).all()
        #r = UsersMAdminGroup.query.filter(
        #        UsersMAdminGroup.user_id == id).with_entities(UsersMAdminGroup.user_id,
        #                UsersMAdminGroup.admingroup_id).all()
        r = UsersMAdminGroup.query.filter(
                UsersMAdminGroup.user_id == id).all()

        for col in r[0].user_obj.__table__.columns.keys():
            args[col] = getattr(r[0].user_obj, col)

        args['admingroup'] = [];
        for _r in r:
            args['admingroup'].append({'id': getattr(_r, 'admingroup_id')})

        # http://stackoverflow.com/questions/15261149/sqlalchemy-how-is-it-that-a-comma-determines-if-a-query-returns-a-string-or-a-t
        #for _r, in r:
        #    args['admingroup'].append({'id': _r})
            #args['admingroup'].append( \
            #    dict((col, getattr(_r, col))
            #            for col in _r.__table__.columns.keys() if col is not 'id'))
            #print(dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys()))
            #print(dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys() if col is not 'id'))


        #return {'task': 'Hello world'}, 201, {'Etag': 'some-opaque-string'}

        #return message, 200
        return marshal(args, resource_fields), 200
        # 204 no content
        #return message, 204

    def get(self, id):
        # one to many
        try:
            self.args = _reqparse.parse_args()
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            message['message'] = ' '.join(error.args)
            return message, 400

        r = User.query.filter(User.id == id).scalar()

        if r is None:
            message['message'] = 'user id {} not found'.format(id)
            return message, 400

        for col in r.__table__.columns.keys():
            self.args[col] = getattr(r, col)

        self.args[AdminGroup.__tablename__] = r.admingroup

        return marshal(self.args, resource_fields), 200


class Admins(Resource):
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        #request.dataDict = request.get_json()[__head__]
        #orderByValidatedList = ['login', 'name']
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        #_reqparse.add_argument('orderBy', type = inputs.email, location=['dataDictWrap'], help='Rate cannot be converted')
        add_argument(_reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(Admins, self).__init__()

    def get(self):
        # one to many
        try:
            self.args = _reqparse.parse_args()
            self.response = dict(marshal(self.args, resource_fields_wrap).items())
            self.args[__heads__] = []
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            message['message'] = ' '.join(error.args)
            return message, 400

        itemsPerPage = self.response['itemsPerPage']
        page = self.response['page'] - 1
        orderBy = getattr(User, self.response['orderBy'])
        isDesc = getattr(orderBy, 'desc' if self.response['desc'] else 'asc')


        r = User.query.order_by(isDesc())

        if itemsPerPage is 0:
            r = r.all()
        else:
            # .order_by(User.login.desc())
            r = r.offset(itemsPerPage * page)\
                    .limit(itemsPerPage)\
                    .all()
        for _r in r:
            __r = dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys())
            __r['admingroup'] = _r.admingroup
            self.args[__heads__].append(__r)

        self.args['total'] = len(User.query.all())

        resource_fields_wrap[__heads__] = fields.List(fields.Nested(resource_fields))
        return marshal(self.args, resource_fields_wrap), 200

    def delete(self):
        try:
            ids = request.args.get(__heads__).split(',')
        except Exception as error:
            return omitError(ErrorMsg='param `{}` not found'.format(__heads__)), 400

        for id in ids:
            try:
                id = inputs.natural(id)
            except Exception as error:
                return omitError(ErrorMsg='user id `{}` not int'.format(id)), 400

            # it could als cascade delete `online` user
            r = User.query.filter(User.id == id).first()
            if r is None:
                db.session.rollback()
                return omitError('CE_NOT_EXIST',
                        'admin id {} not found'.format(id)), 400

            db.session.delete(r)

        try:
            db.session.flush()
            db.session.commit()
        except Exception as error:
            logger.warning('session commit error(%s)', error)
            db.session.rollback()
            return message, 400

        return message, 204
        # one to many
        try:
            self.args = _reqparse.parse_args()
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            message['message'] = ' '.join(error.args)
            return message, 400

        r = User.query.filter(User.id == id).scalar()

        if r is None:
            message['message'] = 'user id {} not found'.format(id)
            return message, 400

        for col in r.__table__.columns.keys():
            self.args[col] = getattr(r, col)

        self.args[AdminGroup.__tablename__] = r.admingroup

        return marshal(self.args, resource_fields), 200


