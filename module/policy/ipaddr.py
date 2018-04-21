# -*- coding: utf-8 -*-

import json
import traceback
import os.path
#import re

from flask import Flask, request, Response, jsonify, g, session
from werkzeug.exceptions import BadRequest
from sqlalchemy import exc
from sqlalchemy.orm import lazyload, joinedload, subqueryload, contains_eager
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import mapped_collection

from config.config import _logging, api, app, db, platform_model_config
logger = _logging.getLogger(__name__)

from utils import reqparse, abort, Resource, fields, marshal, inputs
from utils.error import ErrorCode, omitError

# for ip validate
import socket

from module.common import add_argument, GetResource, ExtraParamsIsValid
from module.common import field_inputs_wrap as _field_inputs_wrap
from module.common import field_inputs_ref as _field_inputs_ref
from module.common import field_inputs as _field_inputs


#
# predefind validate in each column, please ref to MRQ
#
from .model import ObjectsIpaddrs as obj
from .__init__ import __objects_ipaddr_head__ as __head__, \
        __objects_ipaddr_heads__ as __heads__

# our dir structure is just like: module/{modulename}/feature
moduleName = os.path.dirname(__file__).rsplit(os.path.sep, 1)[1]
limit = platform_model_config[moduleName][__heads__]

field_inputs = _field_inputs.copy()
field_inputs_ref = _field_inputs_ref.copy()
field_inputs_wrap = _field_inputs_wrap.copy()
_reqparse = reqparse.RequestParser()

field_inputs['ipVersion'] =  {
        'type': fields.String,
        'required': True,
        'validator': {
            'name': inputs.str_in_list,
            'argument': ['IPv4', 'IPv6']
            }
        }

field_inputs['type'] =  {
        'type': fields.String,
        'validator': {
            'name': inputs.str_in_list,
            'argument': ['Single', 'Range', 'Subnet']
            }
        }

field_inputs['addr1'] =  {
        'type': fields.String,
        'required': True,
        'validator': {
            'name': inputs.wrap_str_range, 'argument': '1,46'
            }
        }

field_inputs['addr2'] =  field_inputs['addr1'].copy()

#field_inputs_ref[] =  field_inputs_ref['secpolicies'].copy()

field_inputs_wrap['orderBy']['type'] = fields.String(default='name')
field_inputs_wrap['orderBy']['validator']['argument'] = \
    ['name', 'type', 'description']

resource_fields, resource_fields_ref, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_ref, field_inputs_wrap, __heads__)

def checkInputIsValid(args={}):
    try:
        # now we only support IPv4/IPv6
        args['addr1'] = inputs.is_ipv4_ipv6(args['addr1'], argument=args['ipVersion'])
    except socket.error as error:
        # Not legal
        logger.debug('traceback.format_exc(%s)', traceback.format_exc())
        raise ValueError(omitError('CE_INVALID_PARAM',
                '`{}/{}`: {}'.format(args['addr1'], args['ipVersion'], error.args)), 400
                )

    ip = args['addr1']
    ver = args['ipVersion']
    pre = args['addr2']

    try:
        if args['type'] == 'Single':
            # TODO: maybe we limit that could not pass anything in attribute 'addr2'
            pass

        elif args['type'] == 'Range':
            # do the same as below
            pre = inputs.is_ipv4_ipv6(pre, argument=ver)
            # legal
        elif args['type'] == 'Subnet':
            # do the same as below
            if 'IPv4' == ver:
                #NOTICE: maybe correct user's input?
                try:
                    ip = inputs.is_cidr(ip, argument=pre)
                except Exception as error:
                    pre = inputs.is_netmask(pre)

            elif 'IPv6' == ver:
                pre = inputs.is_ipv6_prefix(ip, argument=pre)
            # legal

    except Exception as error:
        # Not legal
        logger.debug('traceback.format_exc(%s)', traceback.format_exc())
        raise ValueError( omitError('CE_INVALID_PARAM', '`{}/{}({})`: {}'.\
                format(ip, pre, ver, error.args)), 400)



class ObjectIpaddr(Resource):
    def __init__(self):
        #self.reqparse = reqparse.RequestParser()
        #self.reqparse.add_argument('login', type = str, location = 'json')
        #self.reqparse.add_argument('email', type = field_inputs['email']['validator']['name'], location = ['dataDict'],
        #        required=False, help='email Valid Error')
        #add_argument(self.reqparse, field_inputs)
        #for k, v in field_inputs.items():
        #    _type = v.get('validator', {}).get('name', str)
        #    self.reqparse.add_argument(k, type = _type, location = ['dataDict'],
        #        required=v.get('required', False),
        #        argument=v.get('validator', {}).get('argument'),
        #        help='{} Valid Error'.format(k))


        #self.reqparse.add_argument('email', type = field_inputs['email']['validator']['name'], location = ['dataDict'],
        #        required=False, help='email Valid Error')
        #self.reqparse.add_argument('description', type = validator.description, location = ['dataDict'],
        #       required=True, help='description Valid Error')
        #self.reqparse.add_argument('login', type = validator['login'], location=['dataDict'],
        #        help='login Valid Error', dest='login',
        #        argument='1,64')

        # raise ValueError('Malformed JSON')
        self.dataDict = request.get_json()
        #self.dataDict = json.loads(repr(request.data))

        # downgrand one layer, from {admin:{a:1, b:2}} to {a:1, b:2}
        request.dataDict = self.dataDict[__head__]
        add_argument(_reqparse, field_inputs)
        super(ObjectIpaddr, self).__init__()

    #@marshal_with(task_list_format)
    def put(self, id):
        requestArgsSet = set((col) for col in request.args)
        if not ExtraParamsIsValid(requestArgsSet):
            return omitError(ErrorMsg=repr(set((col) for col in request.args))), 400

        try:
            self.dataDict = request.get_json()
            request.dataDict = self.dataDict[__head__]
            add_argument(_reqparse, field_inputs)
            self.args = _reqparse.parse_args()
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            if error == type(BadRequest):
                return omitError(ErrorMsg='maybe json format error'), 400

            return omitError(ErrorMsg='{}'.format(repr(error.args))), 400


        try:
            checkInputIsValid(self.args)
        except Exception as error:
            return error.args


        r = obj.query.filter(obj.id == id).scalar()
        for k, v in self.args.items():
            if v != None :
                setattr(r, k, v)

        db.session.add(r)

        try:
            db.session.flush()
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            if exc.IntegrityError == type(error):
                return omitError('CE_NAME_CONFLICT', repr(error)), 400

            return omitError(ErrorMsg=repr(error)), 400


        self.args[__head__] = {}
        _resource_fields_wrap = {}
        _resource_fields_wrap[__head__] = fields.Nested(resource_fields)

        for col in r.__table__.columns.keys():
            self.args[__head__][col] = getattr(r, col)


        return marshal(self.args, _resource_fields_wrap), 200

    def _put(self, id):
        #task = filter(lambda t: t['id'] == id, admins)
        #data = request.data
        #dataDict = json.loads(data)
        #parser = reqparse.RequestParser()
        #parser.add_argument('login', required=True, type=str, location=['json', 'form', 'values'], help='Rate cannot be converted')
        #args = parser.parse_args()
        #print(data, 'xxx', 'dataDict', self.dataDict, 'xxx', args)
        #print(self.dataDict, 'xxx')
        #if len(task) == 0:
        #    abort(404)
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
                #print(json.loads(args['admingroup'].replace('\'', '"')))
                #print(set((col) for col in json.loads(args['admingroup'].replace('\'', '"')).get('id')))
                #for admingroup_id in json.loads(args['admingroup'].replace('\'', '"')).get('id')
                #rr = UsersMAdminGroup()
                #rr.admingroup_id = admingroup_id
                #rr.user_id = id
                #db.session.add(rr)

                #j = repr(args['admingroup'])
                #j = re.sub(r"{\s*(\w)", r'{"\1', j)
                #j = re.sub(r",\s*(\w)", r',"\1', j)
                #j = re.sub(r"(\w):", r'\1":', j)
                #admingroup = json.loads(j)
                #admingroup = json.loads(args['admingroup'].replace('\'', '"'))
                #admingroup = json.loads(repr(args['admingroup']))
                #admingroup = json.loads(('{"id": "1"}'))
                #print('rr', type(args['admingroup']), type(admingroup), repr(args['admingroup']))
                #admingroup_id = admingroup[0].get('id')
                # JSON requires double quotes for its strings.
                #admingroup_id = json.loads(args['admingroup'].replace('\'', '"')).get('id')
                #if admingroup_id:

                #    #print(rr, 'rr', admingroup_id)
                #    if rr is None:
                #        rr = UsersMAdminGroup()
                #        rr.admingroup_id = admingroup_id
                #        rr.user_id = id
                #        db.session.add(rr)

                #    #print(json.loads(repr(args['admingroup'])).get('id'), 'd')
                #    #setattr(rr, 'user_id', json.loads(repr(args['admingroup'])).get('id'))
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

        requestArgsSet = set((col) for col in request.args)
        if not ExtraParamsIsValid(requestArgsSet):
            return omitError(ErrorMsg=repr(set((col) for col in request.args))), 400

        r = obj.query.filter(obj.id == id).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST', 'user id {} not found'.format(id)), 400

        self.args = {}
        self.args[__head__] = {}
        _resource_fields_wrap = {}
        _resource_fields_wrap[__head__] = fields.Nested(resource_fields)

        for col in r.__table__.columns.keys():
            self.args[__head__][col] = getattr(r, col)

        return marshal(self.args, _resource_fields_wrap), 200

    def delete(self, id):
        requestArgsSet = set((col) for col in request.args)
        if not ExtraParamsIsValid(requestArgsSet):
            return omitError(ErrorMsg=repr(set((col) for col in request.args))), 400

        try:
            ids = request.args.get(__heads__).split(',')
        except Exception as error:
            return omitError(ErrorMsg='param `{}` not found'.format(__heads__)), 400

        for id in ids:
            try:
                id = inputs.natural(id)
            except Exception as error:
                db.session.rollback()
                return omitError(ErrorMsg='user id `{}` not int'.format(id)), 400

            # it could als cascade delete `online` user
            r = obj.query.filter(obj.id == id).scalar()
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

class ObjectIpaddrs(Resource):
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        add_argument(_reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(ObjectIpaddrs, self).__init__()

    def get(self):
        # check the request is validtion,
        # ex: we not allow request arg 'itemsPerPage1'

        validSet = set(field_inputs_wrap.keys())
        requestArgsSet = set(request.dataDictWrap.keys())

        if not ExtraParamsIsValid(requestArgsSet, validSet):
            return omitError(ErrorMsg=repr(requestArgsSet.difference(validSet))), 400

        # one to many
        try:
            self.args = _reqparse.parse_args()
            self.response = dict(marshal(self.args, resource_fields_wrap).items())
            self.args[__heads__] = []

        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            return omitError('CE_INVALID_PARAM', repr(error)), 400

        itemsPerPage = self.response['itemsPerPage']
        page = self.response['page']
        orderBy = getattr(obj, self.response['orderBy'])
        isDesc = getattr(orderBy, 'desc' if self.response['desc'] else 'asc')

        # .order_by(User.login.desc())
        r = obj.query.order_by(isDesc())

        if itemsPerPage is 0:
            r = r.all()
        else:
            r = r.offset(itemsPerPage * (page-1))\
                    .limit(itemsPerPage)\
                    .all()
        for _r in r:
            __r = dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys())
            self.args[__heads__].append(__r)

        self.args['total'] = len(r)

        resource_fields_wrap[__heads__] = fields.List(fields.Nested(resource_fields))
        return marshal(self.args, resource_fields_wrap), 200

    #@marshal_with(task_list_format)
    def post(self):
        try:
            self.dataDict = request.get_json()
            request.dataDict = self.dataDict[__head__]
            add_argument(_reqparse, field_inputs)
            args = _reqparse.parse_args()
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            if error == type(BadRequest):
                return omitError(ErrorMsg='maybe json format error'), 400

            return omitError(ErrorMsg='{}'.format(error.args)), 400

        if db.session.query(obj.id).count() > limit['max']:
            return omitError('CE_EXCEED_LIMIT', 'limit is {}'.format(limit['max'])), 400


        try:
            # now we only support IPv4/IPv6
            args['addr1'] = inputs.is_ipv4_ipv6(args['addr1'],
                    argument=args['ipVersion'])
        except socket.error as error:
            # Not legal
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            return omitError('CE_INVALID_PARAM',
                    '`{}/{}`: {}'.format(args['addr1'], args['ipVersion'], error.args)), 400

        ip = args['addr1']
        ver = args['ipVersion']
        pre = args['addr2']

        try:
            if args['type'] == 'Single':
                # TODO: maybe we limit that could not pass anything in attribute 'addr2'
                pass

            elif args['type'] == 'Range':
                # do the same as below
                pre = inputs.is_ipv4_ipv6(pre, argument=ver)
                # legal
            elif args['type'] == 'Subnet':
                # do the same as below
                if 'IPv4' == ver:
                    #NOTICE: maybe correct user's input?
                    try:
                        ip = inputs.is_cidr(ip, argument=pre)
                    except Exception as error:
                        pre = inputs.is_netmask(pre)

                elif 'IPv6' == ver:
                    pre = inputs.is_ipv6_prefix(ip, argument=pre)
                # legal

        except Exception as error:
            # Not legal
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            return omitError('CE_INVALID_PARAM', '`{}/{}({})`: {}'.\
                    format(ip, pre, ver, error.args)), 400


        r = obj()
        for k, v in args.items():
            if v != None :
                setattr(r, k, v)

        db.session.add(r)

        try:
            db.session.flush()
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            if exc.IntegrityError == type(error):
                return omitError('CE_NAME_CONFLICT', repr(error)), 400

            return omitError(ErrorMsg=repr(error)), 400

        # get id immediately after call commit
        for col in r.__table__.columns.keys():
            args[col] = getattr(r, col)

        args[__head__] = args
        _resource_fields = {}
        _resource_fields[__head__] = fields.Nested(resource_fields)
        return marshal(args, _resource_fields), 200


class ObjectIpaddrsRef(Resource):
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        add_argument(_reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(ObjectIpaddrsRef, self).__init__()

    def get(self):
        # check the request is validtion,
        # ex: we not allow request arg 'itemsPerPage1'

        validSet = set(__heads__, 'refBy')
        requestArgsSet = set(request.dataDictWrap.keys())

        if not ExtraParamsIsValid(requestArgsSet, validSet):
            return omitError(ErrorMsg=repr(requestArgsSet.difference(validSet))), 400

        try:
            self.args = _reqparse.parse_args()
            self.response = dict(marshal(self.args, resource_fields_wrap).items())
            self.args[__heads__] = []

        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            return omitError('CE_INVALID_PARAM', repr(error)), 400

        itemsPerPage = self.response['itemsPerPage']
        page = self.response['page']
        orderBy = getattr(obj, self.response['orderBy'])
        isDesc = getattr(orderBy, 'desc' if self.response['desc'] else 'asc')

        # .order_by(User.login.desc())
        r = obj.query.order_by(isDesc())

        if itemsPerPage is 0:
            r = r.all()
        else:
            r = r.offset(itemsPerPage * (page-1))\
                    .limit(itemsPerPage)\
                    .all()
        for _r in r:
            __r = dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys())
            self.args[__heads__].append(__r)

        self.args['total'] = len(r)

        resource_fields_wrap[__heads__] = fields.List(fields.Nested(resource_fields))
        return marshal(self.args, resource_fields_wrap), 200
