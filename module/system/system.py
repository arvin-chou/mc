# -*- coding: utf-8 -*-

import os
import json
import traceback
from datetime import datetime

from flask import Flask, request, Response, jsonify, g, session
from utils import reqparse, Resource, fields, marshal, inputs
from utils.error import omitError
from config.config import _logging, db, platform_model_config

from module.common import field_inputs_wrap_head
from module.common import _add_argument, GetResource, ExtraParamsIsValid
from module.common import GetResource,\
       GetRequestArgs, GetRequest, ExtraParamsIsValid,\
       SerialGroupOutput, PrepareGroupORM,\
       SerialObjOutput, PrepareObjORM, \
       GetTwoLayerRequestArgs

from module.user.users_valid import \
    resource_fields, resource_fields_wrap, \
    field_inputs, field_inputs_wrap,\
    field_inputs_post, resource_fields_post

#
# predefind validate in each column, please ref to MRQ
#
from module.user.model import Users as obj
#from schema.usersmadmingroup import UsersMAdminGroup
#from schema.admingroup import AdminGroup

from .__init__ import \
        __user_admin_head__ as __head__, \
        __user_admin_heads__ as __heads__
      
logger = _logging.getLogger(__name__)

# our dir structure is just like: module/{modulename}/feature
moduleName = os.path.dirname(__file__).rsplit(os.path.sep, 1)[1]
limit = platform_model_config[moduleName][__head__]
max = limit['max']

# TODO: use permission table
superuser = "test@gmail.com"

def check_permission(reqiured_user, allowed_user):
    # TODO: raise custome error
    #if self.args['login'] != r.login and r.login != superuser:
    if reqiured_user != allowed_user and reqiured_user != superuser:
        raise RuntimeError("permission deny, not change others account")



class Admin(Resource):
    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        if request.dataDictWrap:
            _add_argument(reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(Admin, self).__init__()

    #@marshal_with(task_list_format)
    def put(self, id):
        """ update one item
        """
        # 1. parsing reqest
        try:
            orgArgs, self.args = GetTwoLayerRequestArgs(field_inputs_wrap_head, field_inputs_post)

        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400


        # 2. get orm from db
        r = obj.query.filter(obj.id == id, obj.isdel == False).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST',
                    'id {} not found'.format(id)), 400

        # 3. assign request data to orm
        try:
            t = datetime.utcnow()
            if not self.args['passHash']:
                self.args['passHash'] = r.passHash

            # not allow others change expect itself
            # TODO: raise custome error
            check_permission(self.args['login'], r.login)

            # not allow change login name
            self.args['login'] = r.login

            r = PrepareObjORM(r, self.args.items())
            r.mtime = t;


        except Exception as error:
            if RuntimeError == type(error):
                return omitError('CE_UNAUTHORIZED', repr(error)), 400

            return omitError(ErrorMsg=repr(error)), 400

        # 4. commit to save
        try:
            db.session.merge(r)
            db.session.flush()
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            if exc.IntegrityError == type(error):
                return omitError('CE_NAME_CONFLICT', repr(error)), 400

            return omitError(ErrorMsg=repr(error)), 400

        # 5. return all data to user
        _resource_fields_post = resource_fields_post.copy() 
        _resource_fields_post.pop('access_token', None)
        out = SerialObjOutput(r, objname=field_inputs_wrap_head,
                resource_fields=_resource_fields_post), 200

        next(iter(out))['type'] = 'system'
        next(iter(out))['subtype'] = 'regist'

        return out


        #try:
        #    args = _reqparse.parse_args()
        #except Exception as error:
        #    logger.debug('traceback.format_exc(%s)', traceback.format_exc())
        #    message['message'] = ' '.join(error.args)
        #    return message, 400

        ##task = {}
        ##print(args, 'xxxx')
        ##r = User.query.filter(
        ##        User.id == id).options(lazyload('AdminGroup').first()
        ## one to many
        #r = UsersMAdminGroup.query.filter(
        #        UsersMAdminGroup.user_id == id).all()
        ##print(_r.user_obj.login, 'xxxx')
        ##r = User.query.filter(
        ##        User.id == id).first()

        ##rr = UsersMAdminGroup.query.filter(
        ##        UsersMAdminGroup.user_id == id).all()

        #if len(r) is 0:
        #    message['message'] = 'user id {} not found'.format(id)
        #    return message, 400

        #else:
        #    for k, v in args.items():
        #        if v != None :
        #            if k == 'admingroup':
        #                continue

        #            #print(k, v, 'v', type(v) is dict, type(v))
        #            setattr(r[0].user_obj, k, v)

        #            #data = json.loads(repr(v))
        #    db.session.add(r[0].user_obj)

        #    # update foreign table
        ## delete all mapping
        #if args['admingroup']:
        #    #print("args['admingroup']",
        #    #        json.loads(args['admingroup'][1].replace('\'', '"')))
        #    try:

        #        for _r in r:
        #            # 1. delete all
        #            db.session.delete(_r)

        #        db.session.flush()

        #        for entity in args['admingroup']:
        #            # 2. re-add it
        #            rr = UsersMAdminGroup()
        #            rr.admingroup_id = json.loads((entity.replace('\'', '"'))).get('id')
        #            rr.user_id = id
        #            db.session.add(rr)
        #        
        #    except Exception as error:
        #        # for ambiguous
        #        #(TypeError, ValueError) as err:
        #        logger.debug('impossible that parsing json %s error(%s)',
        #                args['admingroup'], error)
        #        pass
        ##return message, 400

        ##db.session.commit()
        #try:
        #    db.session.commit()
        #except Exception as error:
        #    logger.warning('session commit error(%s)', error)
        #    db.session.rollback()
        #    return message, 400

        ##print(dict((k, v['type']) for k,v in field_inputs.items()))
        ## http://stackoverflow.com/questions/7389759/memory-efficient-built-in-sqlalchemy-iterator-generator
        ##args['admingroup'] = dict(('id', getattr(_r,'id')) for _r in rr)
        ##r = UsersMAdminGroup.query.filter(UsersMAdminGroup.user_id == id) \
        ##    .with_entities(UsersMAdminGroup.admingroup_id).all()
        ##r = UsersMAdminGroup.query.filter(
        ##        UsersMAdminGroup.user_id == id).with_entities(UsersMAdminGroup.user_id,
        ##                UsersMAdminGroup.admingroup_id).all()
        #r = UsersMAdminGroup.query.filter(
        #        UsersMAdminGroup.user_id == id).all()

        #for col in r[0].user_obj.__table__.columns.keys():
        #    args[col] = getattr(r[0].user_obj, col)

        #args['admingroup'] = [];
        #for _r in r:
        #    args['admingroup'].append({'id': getattr(_r, 'admingroup_id')})

        ## http://stackoverflow.com/questions/15261149/sqlalchemy-how-is-it-that-a-comma-determines-if-a-query-returns-a-string-or-a-t
        ##for _r, in r:
        ##    args['admingroup'].append({'id': _r})
        #    #args['admingroup'].append( \
        #    #    dict((col, getattr(_r, col))
        #    #            for col in _r.__table__.columns.keys() if col is not 'id'))
        #    #print(dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys()))
        #    #print(dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys() if col is not 'id'))


        ##return {'task': 'Hello world'}, 201, {'Etag': 'some-opaque-string'}

        ##return message, 200
        #return marshal(args, resource_fields), 200
        ## 204 no content
        ##return message, 204

    def get(self, id):
        """Get all data, getall
        """
        # check the request is validtion,
        # ex: we not allow request arg 'itemsPerPage1'

        validSet = set(field_inputs_wrap.keys())
        requestArgsSet = set(request.dataDictWrap.keys())

        if not ExtraParamsIsValid(requestArgsSet, validSet):
            return omitError(ErrorMsg=repr(requestArgsSet.difference(validSet))), 400

        # one to many
        # 1. parsing reqest
        try:
            for k, v in field_inputs.items():
                field_inputs[k]['required'] = False

            orgArgs, self.args = GetRequestArgs(None, field_inputs_wrap,
                    dict((col, request.args.get(col)) for col in request.args))
            # get default value
            # print(self.args, 'self.args', resource_fields_wrap)
            self.response = dict(marshal(self.args, resource_fields_wrap).items())

            self.args[__heads__] = []
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        if not hasattr(g, 'user'):
            return omitError('CE_NOT_EXIST', 'not login yet'), 400

        r = g.user
        if r is None:
            return omitError('CE_NOT_EXIST'), 400

        # 1.1 check permission
        if r.id != id:
             return omitError('CE_UNAUTHORIZED', 'id not match'), 400

        # 2. export to user
        _r = dict((col, getattr(r, col)) for col in r.__table__.columns.keys())
        self.args[field_inputs_wrap_head] = _r


        _resource_fields = resource_fields.copy()
        _resource_fields_wrap = resource_fields_wrap.copy()
        for col in resource_fields_wrap:
            if col not in ['type', 'subtype']:
                _resource_fields_wrap.pop(col, None) 

        _resource_fields.pop('access_token', None)
        _resource_fields_wrap[field_inputs_wrap_head] = (fields.Nested(_resource_fields))
        self.args['type'] = "system"
        self.args['subtype'] = "regist"
        return marshal(self.args, _resource_fields_wrap), 200

        ## one to many
        #try:
        #    self.args = _reqparse.parse_args()
        #except Exception as error:
        #    logger.debug('traceback.format_exc(%s)', traceback.format_exc())
        #    message['message'] = ' '.join(error.args)
        #    return message, 400

        #r = User.query.filter(User.id == id).scalar()

        #if r is None:
        #    message['message'] = 'user id {} not found'.format(id)
        #    return message, 400

        #for col in r.__table__.columns.keys():
        #    self.args[col] = getattr(r, col)

        #self.args[AdminGroup.__tablename__] = r.admingroup

        #return marshal(self.args, resource_fields), 200


class Admins(Resource):
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        if request.dataDictWrap:
            _add_argument(reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(Admins, self).__init__()

    def get(self):
        """Get all data, getall
        """
        # check the request is validtion,
        # ex: we not allow request arg 'itemsPerPage1'

        validSet = set(field_inputs_wrap.keys())
        requestArgsSet = set(request.dataDictWrap.keys())

        if not ExtraParamsIsValid(requestArgsSet, validSet):
            return omitError(ErrorMsg=repr(requestArgsSet.difference(validSet))), 400

        if not hasattr(g, 'user'):
            return omitError('CE_NOT_EXIST', 'not login yet'), 400

        r = g.user
        if r is None:
            return omitError('CE_NOT_EXIST'), 400

        if r.login != superuser:
            return omitError('CE_UNAUTHORIZED', 'permission deny'), 400


        # one to many
        # 1. parsing reqest
        try:
            for k, v in field_inputs.items():
                field_inputs[k]['required'] = False

            orgArgs, self.args = GetRequestArgs(None, field_inputs_wrap,
                    dict((col, request.args.get(col)) for col in request.args))
            # get default value
            # print(self.args, 'self.args', resource_fields_wrap)
            self.response = dict(marshal(self.args, resource_fields_wrap).items())

            self.args[field_inputs_wrap_head] = []
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        itemsPerPage = self.response['itemsPerPage']
        page = self.response['page']
        orderBy = getattr(obj, self.response['orderBy'])
        isDesc = getattr(orderBy, 'desc' if self.response['desc'] else 'asc')

        r = obj.query.filter(obj.isdel == False).order_by(isDesc())
        _r = r.all()
        self.args['total'] = len(_r)

        if itemsPerPage is not 0:
            _r = r.offset(itemsPerPage * (page-1))\
                    .limit(itemsPerPage)\
                    .all()

        r = _r
        # 2. export to user
        for _r in r:
            __r = dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys())
            self.args[field_inputs_wrap_head].append(__r)


        _resource_fields = resource_fields.copy()
        _resource_fields_wrap = resource_fields_wrap.copy()
        _resource_fields_wrap[field_inputs_wrap_head] = fields.List(fields.Nested(_resource_fields))
        _resource_fields.pop('access_token', None)
        self.args['type'] = "system"
        self.args['subtype'] = "regist"
        return marshal(self.args, _resource_fields_wrap), 200

        # one to many
        #try:
        #    self.args = _reqparse.parse_args()
        #    self.response = dict(marshal(self.args, resource_fields_wrap).items())
        #    self.args[__heads__] = []
        #except Exception as error:
        #    logger.debug('traceback.format_exc(%s)', traceback.format_exc())
        #    message['message'] = ' '.join(error.args)
        #    return message, 400

        #itemsPerPage = self.response['itemsPerPage']
        #page = self.response['page'] - 1
        #orderBy = getattr(User, self.response['orderBy'])
        #isDesc = getattr(orderBy, 'desc' if self.response['desc'] else 'asc')


        #r = User.query.order_by(isDesc())

        #if itemsPerPage is 0:
        #    r = r.all()
        #else:
        #    # .order_by(User.login.desc())
        #    r = r.offset(itemsPerPage * page)\
        #            .limit(itemsPerPage)\
        #            .all()
        #for _r in r:
        #    __r = dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys())
        #    __r['admingroup'] = _r.admingroup
        #    self.args[__heads__].append(__r)

        #self.args['total'] = len(User.query.all())

        #resource_fields_wrap[__heads__] = fields.List(fields.Nested(resource_fields))
        #return marshal(self.args, resource_fields_wrap), 200

    def delete(self):
        """multi delete
        """
        try:
            ids = request.args.get(__heads__).split(',')
        except Exception as error:
            return omitError(ErrorMsg='param `{}` not found'.format(__heads__)), 400

        # TODO: use function
        if not hasattr(g, 'user'):
            return omitError('CE_NOT_EXIST', 'not login yet'), 400

        r = g.user
        if r is None:
            return omitError('CE_NOT_EXIST'), 400

        if r.login != superuser:
            return omitError('CE_UNAUTHORIZED', 'permission deny'), 400


        for id in ids:
            try:
                id = inputs.natural(id)
            except Exception as error:
                return omitError(ErrorMsg='id `{}` not int'.format(id)), 400

            # it could als cascade delete `online` user
            r = obj.query.filter(obj.id == id, obj.isdel == False).scalar()
            if r is None:
                return omitError('CE_NOT_EXIST',
                        'id {} not found'.format(id)), 400

        _r = []
        for id in ids:
            id = inputs.natural(id)

            # it could als cascade delete `online` user
            r = obj.query.filter(obj.id == id, obj.isdel == False).scalar()
            r.isdel = True
            _r.append(r)


        try:
            for v in _r:
                db.session.merge(v)

            db.session.flush()
            db.session.commit()
        except Exception as error:
            logger.warning('session commit error(%s)', error)
            db.session.rollback()
            return omitError(ErrorMsg=repr(error)), 400

        return '', 204
        #try:
        #    ids = request.args.get(__heads__).split(',')
        #except Exception as error:
        #    return omitError(ErrorMsg='param `{}` not found'.format(__heads__)), 400

        #for id in ids:
        #    try:
        #        id = inputs.natural(id)
        #    except Exception as error:
        #        return omitError(ErrorMsg='user id `{}` not int'.format(id)), 400

        #    # it could als cascade delete `online` user
        #    r = User.query.filter(User.id == id).first()
        #    if r is None:
        #        db.session.rollback()
        #        return omitError('CE_NOT_EXIST',
        #                'admin id {} not found'.format(id)), 400

        #    db.session.delete(r)

        #try:
        #    db.session.flush()
        #    db.session.commit()
        #except Exception as error:
        #    logger.warning('session commit error(%s)', error)
        #    db.session.rollback()
        #    return message, 400

        #return message, 204
        ## one to many
        #try:
        #    self.args = _reqparse.parse_args()
        #except Exception as error:
        #    logger.debug('traceback.format_exc(%s)', traceback.format_exc())
        #    message['message'] = ' '.join(error.args)
        #    return message, 400

        #r = User.query.filter(User.id == id).scalar()

        #if r is None:
        #    message['message'] = 'user id {} not found'.format(id)
        #    return message, 400

        #for col in r.__table__.columns.keys():
        #    self.args[col] = getattr(r, col)

        #self.args[AdminGroup.__tablename__] = r.admingroup

        #return marshal(self.args, resource_fields), 200

    def post(self):
        """regist local user

        @api {post} /rest/admins regist local account
        @apiVersion 0.0.5
        @apiName RegistOneUser
        @apiGroup account
        @apiPermission registered user

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo validation<br />
        todo error / success return code in api

        @apiParam {Object[]}        user         user object
        @apiParam {String{..254}}   user.name    user name for display
        @apiParam {String{..254}}   user.login   user email for login
        @apiParam {String{..254}}   user.passHash user password encode with sha1
        @apiExample {curl} Example usage:

        curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "
        {  
            'data':{  
                'id':2,
                'login':'testlogin@gmail.com',
                'passHash':'c4f9375f9834b4e7f0a528cc65c055702bf5f24a',
                'name':'test'
            },
            'type':'system',
            'subtype':'regist'
        }
        " http://localhost/rest/admins
        """

        # 1. check id exist
        try:
            orgArgs, self.args = GetTwoLayerRequestArgs(field_inputs_wrap_head, field_inputs_post)
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError('CE_INVALID_PARAM', 'not found'), 400

        # 2. validate follows spec
        if db.session.query(obj).filter(obj.isdel == False).count() > max:
            return omitError('CE_EXCEED_LIMIT', 'limit is {}'.format(max)), 400

        # 3 check name unique
        r = obj.query.filter(obj.login == self.args['login'],
                obj.isdel == False).scalar()

        if r is not None:
            return omitError('CE_DATA_DUPLICATE',
                    'login {} is duplicate'.format(self.args['login'])), 400

        r = obj()
        try:
            r = PrepareObjORM(r, self.args.items())

        except Exception as error:
            return omitError(ErrorMsg=repr(error)), 400


        # 4. commit to save
        try:
            db.session.add(r)
            db.session.flush()
            db.session.refresh(r)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            if exc.IntegrityError == type(error):
                return omitError('CE_NAME_CONFLICT', repr(error)), 400

            return omitError(ErrorMsg=repr(error)), 400


        # 5. return all data to user
        _resource_fields_post = resource_fields_post.copy() 
        _resource_fields_post.pop('access_token', None)
        out = SerialObjOutput(r, objname=field_inputs_wrap_head,
                resource_fields=_resource_fields_post), 200

        next(iter(out))[field_inputs_wrap_head].update({'id': r.id})
        next(iter(out))['type'] = 'system'
        next(iter(out))['subtype'] = 'regist'

        return out
