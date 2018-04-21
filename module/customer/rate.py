# -*- coding: utf-8 -*-

# sys
import json
import traceback
import os.path
from datetime import datetime

# flask
from flask import Flask, request
from sqlalchemy import exc

# config
from config.config import _logging, db, platform_model_config
logger = _logging.getLogger(__name__)

# utils / common
from utils import reqparse, Resource, fields, marshal, inputs
from utils.error import omitError
from module.common import field_inputs_wrap_head
from module.common import _add_argument, GetResource, ExtraParamsIsValid
from module.common import GetResource,\
       GetRequestArgs, GetRequest, ExtraParamsIsValid,\
       SerialGroupOutput, PrepareGroupORM,\
       SerialObjOutput, PrepareObjORM, \
       GetTwoLayerRequestArgs

#
# predefind validate in each column, please ref to MRQ
#
from .model import CustomerBusinessRates as obj, \
        CustomerBusinessgrps as grp, \
        CustomerBusinessDetails as detail, \
        CustomerBusinessDeals as deals, \
        CustomerBusinessPics as pics

from module.user.model import Users

from .__init__ import \
        __customer_rate_head__ as __head__, \
        __customer_rate_heads__ as __heads__, \
        __customer_business_detail_head__ as __head_detail__, \
        __customer_business_detail_rates_head__ as __head_detail_rates__, \
        __customer_business_detail_deals_head__ as __head_detail_deals__, \
        __customer_business_detail_images_url_head__ as __head_detail_images_url__,\
        __customer_comment_user_head__ as __head_user__
        #__customer_business_head__ as __head__, \


from .rate_valid import \
    resource_fields, resource_fields_wrap, \
    field_inputs, field_inputs_wrap,\
    field_inputs_post, resource_fields_post


# our dir structure is just like: module/{modulename}/feature
moduleName = os.path.dirname(__file__).rsplit(os.path.sep, 1)[1]
limit = platform_model_config[moduleName][__head__]
max = limit['max']

class CustomerRate(Resource):
    """entry point about '/rest/customer/rate'
    """
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        if request.dataDictWrap:
            _add_argument(reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(CustomerRate, self).__init__()

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
            r = PrepareObjORM(r, self.args.items())
            r.mtime = t;


        except Exception as error:
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
        out = SerialObjOutput(r, objname=field_inputs_wrap_head,
                resource_fields=resource_fields_post), 200

        next(iter(out))[field_inputs_wrap_head].update({'id': id})
        next(iter(out))['type'] = 'business'
        next(iter(out))['subtype'] = 'rate'

        return out



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

        r = obj.query.filter(obj.id == id, obj.isdel == False).scalar()
        if r is None:
            return omitError('CE_NOT_EXIST', 'id {} not found'.format(id)), 400

        # 2. export to user
        _r = dict((col, getattr(r, col)) for col in r.__table__.columns.keys())
        self.args[field_inputs_wrap_head] = _r


        _resource_fields = resource_fields.copy()
        _resource_fields_wrap = resource_fields_wrap.copy()
        for col in resource_fields_wrap:
            if col not in ['type', 'subtype']:
                _resource_fields_wrap.pop(col, None) 

        _resource_fields_wrap[field_inputs_wrap_head] = (fields.Nested(_resource_fields))
        self.args['type'] = "business"
        self.args['subtype'] = "rate"
        return marshal(self.args, _resource_fields_wrap), 200

class CustomerRates(Resource):
    """entry point about '/rest/customer/rates'
        when user do below actions:
        delete/create/getall
    """
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        if request.dataDictWrap:
            _add_argument(reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(CustomerRates, self).__init__()

    def get(self):
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
        self.args['type'] = "business"
        self.args['subtype'] = "rate"
        return marshal(self.args, _resource_fields_wrap), 200

    #@marshal_with(task_list_format)
    def post(self):
        """create data
        """

        # 1. parsing reqest
        # 1.1 parsing 1st layer reqest

        try:
            orgArgs, self.args = GetTwoLayerRequestArgs(field_inputs_wrap_head, field_inputs_post)

        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        # 1.3 check name unique
        r = obj.query.filter(obj.user_id == self.args['user_id'],
                obj.business_id == self.args['business_id'],
                obj.isdel == False).scalar()

        if r is not None:
            return omitError('CE_DATA_DUPLICATE',
                    'user_id {}, business_id {} are duplicate'.format(self.args['user_id'],
                        self.args['business_id'])), 400


        # 2. validate follows spec
        if db.session.query(obj).filter(obj.isdel == False).count() > max:
            return omitError('CE_EXCEED_LIMIT', 'limit is {}'.format(max)), 400


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
        out = SerialObjOutput(r, objname=field_inputs_wrap_head,
                resource_fields=resource_fields_post), 200

        next(iter(out))[field_inputs_wrap_head].update({'id': r.id})
        next(iter(out))['type'] = 'business'
        next(iter(out))['subtype'] = 'rate'

        return out

    def delete(self):
        """multi delete
        """
        try:
            ids = request.args.get(__heads__).split(',')
        except Exception as error:
            return omitError(ErrorMsg='param `{}` not found'.format(__heads__)), 400

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
