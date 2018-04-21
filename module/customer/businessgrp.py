# -*- coding: utf-8 -*-

# sys
import json
import traceback
import os.path

# flask
from flask import Flask, request
from sqlalchemy import exc

# config
from config.config import _logging, db, platform_model_config
logger = _logging.getLogger(__name__)

# utils / common
from utils import reqparse, Resource, fields, marshal, inputs
from utils.error import omitError
from module.common import _add_argument, GetResource, ExtraParamsIsValid
from module.common import GetResource,\
       GetRequestArgs, GetRequest, ExtraParamsIsValid,\
       SerialGroupOutput, PrepareGroupORM,\
       SerialObjOutput, PrepareObjORM

#
# predefind validate in each column, please ref to MRQ
#
from .model import CustomerBusinesses as obj, CustomerBusinessgrps as grp, \
        CustomerBusinessesBusinessgrps as mapping
from .__init__ import __customer_businessgrp_head__ as __head__, \
        __customer_businessgrp_heads__ as __heads__, \
        __customer_business_head__ as __obj__head__, \
        __customer_business_heads__ as __obj__heads__

#
# our dir structure is just like: module/{modulename}/feature
#
moduleName = os.path.dirname(__file__).rsplit(os.path.sep, 1)[1]
limit = platform_model_config[moduleName][__head__]
max = limit['max']
childrenMax = limit['children']

#
# init validator
#
from .businessgrp_valid import \
    resource_fields, resource_fields_ref, resource_fields_wrap, \
    field_inputs, field_inputs_ref, field_inputs_wrap

class CustomerBusinessgrp(Resource):
    """
        entry point about '/rest/customer/businessgrps/<int:id>'
        when user do below actions:
        getone/put
    """
    def __init__(self):
        pass

    #@marshal_with(task_list_format)
    def put(self, id):
        """
            update one record
        """
        # 1. parsing reqest
        try:
            self.args = GetRequest(__head__, field_inputs)
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        # 2. get orm from db
        r = grp.query.filter(grp.id == id).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST',
                    'id {} not found'.format(id)), 400

        # 3. assign request data to orm
        try:
            r = PrepareGroupORM(r, obj, mapping, __obj__heads__, self.args.items())
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
        data, field = SerialGroupOutput(r, resource_fields=resource_fields)

        return marshal(data, field), 200

    def get(self, id):
        """
            retreive one record
        """
        r = grp.query.filter(grp.id == id).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST', 'id {} not found'.format(id)), 400

        data, field = SerialGroupOutput(r, resource_fields=resource_fields,
                omitKeys=['id', 'name'])

        return marshal(data, field), 200

class CustomerBusinessgrps(Resource):
    """
        entry point about '/rest/customer/businessgrps'
        when user do below actions:
        delete/create/getall
    """
    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        if request.dataDictWrap:
            _add_argument(reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(CustomerBusinessgrps, self).__init__()

    def get(self):
        """Get all data, getall

         @api {get} /rest/customer/businessgrps Read IP Address groups
         @apiVersion 0.0.1
         @apiName GetIpGrp
         @apiVersion 0.0.1
         @apiGroup customer
         @apiPermission registered user

         @apiDescription
         todo validation

         @apiParam {Number=0, 25, 50, 100} [itemsPerPage=25] items for each request.
         @apiParam {Number} [page=1] page you want to request from, start with 1.
         @apiParam {String="name", "description"} [orderBy=name] the items order by column you specified.
         @apiParam {String="true", "false"} [desc=false] the items order by descending or asceding order.


         @apiExample Example usage:
         curl -i http://localhost/rest/customer/businessgrps?itemsPerPage=50&page=1&orderBy=name&desc=true

         @apiSuccess {Number}   total         total items for pagination.
         @apiSuccess {String}   orderBy       the items order by column you specified.
         @apiSuccess {Number}   page          page you want to request from, start with 1.
         @apiSuccess {Number}   itemsPerPage  items for each request.
         @apiSuccess {String}   desc          the items order by descending or asceding order.
         @apiSuccess {Customer[]} businessgrps       List of IP Addresses.
         @apiSuccess {String}   businessgrps.addr1 1st IP Address.
         @apiSuccess {String}   businessgrps.addr2 2ed IP Address.
         @apiSuccess {String}   businessgrps.description this items's description.
         @apiSuccess {Number}   businessgrps.id index in database.
         @apiSuccess {String}   businessgrps.ipVersion IP Address version.
         @apiSuccess {String}   businessgrps.name items uniq name for record.
         @apiSuccess {String}   businessgrps.type IP Address type, the possible values are 'Single', 'Range', 'Subnet'.

         @apiError CE_INVALID_PARAM invalid parameter
         @api {get} /rest/customer/businessgrps
         @apiErrorExample {json} we use invalid parameter pages
            curl -i http://localhost/rest/customer/businessgrps?pages=1
            ================================================
             HTTP/1.0 400 BAD REQUEST
            {
                "errorId": 2001,
                "message": "{'pages'}"
            }
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
            # FIXME:
            # when i assign field_inputs['name']['required'] to True,
            # it could through below error:
            # ValueError: [name]: (name Valid Error) Missing required parameter
            # in dataDict
            # but i have no idea what it happen.
            if os.environ.get('EVN'):
                # in unit test
                field_inputs['name']['required'] = False
                logger.warning('now we are in unit test mode, turn off'\
                               ' field_inputs[\'name\'][\'required\']'\
                               ' but 1st run is ok :(')

            orgArgs, self.args = GetRequestArgs(None, field_inputs_wrap,
                    dict((col, request.args.get(col)) for col in request.args))

            # get default value
            self.response = dict(marshal(self.args, resource_fields_wrap).items())

            self.args[__heads__] = []
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        itemsPerPage = self.response['itemsPerPage']
        page = self.response['page']
        orderBy = getattr(grp, self.response['orderBy'])
        isDesc = getattr(orderBy, 'desc' if self.response['desc'] else 'asc')

        r = grp.query.order_by(isDesc())
        _r = r.all()
        self.args['total'] = len(_r)

        if itemsPerPage is not 0:
            _r = r.offset(itemsPerPage * (page-1))\
                    .limit(itemsPerPage)\
                    .all()
        r = _r

        # 2. export to user
        data, field = SerialGroupOutput(r, resource_fields=resource_fields,
                omitKeys=['id', 'name'])
        self.args[__heads__] = data

        _resource_fields_wrap = resource_fields_wrap.copy()
        _resource_fields_wrap[__heads__] = fields.List(fields.Nested(field))

        return marshal(self.args, _resource_fields_wrap), 200

    #@marshal_with(task_list_format)
    def post(self):
        """Create new
        """
        # 1. parsing reqest
        try:
            orgArgs, self.args = GetRequestArgs(__head__, field_inputs)
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400


        # 2. validate follows spec
        if db.session.query(grp.id).count() > max:
            return omitError('CE_EXCEED_LIMIT', 'limit is {}'.format(max)), 400

        if len(self.args[__obj__heads__]) > childrenMax:
            return omitError('CE_EXCEED_LIMIT', 'limit is {}'.format(childrenMax)), 400

        # 3. assign request data to orm
        r = grp()
        try:
            r = PrepareGroupORM(r, obj, mapping, __obj__heads__, self.args.items())
        except Exception as error:
            return omitError(ErrorMsg=repr(error)), 400

        # 4. commit to save
        try:
            db.session.add(r)
            db.session.flush()
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            if exc.IntegrityError == type(error):
                return omitError('CE_NAME_CONFLICT', repr(error)), 400

            return omitError(ErrorMsg=repr(error)), 400

        # 5. return all data to user
        data, field = SerialGroupOutput(r, resource_fields=resource_fields)

        return marshal(data, field), 200


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
                db.session.rollback()
                return omitError(ErrorMsg='user id `{}` not int'.format(id)), 400

            # it could als cascade delete `online` user
            r = grp.query.filter(grp.id == id).scalar()
            if r is None:
                db.session.rollback()
                return omitError('CE_NOT_EXIST',
                        'id {} not found'.format(id)), 400

            db.session.delete(r)

        try:
            db.session.flush()
            db.session.commit()
        except Exception as error:
            logger.warning('session commit error(%s)', error)
            db.session.rollback()
            return omitError(ErrorMsg=repr(error)), 400

        return '', 204
        #return '', 200





class CustomerBusinessgrpRef(Resource):
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        add_argument(_reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(CustomerBusinessgrpRef, self).__init__()

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

        _resource_fields_wrap[__heads__] = {}
        _resource_fields_wrap[__heads__] = fields.List(fields.Nested(resource_fields))
        return marshal(self.args, _resource_fields_wrap), 200
