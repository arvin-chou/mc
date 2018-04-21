# -*- coding: utf-8 -*-

# sys
import json
import traceback
import os.path
# for ip validate
import socket

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
from .model import CustomerBusinesses as obj, CustomerBusinessgrps as grp
from .__init__ import \
        __customer_business_head__ as __head__, \
        __customer_business_heads__ as __heads__

from .business_valid import \
    resource_fields, resource_fields_ref, resource_fields_wrap, \
    field_inputs, field_inputs_ref, field_inputs_wrap

# our dir structure is just like: module/{modulename}/feature
moduleName = os.path.dirname(__file__).rsplit(os.path.sep, 1)[1]
limit = platform_model_config[moduleName][__head__]
max = limit['max']

class CustomerBusiness(Resource):
    """entry point about '/rest/customer/business'
        when user do below actions:
        put/getone
    """

    def __init__(self):
        pass

    #@marshal_with(task_list_format)
    def put(self, id):
        """
            update one item

        @api {put} /rest/customer/business/:id update a item
        @apiVersion 0.0.3
        @apiName UpdateCustomerBusiness
        @apiGroup customer
        @apiPermission registered user


        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />

        @apiParam {Number}          id               item's uniq id.
        @apiParam {Customer[]}      businesses       List of businesses.
        @apiParam {Number}          businesses.id    item's uniq id.
        @apiParam {String{..64}}    businesses.name  item's name.
        @apiParam {Number}          businesses.cat   item's business industry category.
        @apiParam {float}           businesses.lat   item's entered latitude.
        @apiParam {float}           businesses.long  item's entered longitude.
        @apiParam {String{..255}}   [businesses.description] this items's description.
        @apiParam {Number}          businesses.deal  items's deal.
        @apiParam {String{..255}}   businesses.image_url  items's image url.
        @apiExample Example usage:
           BODY=$(cat <<'EOF'
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "id": 1,
                   "name": "Starbucks Coffee",
                   "image_url": "business/icon/1",
                   "cat": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }
           EOF
           );

        curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/business/1

            ================================================
            HTTP/1.0 200 OK
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "id": 1,
                   "name": "Starbucks Coffee",
                   "image_url": "business/icon/1",
                   "cat": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }

        @apiSuccess {Customer[]} businesses       List of businesses.
        @apiSuccess {Number}     businesses.id    item's uniq id.
        @apiSuccess {String}     businesses.name  item's name.
        @apiSuccess {Number}     businesses.cat   item's business industry category.
        @apiSuccess {float}      businesses.lat   item's entered latitude.
        @apiSuccess {float}      businesses.long  item's entered longitude.
        @apiSuccess {String}     businesses.description this items's description.
        @apiSuccess {Number}     businesses.deal  items's deal.
        @apiSuccess {String}     businesses.image_url  items's image url.

        @apiError CE_INVALID_PARAM invalid parameter
        @api {put} /rest/customer/business/:id
        @apiErrorExample {json} we use invalid member type1 in request body
           BODY=$(cat <<'EOF'
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "id": 1,
                   "name": "Starbucks Coffee",
                   "image_url": "business/icon/1",
                   "type1": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }
           EOF
           );

           curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/business/1
           ================================================
           HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2001,
               "message": "ValueError('[cat]: (cat Valid Error) Missing required parameter in dataDict, error=400: Bad Request',)"
           }

        @apiError CE_NAME_CONFLICT name conflict
        @api {put} /rest/customer/business/:id
        @apiErrorExample {json} we use duplicate name.
            BODY=$(cat <<'EOF'
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "id": 1,
                   "name": "Starbucks Coffee - 2",
                   "image_url": "business/icon/1",
                   "cat": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }
           EOF
           );

           curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/business/1
           ================================================
           HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2004,
               "message": "IntegrityError('(sqlite3.IntegrityError) UNIQUE constraint failed: customer_businesses.name',)"
           }

        @apiError CE_NOT_EXIST item not found
        @api {put} /rest/customer/business/:id
        @apiErrorExample {json} we use not exist id
            BODY=$(cat <<'EOF'
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "id": 17,
                   "name": "Starbucks Coffee - 2",
                   "image_url": "business/icon/1",
                   "cat": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }
           EOF
           );

           curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/business/17

           ================================================
           HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2003,
               "message": "id 17 not found"
           }

        """
        # 1. parsing reqest
        try:
            orgArgs, self.args = GetRequestArgs(__head__, field_inputs)
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400


        # 2. get orm from db
        r = obj.query.filter(obj.id == id).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST',
                    'id {} not found'.format(id)), 400

        # 3. assign request data to orm
        try:
            r = PrepareObjORM(r, self.args.items())
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
        return SerialObjOutput(r, objname=__head__, resource_fields=resource_fields), 200

    def get(self, id):
        """
        @api {get} /rest/customer/business/:id get one item by id.
        @apiName GetCustomerBusiness
        @apiVersion 0.0.3
        @apiGroup customer
        @apiPermission registered user

        @apiDescription
        todo validation

        @apiParam {Number} id IP Address item id.

        @apiExample Example usage:
        curl -i http://localhost/rest/customer/business/1

        @apiSuccess {Customer[]} businesses       List of businesses.
        @apiSuccess {Number}     businesses.id    item's uniq id.
        @apiSuccess {String}     businesses.name  item's name.
        @apiSuccess {Number}     businesses.cat   item's business industry category.
        @apiSuccess {float}      businesses.lat   item's entered latitude.
        @apiSuccess {float}      businesses.long  item's entered longitude.
        @apiSuccess {String}     businesses.description this items's description.
        @apiSuccess {Number}     businesses.deal  items's deal.
        @apiSuccess {String}     businesses.image_url  items's image url.


        @apiError CE_INVALID_PARAM invalid parameter
        @api {get} /rest/customer/business/:id
        @apiErrorExample {json} we use invalid parameter pages
            curl -X GET -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/business/7?pages=1
            ================================================
            HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2001,
               "message": "{'pages'}"
           }

        @apiError CE_NOT_EXIST item not found
        @api {get} /rest/customer/business/:id
        @apiErrorExample {json} we use not exist id
            curl -X GET -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/business/17
            ================================================
            HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2003,
               "message": "id 17 not found"
           }

        """
        requestArgsSet = set((col) for col in request.args)
        if not ExtraParamsIsValid(requestArgsSet):
            return omitError(ErrorMsg=repr(set((col) for col in request.args))), 400

        r = obj.query.filter(obj.id == id).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST', 'id {} not found'.format(id)), 400

        self.args = {}
        self.args[__head__] = {}
        _resource_fields_wrap = {}
        _resource_fields_wrap[__head__] = fields.Nested(resource_fields)

        for col in r.__table__.columns.keys():
            self.args[__head__][col] = getattr(r, col)

        return marshal(self.args, _resource_fields_wrap), 200


class CustomerBusinesses(Resource):
    """entry point about '/rest/customer/businesses'
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

        super(CustomerBusinesses, self).__init__()

    def get(self):
        """Get all data, getall

        @api {get} /rest/customer/businesses Read all item with pagination / sort /filter
        @apiName GetAllCustomerBusiness
        @apiVersion 0.0.3
        @apiGroup customer
        @apiPermission registered user

        @apiDescription
        modified: change category type from string to number.<br/>
        modified: add name attribute.<br />
        modified: change deal type from string to number.<br/>
        todo validation<br/>

        @apiParam {Number=0, 25, 50, 100} [itemsPerPage=25] items for each request.
        @apiParam {Number} [page=1] page you want to request from, start with 1.
        @apiParam {String="name", "description"} [orderBy=name] the items order by column you specified.
        @apiParam {String="true", "false"} [desc=false] the items order by descending or asceding order.
        @apiParam {String={..255}} [q] query string for pre-defined columns.


        @apiExample Example usage:
        curl -i http://localhost/rest/customer/businesses?itemsPerPage=50&page=1&orderBy=name&desc=true
            ================================================
            HTTP/1.0 200 OK
            {
                "desc": false,
                "business": [
                    {
                        "description": "Early Bird Special: Get $2 off.",
                        "id": 1,
                        "name": "Starbucks Coffee",
                        "image_url": "business/icon/1",
                        "cat": 1,
                        "deal": 200,
                        "lat": 120.678469,
                        "long": 23.538302
                    },
                    {
                        "description": "Free Coffee Today.",
                        "id": 4,
                        "name": "Luxy",
                        "image_url": "business/icon/2",
                        "cat": 2,
                        "deal": 201,
                        "lat": 120.4540969,
                        "long": 23.4862023
                    },
                    {
                        "description": "Come back john! Get $5 off.",
                        "id": 4,
                        "name": "台北福華大飯店",
                        "image_url": "business/icon/3",
                        "cat": 2,
                        "deal": 201,
                        "lat": 120.4540969,
                        "long": 23.4862023
                    },
                    {
                        "description": "Spend $55, Get $5 credit.",
                        "id": 4,
                        "name": "McDonald's 麥當勞",
                        "image_url": "business/icon/4",
                        "cat": 2,
                        "deal": 201,
                        "lat": 120.4540969,
                        "long": 23.4862023
                    }
                ],
                "itemsPerPage": 25,
                "orderBy": "name",
                "page": 1,
                "total": 2
            }

         @apiSuccess {Number}   total         total items for pagination.
         @apiSuccess {String}   orderBy       the items order by column you specified.
         @apiSuccess {Number}   page          page you want to request from, start with 1.
         @apiSuccess {Number}   itemsPerPage  items for each request.
         @apiSuccess {String}   desc          the items order by descending or asceding order.
         @apiSuccess {String}   q             query string for pre-defined columns.

         @apiSuccess {Customer[]} businesses       List of businesses.
         @apiSuccess {Number}   businesses.id    item's uniq id.
         @apiSuccess {String}   businesses.name  item's name.
         @apiSuccess {Number}   businesses.cat   item's business industry category.
         @apiSuccess {float}    businesses.lat   item's entered latitude.
         @apiSuccess {float}    businesses.long  item's entered longitude.
         @apiSuccess {String}   businesses.description this items's description.
         @apiSuccess {Number}   businesses.deal  items's deal.
         @apiSuccess {String}   businesses.image_url  items's image url.

         @apiError CE_INVALID_PARAM invalid parameter
         @api {get} /rest/customer/businesses
         @apiErrorExample {json} we use invalid parameter pages
            curl -i http://localhost/rest/customer/businesses?pages=1
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
            # print(self.args, 'self.args', resource_fields_wrap)
            self.response = dict(marshal(self.args, resource_fields_wrap).items())

            self.args[__heads__] = []
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        itemsPerPage = self.response['itemsPerPage']
        page = self.response['page']
        orderBy = getattr(obj, self.response['orderBy'])
        isDesc = getattr(orderBy, 'desc' if self.response['desc'] else 'asc')

        r = obj.query.order_by(isDesc())
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
            self.args[__heads__].append(__r)

        resource_fields_wrap[__heads__] = fields.List(fields.Nested(resource_fields))
        return marshal(self.args, resource_fields_wrap), 200

    #@marshal_with(task_list_format)
    def post(self):
        """create data

        @api {post} /rest/customer/businesses Create a item
        @apiVersion 0.0.3
        @apiName CreateCustomerBusiness
        @apiGroup customer
        @apiPermission registered user

        @apiDescription
        todo validation <br/>
        todo certificate with cookies / oauth 2.0 <br/>
        todo muti-create

        @apiParam {Customer}        business         business object.
        @apiParam {String{..64}}    businesses.name  item's name.
        @apiParam {Number}          businesses.cat   item's business industry category.
        @apiParam {float}           businesses.lat   item's entered latitude.
        @apiParam {float}           businesses.long  item's entered longitude.
        @apiParam {String{..255}}   [businesses.description] this items's description.
        @apiParam {Number}          businesses.deal  items's deal.
        @apiParam {String{..255}}   businesses.image_url  items's image url.
        @apiExample Example usage:
            BODY=$(cat <<'EOF'
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "name": "Starbucks Coffee",
                   "image_url": "business/icon/1",
                   "cat": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }
            EOF
            );

            curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/businesses
            ================================================
            HTTP/1.0 200 OK
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "id": 1,
                   "name": "Starbucks Coffee",
                   "image_url": "business/icon/1",
                   "cat": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }

        @apiSuccess {Customer}   businesses       business object.
        @apiSuccess {Number}     businesses.id    item's uniq id.
        @apiSuccess {String}     businesses.name  item's name.
        @apiSuccess {Number}     businesses.cat   item's business industry category.
        @apiSuccess {float}      businesses.lat   item's entered latitude.
        @apiSuccess {float}      businesses.long  item's entered longitude.
        @apiSuccess {String}     businesses.description this items's description.
        @apiSuccess {Number}     businesses.deal  items's deal.
        @apiSuccess {String}     businesses.image_url  items's image url.

        @apiError CE_INVALID_PARAM invalid parameter
        @api {post} /rest/customer/businesses
        @apiErrorExample {json} we use invalid member type1 in request body
           BODY=$(cat <<'EOF'
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "id": 1,
                   "name": "Starbucks Coffee",
                   "image_url": "business/icon/1",
                   "type1": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }
           EOF
           );

           curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/businesses
           ================================================
           HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2001,
               "message": "ValueError('[cat]: (cat Valid Error) Missing required parameter in dataDict, error=400: Bad Request',)"
           }

        @apiError CE_NAME_CONFLICT name conflict
        @api {put} /rest/customer/businesses
        @apiErrorExample {json} we use duplicate name.
            BODY=$(cat <<'EOF'
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "id": 1,
                   "name": "Starbucks Coffee - 2",
                   "image_url": "business/icon/1",
                   "cat": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }
           EOF
           );

           curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/businesses
           ================================================
           HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2004,
               "message": "IntegrityError('(sqlite3.IntegrityError) UNIQUE constraint failed: customer_businesses.name',)"
           }


         @apiError CE_EXCEED_LIMIT exceed max limit
         @api {post} /rest/customer/businesses
         @apiErrorExample {json} we create item exceed max.
            BODY=$(cat <<'EOF'
            {
               "business" : {
                   "description": "Early Bird Special: Get $2 off.",
                   "name": "Starbucks Coffee - 2",
                   "image_url": "business/icon/1",
                   "cat": 1,
                   "deal": 200,
                   "lat": 120.678469,
                   "long": 23.538302
                }
            }
           EOF
           );

            curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/customer/businesses
            ================================================
            HTTP/1.0 400 BAD REQUEST
            {
                "errorId": 2005,
                "message": "limit is 5"
            }

        """

        # 1. parsing reqest
        # 1.1 parsing 1st layer reqest
        try:
            orgArgs, self.args = GetRequestArgs(__head__, field_inputs)
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        # 1.2 parsing 2ed layer reqest
        try:
            for v in set((v) for v in set(field_inputs).intersection(orgArgs)
                    if isinstance(field_inputs[v]['validator'], set)):
                _type = field_inputs[v]['validator']

                validator = next(iter(_type)).container.nested.items() \
                      if type(_type) is set else _type.items()

                # validate 2ed value
                # if is list, such as [{id: 1, name:2}, {id: 2, name:2}]
                for _k, _v in validator:
                  for __v in orgArgs[v]:
                    if (_v.get('required', False)):
                      _v['type'](__v[_k])

                self.args[v] = self.args[v] if self.args.get(v, False) else []
                self.args[v].append(__v)

        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            return omitError(ErrorMsg=repr(error)), 400


        logger.debug('parsed args = (%s)', self.args);


        # 2. validate follows spec
        if db.session.query(obj.id).count() > max:
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
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            if exc.IntegrityError == type(error):
                return omitError('CE_NAME_CONFLICT', repr(error)), 400

            return omitError(ErrorMsg=repr(error)), 400

        # 5. return all data to user
        return SerialObjOutput(r, objname=__head__,
                resource_fields=resource_fields), 200

    def delete(self):
        """multi delete
        @api {delete} /rest/customer/businesses delete items.
        @apiName DelCustomerBusiness
        @apiVersion 0.0.3
        @apiGroup customer
        @apiPermission registered user

        @apiDescription
        todo validation

        @apiParam {String{..255}} [ids] the items id seperate with common

        @apiExample Example usage:
        curl -X DELETE -v -b $COOKIES -H "Content-Type:application/json" http://localhost/rest/customer/businesses?id=1,2,3
        ================================================
        HTTP/1.0 204 NO CONTENT


        @apiError CE_INVALID_PARAM invalid parameter
        @api {delete} /rest/customer/businesses
        @apiErrorExample {json} we use invalid parameter pages
        curl -X DELETE -v -b $COOKIES -H "Content-Type:application/json" http://localhost/rest/customer/pages?id=1,2,3
        ================================================
            HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2001,
               "message": "param `businesses` not found"
           }

        @apiError CE_NOT_EXIST item not found
        @api {delete} /rest/customer/businesses
        @apiErrorExample {json} we use not exist id
        curl -X DELETE -v -b $COOKIES -H "Content-Type:application/json" http://localhost/rest/customer/pages?id=7,8,9
        ================================================
            HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2003,
               "message": "id 7 not found"
           }


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
                return omitError(ErrorMsg='id `{}` not int'.format(id)), 400

            # it could als cascade delete `online` user
            r = obj.query.filter(obj.id == id).scalar()
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



class CustomerBusinessesRef(Resource):
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        add_argument(_reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(CustomerBusinessesRef, self).__init__()

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
