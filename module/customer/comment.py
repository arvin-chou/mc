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
from .model import CustomerBusinessComments as obj, \
        CustomerBusinessgrps as grp, \
        CustomerBusinessDetails as detail, \
        CustomerBusinessDeals as deals, \
        CustomerBusinessPics as pics, \
        CustomerBusinessRates as rates

from module.user.model import Users

from .__init__ import \
        __customer_comment_head__ as __head__, \
        __customer_comment_heads__ as __heads__, \
        __customer_business_detail_head__ as __head_detail__, \
        __customer_business_detail_rates_head__ as __head_detail_rates__, \
        __customer_business_detail_deals_head__ as __head_detail_deals__, \
        __customer_business_detail_images_url_head__ as __head_detail_images_url__,\
        __customer_comment_user_head__ as __head_user__
        #__customer_business_head__ as __head__, \


from .comment_valid import \
    resource_fields, resource_fields_user, resource_fields_wrap, \
    field_inputs, field_inputs_user, field_inputs_wrap,\
    field_inputs_post, resource_fields_post


# our dir structure is just like: module/{modulename}/feature
moduleName = os.path.dirname(__file__).rsplit(os.path.sep, 1)[1]
limit = platform_model_config[moduleName][__head__]
max = limit['max']

class CustomerComment(Resource):
    """entry point about '/rest/customer/comment'
    """
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        if request.dataDictWrap:
            _add_argument(reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(CustomerComment, self).__init__()

    def put(self, id):
        """ update one item
        """
        """update comment 

        @api {put} /rest/customer/comment/:id create comment
        @apiVersion 0.0.5
        @apiName UpdateComment
        @apiGroup campaign
        @apiPermission registered user
        @apiParam {Number} id comment id

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiParam {Object}          data        object
        @apiParam {String{..254}}   data.content message's title
        @apiParam {Number}          data.business_id comment belong to the business_id 
        @apiParam {Number}          data.user_id  user who create it
        @apiParam {Number={0..5}}   data.rate    comment's rate
        @apiParam {String}          type         request's type
        @apiParam {String}          subtype      request's subtype
        @apiExample {curl} Example usage:

        curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "
        {  
            "subtype":"comment",
            "type":"business",
            "data":{  
                "content":"Starbucks were all over Singapore and the quality ",
                "business_id":1,
                "user_id":2,
                "rate":1
            }
        }" http://localhost/rest/customer/comment/1

        HTTP/1.0 200 OK
        {  
            "data":{  
                "content":"Starbucks were all over Singapore and the quality ",
                "user_id":1,
                "business_id":1,
                "rate":1,
                "mtime":"2016-08-31 04:16:42.091706",
                "id":2
            },
            "type":"business",
            "subtype":"comment"
        }

        @apiSuccess {Object}          data        object
        @apiSuccess {String{..254}}   data.content message's title
        @apiSuccess {Number}          data.business_id comment belong to the business_id 
        @apiSuccess {Number}          data.user_id  user who create it
        @apiSuccess {Number}          data.id      comment's id
        @apiSuccess {String{..254}}   data.mtime   comment's modify time
        @apiSuccess {Number={0..5}}   data.rate    comment's rate
        @apiSuccess {String}          type         request's type
        @apiSuccess {String}          subtype      request's subtype
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

        # TODO: make sure tranaction
        _r = rates.query.filter(rates.user_id == self.args['user_id'],
                rates.business_id == self.args['business_id'],
                rates.isdel == False).scalar()

        if _r is None:
            return omitError('CE_NOT_EXIST',
                    'user_id {}, business_id {} '.format(self.args['user_id'],
                        self.args['business_id'])), 400

        _r.rate = self.args['rate']


        # 4. commit to save
        try:
            db.session.merge(r)
            db.session.merge(_r)
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
        next(iter(out))[field_inputs_wrap_head].update({'rate':  self.args['rate']})
        next(iter(out))['type'] = 'business'
        next(iter(out))['subtype'] = 'comment'

        return out



    def get(self, id):
        """Get all data, getall

        @api {get} /rest/customer/comment/:id Read all comments under one business
        @apiName GetAllCustomerComments
        @apiVersion 0.0.5
        @apiGroup campaign
        @apiPermission registered user

        @apiParam {Number} id business id

        @apiDescription
        todo validation<br/>
        todo query target<br/>

        @apiParam {Number=0, 25, 50, 100} [itemsPerPage=25] items for each request.
        @apiParam {Number} [page=1] page you want to request from, start with 1.
        @apiParam {String} [orderBy=mtime] the items order by column you specified.
        @apiParam {String="true", "false"} [desc=false] the items order by descending or asceding order.
        @apiParam {String={..254}} [q] query string for pre-defined columns.


        @apiExample {curl} Example usage:
        curl -X GET -H "mTag: xx" -H "Content-Type:application/json" http://localhost/rest/customer/comment/1

        HTTP/1.0 200 OK
        {
            "desc": false,
            "comments": [
                {
                    "user": {
                        "id": 1,
                        "avatar_url": "/user/1/avatar"
                    },
                    "content": "xxxx"
                    "rate": 4
                    "mtime": "2016-05-17 01:40:24"
                }
            ],
            "itemsPerPage": 25,
            "orderBy": "mtime",
            "page": 1,
            "total": 1
        }

        @apiSuccess {Number}   total         total items for pagination.
        @apiSuccess {String}   orderBy       the items order by column you specified.
        @apiSuccess {Number}   page          page you want to request from, start with 1.
        @apiSuccess {Number}   itemsPerPage  items for each request.
        @apiSuccess {String}   desc          the items order by descending or asceding order.

        @apiSuccess {Object[]} data       List of business's comments.
        @apiSuccess {Number}   data.id    item's uniq id.
        @apiSuccess {String}   data.content  item's comment content
        @apiSuccess {Number}   data.rate   item's rate for business item
        @apiSuccess {Number}   data.mtime  items's latest modified time with ISO 8601 format
        @apiSuccess {Object}   data.user   item's author infomation
        @apiSuccess {Number}   data.user.id  item's author id
        @apiSuccess {String}   data.user.avatar_url  item's author avatar

        @apiError CE_INVALID_PARAM invalid parameter
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2001,
            "message": "{'pages'}"
        }

        @apiError CE_NOT_EXIST item not found
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2003,
            "message": "id 1 not found"
        }
        """
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

        r = obj.query.filter(obj.isdel == False, obj.business_id == id).order_by(isDesc())
        _r = r.all()
        self.args['total'] = len(_r)

        if itemsPerPage is not 0:
            _r = r.offset(itemsPerPage * (page-1))\
                    .limit(itemsPerPage)\
                    .all()

        r = _r
        # 2. export to user
        # TODO: link with user
        for _r in r:
            __r = dict((col, getattr(_r, col)) for col in _r.__table__.columns.keys())
            ___r = db.session.query(Users).\
                    filter(_r.user_id == Users.id).scalar()
            #if ___r is None: # not re mapping to user, impossibile
            __r['user'] = {
                    'id': ___r.id,
                    'avatar_url': ___r.avatar_url
                    }
            ___r = db.session.query(rates).\
                    filter(_r.user_id == rates.id, id == rates.business_id).scalar()

            if ___r is not None:
                __r['rate'] = ___r.rate

            self.args[field_inputs_wrap_head].append(__r)


        _resource_fields = resource_fields.copy()
        _resource_fields_wrap = resource_fields_wrap.copy()
        _resource_fields['user'] = fields.Nested(resource_fields_user)
        _resource_fields_wrap[field_inputs_wrap_head] = fields.List(fields.Nested(_resource_fields))
        self.args['type'] = "business"
        self.args['subtype'] = "comment"
        return marshal(self.args, _resource_fields_wrap), 200

class CustomerComments(Resource):
    """entry point about '/rest/customer/comments'
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

        super(CustomerComments, self).__init__()

    def get(self):
        """Get all data, getall

        @api {get} /rest/customer/comments list all comments
        @apiName GetAllCustomerComments
        @apiVersion 0.0.5
        @apiGroup campaign
        @apiPermission registered user


        @apiDescription
        todo validation<br/>
        todo query target<br/>

        @apiParam {Number=0, 25, 50, 100} [itemsPerPage=25] items for each request.
        @apiParam {Number} [page=1] page you want to request from, start with 1.
        @apiParam {String} [orderBy=mtime] the items order by column you specified.
        @apiParam {String="true", "false"} [desc=false] the items order by descending or asceding order.
        @apiParam {String={..254}} [q] query string for pre-defined columns.


        @apiExample {curl} Example usage:
        curl -X GET -H "mTag: xx" -H "Content-Type:application/json" http://localhost/rest/customer/comments

        HTTP/1.0 200 OK
        {  
            "page":1,
            "orderBy":"mtime",
            "desc":0,
            "total":2,
            "subtype":"comment",
            "type":"business",
            "itemsPerPage":25,
            "data":[  
                {  
                    "id":1,
                    "business_id":1,
                    "mtime":"2016-08-31 00:14:56.215613",
                    "content":"Starbucks were all over Singapore and the quality ",
                    "rate":2,
                    "user":{  
                        "id":2,
                        "avatar_url":""
                    }
                },
                {  
                    "id":2,
                    "business_id":1,
                    "mtime":"2016-08-31 04:23:15.682219",
                    "content":"Starbucks were all over Singapore and the quality ",
                    "rate":2,
                    "user":{  
                        "id":2,
                        "avatar_url":""
                    }
                }
            ]
        }

        @apiSuccess {Number}   total         total items for pagination.
        @apiSuccess {String}   orderBy       the items order by column you specified.
        @apiSuccess {Number}   page          page you want to request from, start with 1.
        @apiSuccess {Number}   itemsPerPage  items for each request.
        @apiSuccess {String}   desc          the items order by descending or asceding order.

        @apiSuccess {Object[]} data       List of business's comments.
        @apiSuccess {Number}   data.id    item's uniq id.
        @apiSuccess {String}   data.content  item's comment content
        @apiSuccess {Number}   data.rate   item's rate for business item
        @apiSuccess {Number}   data.mtime  items's latest modified time with ISO 8601 format
        @apiSuccess {Object}   data.user   item's author infomation
        @apiSuccess {Number}   data.user.id  item's author id
        @apiSuccess {String}   data.user.avatar_url  item's author avatar

        @apiError CE_INVALID_PARAM invalid parameter
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2001,
            "message": "{'pages'}"
        }

        @apiError CE_NOT_EXIST item not found
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2003,
            "message": "id 1 not found"
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
            ___r = db.session.query(Users).\
                    filter(_r.user_id == Users.id).scalar()
            __r['user'] = {
                    'id': ___r.id,
                    'avatar_url': ___r.avatar_url
                    }
            ___r = db.session.query(rates).\
                    filter(_r.user_id == rates.user_id, _r.business_id == rates.business_id).scalar()
            if ___r is not None:
                __r['rate'] = ___r.rate

            self.args[field_inputs_wrap_head].append(__r)


        _resource_fields = resource_fields.copy()
        _resource_fields_wrap = resource_fields_wrap.copy()
        _resource_fields['user'] = fields.Nested(resource_fields_user)
        _resource_fields_wrap[field_inputs_wrap_head] = fields.List(fields.Nested(_resource_fields))
        self.args['type'] = "business"
        self.args['subtype'] = "comment"
        return marshal(self.args, _resource_fields_wrap), 200

    #@marshal_with(task_list_format)
    def post(self):
        """create data
        """
        """create comment 

        @api {post} /rest/customer/comments create comment
        @apiVersion 0.0.5
        @apiName CreateComment
        @apiGroup campaign
        @apiPermission registered user


        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiParam {Object}          data        object
        @apiParam {String{..254}}   data.content message's title
        @apiParam {Number}          data.business_id comment belong to the business_id 
        @apiParam {Number}          data.user_id  user who create it
        @apiParam {Number={0..5}}   data.rate    comment's rate
        @apiParam {String}          type         request's type
        @apiParam {String}          subtype      request's subtype
        @apiExample {curl} Example usage:

        curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "
        {  
            "subtype":"comment",
            "type":"business",
            "data":{  
                "content":"Starbucks were all over Singapore and the quality ",
                "business_id":1,
                "user_id":2,
                "rate":1
            }
        }" http://localhost/rest/customer/comments

        HTTP/1.0 200 OK
        {  
            "data":{  
                "content":"Starbucks were all over Singapore and the quality ",
                "user_id":1,
                "business_id":1,
                "rate":1,
                "mtime":"2016-08-31 04:16:42.091706",
                "id":2
            },
            "type":"business",
            "subtype":"comment"
        }

        @apiSuccess {Object}          data        object
        @apiSuccess {String{..254}}   data.content message's title
        @apiSuccess {Number}          data.business_id comment belong to the business_id 
        @apiSuccess {Number}          data.user_id  user who create it
        @apiSuccess {Number}          data.id      comment's id
        @apiSuccess {String{..254}}   data.mtime   comment's modify time
        @apiSuccess {Number={0..5}}   data.rate    comment's rate
        @apiSuccess {String}          type         request's type
        @apiSuccess {String}          subtype      request's subtype

        """



        # 1. parsing reqest
        # 1.1 parsing 1st layer reqest

        try:
            #orgArgs = {'type': 'business', 'subtype': 'comment', 'data': {"content": "Starbucks were all over Singapore and the quality" ,"business_id": 1, "user_id": 1}}'

            orgArgs, self.args = GetTwoLayerRequestArgs(field_inputs_wrap_head, field_inputs_post)
            #print("self.args=", self.args)
            #return {}, 400

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


        # TODO: make sure tranaction
        # 1.3 check name unique
        _r = rates.query.filter(rates.user_id == self.args['user_id'],
                rates.business_id == self.args['business_id'],
                rates.isdel == False).scalar()

        if _r is not None:
            return omitError('CE_DATA_DUPLICATE',
                    'user_id {}, business_id {} are duplicate'.format(self.args['user_id'],
                        self.args['business_id'])), 400


        _r = rates()
        _r.business_id = self.args['business_id']
        _r.user_id = self.args['user_id']
        _r.rate = self.args['rate']

        # 4. commit to save
        try:
            db.session.add(r)
            db.session.add(_r)
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
        next(iter(out))[field_inputs_wrap_head].update({'rate':  self.args['rate']})
        next(iter(out))['type'] = 'business'
        next(iter(out))['subtype'] = 'comment'

        return out

    def delete(self):
        """multi delete
        delete comments by comment id 

        @api {delete} /rest/customer/comments delete comments by id
        @apiVersion 0.0.5
        @apiName DeleteCommentsById
        @apiGroup campaign
        @apiPermission registered user

        @apiParam {String{..254}} [comments] the items id seperate with common

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiExample {curl} Example usage:

        curl -X DELETE -H "mTag: xx" -H "Content-Type:application/json" http://localhost/rest/customer/comments?comments=1,2

        """
        try:
            ids = request.args.get(__heads__).split(',')
        except Exception as error:
            return omitError(ErrorMsg='param `{}` not found'.format(__heads__)), 400

        _r = []
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

            r.isdel = True
            _r.append(r)

        _rates = []
        for __r in _r:
            ___r = rates.query.filter(rates.user_id == __r.user_id,
                rates.business_id == __r.business_id,
                rates.isdel == False).scalar()

            if ___r is None:
                return omitError('CE_NOT_EXIST',
                        'user_id {}, business_id {} are duplicate'.format(__r.user_id,
                            __r.business_id)), 400

            ___r.isdel = True
            _rates.append(___r)


        try:
            for v in _r:
                db.session.merge(v)
            for v in _rates:
                db.session.merge(v)

            db.session.flush()
            db.session.commit()
        except Exception as error:
            logger.warning('session commit error(%s)', error)
            db.session.rollback()
            return omitError(ErrorMsg=repr(error)), 400

        return '', 204
