# -*- coding: utf-8 -*-

# sys
import json
import traceback
import os.path
# for ip validate
import socket
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
from module.common import _add_argument, GetResource, ExtraParamsIsValid
from module.common import GetResource,\
       GetRequestArgs, GetRequest, ExtraParamsIsValid,\
       RemoveRequestArgs, GetTwoLayerRequestArgs,\
       SerialGroupOutput, PrepareGroupORM,\
       SerialObjOutput, PrepareObjORM
from module.common import field_inputs_wrap_head

#
# predefind validate in each column, please ref to MRQ
#
from .model import CustomerBusinesses as obj, \
        CustomerBusinessgrps as grp, \
        CustomerBusinessDetails as detail, \
        CustomerBusinessComments as comment, \
        CustomerBusinessDeals as deals, \
        CustomerBusinessPics as pics, \
        CustomerBusinessRates as rates, \
        CustomerBusinessFavorite as favor

from module.user.model import Users

from .__init__ import \
        __customer_business_head__ as __head__, \
        __customer_business_heads__ as __heads__, \
        __customer_business_detail_head__ as __head_detail__, \
        __customer_business_detail_rates_head__ as __head_detail_rates__, \
        __customer_business_detail_deals_head__ as __head_detail_deals__, \
        __customer_business_detail_images_url_head__ as __head_detail_images_url__


from .business_valid import \
    resource_fields, resource_fields_ref, resource_fields_wrap, \
    resource_fields_detail, \
    resource_fields_detail_rates, \
    resource_fields_detail_deals, \
    field_inputs_detail_rates, \
    resource_fields_detail_images_url, \
    resource_fields_post, \
    field_inputs, field_inputs_ref, field_inputs_wrap, \
    field_inputs_detail, field_inputs_detail_deals, field_inputs_detail_images_url, \
    field_inputs_post


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

        @api {put} /rest/customer/business/:id Update a item
        @apiVersion 0.0.5
        @apiName UpdateCustomerBusiness
        @apiGroup business
        @apiPermission registered user


        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo error / success return code in api <br />

        @apiParam {Object}     data       object of business.
        @apiParam {Number}     data.id    item's uniq id.
        @apiParam {String}     data.name  item's name.
        @apiParam {Number}     data.cat   item's business industry category.
        @apiParam {float}      data.lat   item's entered latitude.
        @apiParam {float}      data.long  item's entered longitude.
        @apiParam {String}     data.address item's address
        @apiParam {String}     data.description item's description.
        @apiParam {String}     data.image_url  items's image url.
        @apiParam {Float}      data.rate item's rate, average from each comments
        @apiParam {Number}     data.deal  one of item's deal for display in list
        @apiParam {Object[]}   data.deals item's deals
        @apiParam {String}     data.deals.title item's deal title
        @apiParam {String}     data.deals.description item's deal description
        @apiParam {String}     data.open item open time with 24h format
        @apiParam {String}     data.open item close time with 24h format
        @apiParam {Number}     data.dist item's distance farward with your current location, the unit is meter
        @apiParam {Object}     data.images_url item images' path
        @apiParam {String}     data.images_url.bg item backgound images' path
        @apiParam {String}     data.images_url.icon item icon images' path


        @apiExample {curl} Example usage:
        curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "
        {  
            "data":{  
                "dist":12245,
                "close":"2200",
                "lat":120.678,
                "features":"this is features",
                "address":"this is address",
                "deals":[  
                    {  
                        "title":"10% Off Any Order",
                        "description":"Use this promo code and save on coffee, tea, and..."
                    }
                ],
                "cat":1,
                "long":23.5383,
                "meals":"this is meals",
                "deal":200,
                "open":"0600",
                "description":"early Bird Special: Get  off.",
                "name":"Starbucks Coffee 31",
                "images_url":{  
                    "icon":"/img/business/1/icon",
                    "bg":"/img/business/1/bg"
                },
                "id":1
            },
            "type":"business",
            "subtype":"overview"
        }
        " http://localhost/rest/customer/business/1

        @apiError CE_INVALID_PARAM invalid parameter

           HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2001,
               "message": "ValueError('[cat]: (cat Valid Error) Missing required parameter in dataDict, error=400: Bad Request',)"
           }

        @apiError CE_NAME_CONFLICT name conflict
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2004,
            "message": "IntegrityError('(sqlite3.IntegrityError) UNIQUE constraint failed: customer_businesses.name',)"
        }

        @apiError CE_NOT_EXIST item not found
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2003,
            "message": "id 17 not found"
        }

        """
        # 1. parsing reqest
        try:
            orgArgs, self.args = GetTwoLayerRequestArgs(field_inputs_wrap_head, field_inputs_post)
            RemoveRequestArgs(field_inputs_post)
            j = request.get_json()
            orgdetailImgsUrlArgs, self.detailimgsurlargs = GetTwoLayerRequestArgs(None, 
                    field_inputs_detail_images_url,
                    j[field_inputs_wrap_head][__head_detail_images_url__])


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

            _item = []
            for k, v in self.args.items():
                if k != "deals":
                    _item.append((k, v))
            r = PrepareObjORM(r, _item)

            r.mtime = t;

            d = detail.query.filter(detail.business_id == id, detail.isdel == False).scalar()
            __deals = deals.query.filter(deals.business_id == id, deals.isdel == False).all()
            # TODO: mark isdel = True?
            #for v in __deals:
            #    v.isdel = True;

            _deals = [];
            for k, v in self.args.items():
                if v != None:
                    if k == 'deals':
                        deal = deals();
                        for v1 in v: # each entry
                            for k2, v2 in v1.items():
                                setattr(deal, k2, v2)
                        _deals.append(deal)
                    else:
                        setattr(d, k, v)

            d.mtime = t;

            _pics = [];
            _ps = pics.query.filter(pics.business_id == id, pics.isdel == False).all()
            # FIXME: hard code mapping
            for k, v in self.detailimgsurlargs.items():
            # (1, 'icon'), (2, 'bg'), (3, 'gallery')
                p = pics()
                if k == 'icon':
                    p.type = 1
                elif k == 'bg':
                    p.type = 2

                if p.type:
                    p.path = v
                    _pics.append(p)


        except Exception as error:
            return omitError(ErrorMsg=repr(error)), 400

        # 4. commit to save
        try:
            #db.session.merge(r)
            for v in __deals:
                db.session.delete(v)

            for v in _ps:
                db.session.delete(v)

            for v in _pics:
                db.session.add(v)

            for v in _deals:
                db.session.add(v)

            db.session.flush()
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            if exc.IntegrityError == type(error):
                return omitError('CE_NAME_CONFLICT', repr(error)), 400

            return omitError(ErrorMsg=repr(error)), 400

        # 5. return all data to user
        out = SerialObjOutput(d, objname=field_inputs_wrap_head,
                resource_fields=resource_fields_post), 200

        for k, v in field_inputs.items():
            if k not in ['id', 'image_url']:
                next(iter(out))[field_inputs_wrap_head].update({k: orgArgs[k]})

        next(iter(out))[field_inputs_wrap_head].update({'deals': orgArgs['deals']})
        next(iter(out))[field_inputs_wrap_head].update({'images_url': orgArgs['images_url']})
        next(iter(out))[field_inputs_wrap_head].update({'id': id})
        next(iter(out))['type'] = 'business'
        next(iter(out))['subtype'] = 'overview'

        return out

    def get(self, id):
        """get one item

        @api {get} /rest/customer/business/:id get one business
        @apiName GetCustomerBusiness
        @apiVersion 0.0.4
        @apiGroup customer
        @apiPermission registered user

        @apiDescription
        todo validation<br />
        todo query target<br/>

        @apiParam {Number} id business id, you can get from GetAllCustomerBusinesses.

        @apiExample Example usage:
        HTTP/1.0 200 OK
        {
            "id": 1,
            "name": "Starbucks Coffee",
            "image_url": "/business/1/icon",
            "cat": 1,
            "deal": 200,
            "lat": 120.678469,
            "long": 23.538302,
            "description": "Early Bird Special: Get $2 off.",
            "detail": {
                "rate": 4.3,
                "rates": [
                    {"u_id": 1, "avatar_url": "/user/1/avater"},
                    {"u_id": 2, "avatar_url": "/user/2/avater"}
                ],
                "deals": [
                    {"title": "morning", "description": "for every one"}
                ],
                "open": "0600",
                "close": "2100",
                "dist": 12333333,
                "address": "CA",
                "images_url": {
                    "bg": "/business/1/bg",
                    "icon": "/business/1/icon"
                }
            }
        }



        @apiSuccess {Object}     business       object of business.
        @apiSuccess {Number}     business.id    item's uniq id.
        @apiSuccess {String}     business.name  item's name.
        @apiSuccess {Number}     business.cat   item's business industry category.
        @apiSuccess {float}      business.lat   item's entered latitude.
        @apiSuccess {float}      business.long  item's entered longitude.
        @apiSuccess {String}     business.address item's address
        @apiSuccess {String}     business.description item's description.
        @apiSuccess {Number}     business.deal  item's deal.
        @apiSuccess {String}     business.image_url  items's image url.
        @apiSuccess {Object}     business.detail item's detail
        @apiSuccess {Float}      business.detail.rate item's rate, average from each comments
        @apiSuccess {Object[]}   business.detail.rates item's brief comments 
        @apiSuccess {Number}     business.detail.rates.u_id comment's author id
        @apiSuccess {String}     business.detail.rates.avatar_url comment's author avatar url path
        @apiSuccess {Object[]}   business.detail.deals item's deals
        @apiSuccess {String}     business.detail.deals.title item's deal title
        @apiSuccess {String}     business.detail.deals.description item's deal description
        @apiSuccess {String}     business.detail.open item open time with 24h format
        @apiSuccess {String}     business.detail.open item close time with 24h format
        @apiSuccess {Number}     business.detail.dist item's distance farward with your current location, the unit is meter
        @apiSuccess {Object}     business.detail.images_url item images' path
        @apiSuccess {String}     business.detail.images_url.bg item backgound images' path
        @apiSuccess {String}     business.detail.images_url.icon item icon images' path



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
            "message": "id 17 not found"
        }

        """
        requestArgsSet = set((col) for col in request.args)
        if not ExtraParamsIsValid(requestArgsSet):
            return omitError(ErrorMsg=repr(set((col) for col in request.args))), 400

        r = detail.query.filter(detail.business_id == id, detail.isdel == False).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST', 'id {} not found'.format(id)), 400

        self.args = {}
        self.args[field_inputs_wrap_head] = {}
        #self.args[field_inputs_wrap_head][__head_detail__] = {}
        _resource_fields_wrap = resource_fields_wrap.copy()
        for col in resource_fields_wrap:
            if col not in ['type', 'subtype']:
                _resource_fields_wrap.pop(col, None) 
        #_resource_fields_detail_wrap = {}
        #resource_fields_detail[__head_detail_rates__] = \
        #       fields.List(fields.Nested(resource_fields_detail_rates))
        resource_fields_detail[__head_detail_deals__] = \
               fields.List(fields.Nested(resource_fields_detail_deals))

        _resource_fields_detail_rates = {}
        #_resource_fields_detail_rates['user'] = fields.Nested(resource_fields_detail_rates)
        _resource_fields_detail_rates = resource_fields_detail_rates.copy()
        resource_fields_detail['users'] = \
               fields.List(fields.Nested(_resource_fields_detail_rates))
        #resource_fields.update(resource_fields_detail)
        resource_fields_detail[__head_detail_images_url__] = \
                fields.Nested(resource_fields_detail_images_url)
        #resource_fields[__head_detail__] = fields.Nested(_resource_fields_detail_wrap)
        #_resource_fields_wrap[field_inputs_wrap_head] = fields.Nested(resource_fields)
        _resource_fields_wrap[field_inputs_wrap_head] = fields.Nested(resource_fields_detail)


        #print('_resource_fields_wrap ', resource_fields)

        _r = r
        #for col in resource_fields.keys():
        #    self.args[field_inputs_wrap_head][col] = getattr(_r, col)
        #for col in resource_fields.keys():
        for col in _r.__table__.columns.keys():
            self.args[field_inputs_wrap_head][col] = getattr(_r, col)

        self.args[field_inputs_wrap_head]['name'] = getattr(_r.meta, 'name')

        rate = 0;
        self.args[field_inputs_wrap_head]['rate'] = rate
        self.args[field_inputs_wrap_head]['users'] = []
        self.args[field_inputs_wrap_head][__head_detail_deals__] = []
        self.args[field_inputs_wrap_head]['images_url'] = {}


        __r = db.session.query(rates).\
                filter(rates.business_id == id).all()
        r_len = len(__r)
        self.args[field_inputs_wrap_head]['rate_nr'] = r_len
        if r_len > 0:
            for ___r in __r:
                rate += ___r.rate
            self.args[field_inputs_wrap_head]['rate'] = int(rate / r_len)


        # FIXME: hard code
        __r = db.session.query(comment).\
                filter(comment.business_id == id).order_by(comment.mtime.desc()).offset(0).limit(5).all()
        r_len = len(__r)
        self.args[field_inputs_wrap_head]['user_nr'] = r_len
        if r_len > 0:
            for __r in __r:
                ___r = db.session.query(Users).\
                        filter(__r.user_id == Users.id).scalar()

                self.args[field_inputs_wrap_head]['users'].append(
                    #{'user': 
                        {
                        'id': ___r.id,
                        'avatar_url': ___r.avatar_url
                        }
                    #}
                    )
                
        # TODO: get favorite by User id from session

        _r = deals.query.filter(deals.business_id == id).all()
        r_len = len(_r)
        if r_len:
            for __r in _r:
                self.args[field_inputs_wrap_head][__head_detail_deals__].append({
                    'title': __r.title,
                    'description': __r.description
                    })

        _r = pics.query.filter(pics.business_id == id).all()
        # (1, 'icon'), (2, 'bg'), (3, 'gallery')
        r_len = len(_r)
        if r_len > 0:
            # TODO: mapping table
            for __r in _r:
                if getattr(__r, 'type') == 1:
                    self.args[field_inputs_wrap_head]['images_url']['icon'] = \
                    getattr(__r, 'path')
                    r_len -= 1
                elif getattr(__r, 'type') == 2:
                    self.args[field_inputs_wrap_head]['images_url']['bg'] = \
                    getattr(__r, 'path')
                    r_len -= 1

        self.args[field_inputs_wrap_head]['gallery_nr'] = r_len
        self.args[field_inputs_wrap_head]['id'] = id

        self.args['type'] = "business"
        self.args['subtype'] = "overview"
        #print('self.args= ', self.args, '_resource_fields_wrap', _resource_fields_wrap)

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

        @api {get} /rest/customer/businesses list business
        @apiName GetAllCustomerBusinesses
        @apiVersion 0.0.3
        @apiGroup business
        @apiPermission registered user

        @apiDescription
        modified: change category type from string to number.<br/>
        modified: add name attribute.<br />
        modified: change deal type from string to number.<br/>
        todo validation<br/>
        query string <br />
        todo error / success return code in api <br />

        @apiParam {Number=0, 25, 50, 100} [itemsPerPage=25] items for each request.
        @apiParam {Number} [page=1] page you want to request from, start with 1.
        @apiParam {String="name", "description"} [orderBy=name] the items order by column you specified.
        @apiParam {String="true", "false"} [desc=false] the items order by descending or asceding order.


        @apiExample {curl} Example usage:
        curl -X GET -H "mTag: xx" -H "Content-Type:application/json" -i http://localhost/rest/customer/businesses?itemsPerPage=50&page=1&orderBy=name&desc=true

        {  
            "page":1,
            "type":"business",
            "orderBy":"name",
            "desc":0,
            "total":1,
            "itemsPerPage":25,
            "subtype":"list",
            "data":[  
                {  
                    "lat":120.678,
                    "id":1,
                    "deal":200,
                    "name":"Starbucks Coffee 31",
                    "image_url":"",
                    "long":23.5383,
                    "cat":1,
                    "description":"early Bird Special: Get  off."
                }
            ]
        }

        @apiSuccess {Number}   total         total items for pagination
        @apiSuccess {String}   orderBy       the items order by column you specified
        @apiSuccess {Number}   page          page you want to request from, start with 1
        @apiSuccess {Number}   itemsPerPage  items for each request
        @apiSuccess {String}   desc          the items order by descending or asceding order
        @apiSuccess {String}   type          request's type
        @apiSuccess {String}   subtype       request's subtype
        @apiSuccess {Object}   business       object of business.
        @apiSuccess {Number}   business.id    item's uniq id.
        @apiSuccess {String}   business.name  item's name.
        @apiSuccess {Number}   business.cat   item's business industry category.
        @apiSuccess {float}    business.lat   item's entered latitude.
        @apiSuccess {float}    business.long  item's entered longitude.
        @apiSuccess {String}   business.address item's address
        @apiSuccess {String}   business.description item's description.
        @apiSuccess {Number}   business.deal  item's deal.
        @apiSuccess {String}   business.image_url  items's image url.


        @apiError CE_INVALID_PARAM invalid parameter
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
            #__r['description'] = getattr(_r.detail, 'description')

            # (1, 'icon'), (2, 'bg'), (3, 'gallery')
            ___r  = pics.query.filter(pics.business_id == _r.id, pics.type == 1).scalar()
            __r['image_url']  = getattr(___r, 'path', "")
            self.args[field_inputs_wrap_head].append(__r)

        resource_fields_wrap[field_inputs_wrap_head] = fields.List(fields.Nested(resource_fields))
        self.args['type'] = "business"
        self.args['subtype'] = "list"
        return marshal(self.args, resource_fields_wrap), 200

    #@marshal_with(task_list_format)
    def post(self):
        """create data

        @api {post} /rest/customer/businesses Create a item
        @apiVersion 0.0.3
        @apiName CreateCustomerBusiness
        @apiGroup business
        @apiPermission registered user

        @apiDescription
        todo validation <br/>
        todo certificate with cookies / oauth 2.0 <br/>
        todo muti-create <br />
        todo error / success return code in api


        @apiParam {Object}     data       object of business.
        @apiParam {Number}     data.id    item's uniq id.
        @apiParam {String}     data.name  item's name.
        @apiParam {Number}     data.cat   item's business industry category.
        @apiParam {float}      data.lat   item's entered latitude.
        @apiParam {float}      data.long  item's entered longitude.
        @apiParam {String}     data.address item's address
        @apiParam {String}     data.description item's description.
        @apiParam {String}     data.image_url  items's image url.
        @apiParam {Float}      data.rate item's rate, average from each comments
        @apiParam {Number}     data.deal  one of item's deal for display in list
        @apiParam {Object[]}   data.deals item's deals
        @apiParam {String}     data.deals.title item's deal title
        @apiParam {String}     data.deals.description item's deal description
        @apiParam {String}     data.open item open time with 24h format
        @apiParam {String}     data.open item close time with 24h format
        @apiParam {Number}     data.dist item's distance farward with your current location, the unit is meter
        @apiParam {Object}     data.images_url item images' path
        @apiParam {String}     data.images_url.bg item backgound images' path
        @apiParam {String}     data.images_url.icon item icon images' path


        @apiExample {curl} Example usage:

        curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "
        {  
            "data":{  
                "dist":12245,
                "close":"2200",
                "lat":120.678,
                "features":"this is features",
                "address":"this is address",
                "deals":[  
                    {  
                        "title":"10% Off Any Order",
                        "description":"Use this promo code and save on coffee, tea, and..."
                    }
                ],
                "cat":1,
                "long":23.5383,
                "meals":"this is meals",
                "deal":200,
                "open":"0600",
                "description":"early Bird Special: Get  off.",
                "name":"Starbucks Coffee 31",
                "images_url":{  
                    "icon":"/img/business/1/icon",
                    "bg":"/img/business/1/bg"
                },
                "id":1
            },
            "type":"business",
            "subtype":"overview"
        }" http://localhost/rest/customer/businesses


        @apiError CE_INVALID_PARAM invalid parameter
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2001,
            "message": "ValueError('[cat]: (cat Valid Error) Missing required parameter in dataDict, error=400: Bad Request',)"
        }

        @apiError CE_NAME_CONFLICT name conflict
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2004,
            "message": "IntegrityError('(sqlite3.IntegrityError) UNIQUE constraint failed: customer_businesses.name',)"
        }


        @apiError CE_EXCEED_LIMIT exceed max limit
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2005,
            "message": "limit is 5"
        }

        """

        # 1. parsing reqest
        # 1.1 parsing 1st layer reqest

        try:
            #orgArgs = {'type': 'business', 'subtype': 'overview', 'data': {'name': 'Starbucks Coffee 1', 'description': 'early Bird Special: Get  off.', 'address': 'this is address', 'close': '2200', 'meals': 'this is meals', 'long': 23.5383, 'open': '0600', 'lat': 120.678, 'dist': 12245, 'cat': 1, 'images_url': {'icon': '/img/business/1/icon', 'bg': '/img/business/1/bg'}, 'features': 'this is features', 'deal': 200, 'deals': [{'description': 'Use this promo code and save on coffee, tea, and...', 'title': '10% Off Any Order'}]}}'

            orgArgs, self.args = GetTwoLayerRequestArgs(field_inputs_wrap_head, field_inputs_post)
            RemoveRequestArgs(field_inputs_post)
            j = request.get_json()
            orgdetailImgsUrlArgs, self.detailimgsurlargs = GetTwoLayerRequestArgs(None, 
                    field_inputs_detail_images_url,
                    j[field_inputs_wrap_head][__head_detail_images_url__])
            #self.args= {'name': 'Starbucks Coffee 1', 'description': 'early Bird Special: Get  off.', 'address': 'this is address', 'close': '2200', 'meals': 'this is meals', 'long': '23.5383', 'open': '0600', 'lat': '120.678', 'dist': 12245, 'cat': 1, 'features': 'this is features', 'deal': 200, 'deals': [{'description': 'Use this promo code and save on coffee, tea, and...', 'title': '10% Off Any Order'}]} self.detailimgsurlargs= {'icon': '/img/business/1/icon', 'bg': '/img/business/1/bg'}}
            #print("self.args=", self.args, "self.detailimgsurlargs=", self.detailimgsurlargs)

        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        # 1.3 check name unique
        r = obj.query.filter(obj.name == self.args['name'], 
                obj.isdel == False).scalar()

        if r is not None:
            return omitError('CE_NAME_CONFLICT',
                    'name {} conflict'.format(self.args['name'])), 400


        # 2. validate follows spec
        if db.session.query(obj).filter(obj.isdel == False).count() > max:
            return omitError('CE_EXCEED_LIMIT', 'limit is {}'.format(max)), 400


        r = obj()
        d = detail()
        _pics = [];
        _deals = [];
        try:
            _item = []
            for k, v in self.args.items():
                if k != "deals":
                    _item.append((k, v))
            r = PrepareObjORM(r, _item)

            # FIXME: hard code mapping
            for k, v in self.detailimgsurlargs.items():
            # (1, 'icon'), (2, 'bg'), (3, 'gallery')
                p = pics()
                if k == 'icon':
                    p.type = 1
                elif k == 'bg':
                    p.type = 2

                if p.type:
                    p.path = v
                    _pics.append(p)

            for k, v in self.args.items():
                if v != None:
                    if k == 'deals':
                        deal = deals();
                        for v1 in v: # each entry
                            for k2, v2 in v1.items():
                                setattr(deal, k2, v2)
                        _deals.append(deal)
                    else:
                        setattr(d, k, v)
            #print("d.__dict__ = ", d.__dict__)

        except Exception as error:
            return omitError(ErrorMsg=repr(error)), 400


        # 4. commit to save
        try:
            db.session.add(r)
            # At this point, the object f has been pushed to the DB, 
            # and has been automatically assigned a unique primary key id
            db.session.flush()
            # refresh updates given object in the session with its state in the DB
            # (and can also only refresh certain attributes - search for documentation)
            db.session.refresh(r)

            d.business_id = r.id
            #print("d.__dict__ = ", d.__dict__)
            db.session.add(d)
            for v in _deals:
                v.business_id = r.id
                db.session.add(v)

            for v in _pics:
                v.business_id = r.id
                db.session.add(v)

            db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.warning('session commit error(%s)', error)

            if exc.IntegrityError == type(error):
                return omitError('CE_NAME_CONFLICT', repr(error)), 400

            return omitError(ErrorMsg=repr(error)), 400


        # 5. return all data to user
        out = SerialObjOutput(d, objname=field_inputs_wrap_head,
                resource_fields=resource_fields_post), 200

        for k, v in field_inputs.items():
            if k not in ['id', 'image_url']:
                next(iter(out))[field_inputs_wrap_head].update({k: orgArgs[k]})

        next(iter(out))[field_inputs_wrap_head].update({'deals': orgArgs['deals']})
        next(iter(out))[field_inputs_wrap_head].update({'images_url': orgArgs['images_url']})
        next(iter(out))[field_inputs_wrap_head].update({'id': r.id})
        next(iter(out))['type'] = 'business'
        next(iter(out))['subtype'] = 'overview'

        return out

    def delete(self):
        """multi delete
        @api {delete} /rest/customer/businesses Delete items
        @apiName DelCustomerBusiness
        @apiVersion 0.0.3
        @apiGroup customer
        @apiPermission registered user

        @apiDescription
        todo validation

        @apiParam {String{..254}} [ids] the items id seperate with common

        @apiExample {curl} Example usage:
        curl -X DELETE -v -b $COOKIES -H "Content-Type:application/json" http://localhost/rest/customer/businesses?id=1,2,3
        HTTP/1.0 204 NO CONTENT


        @apiError CE_INVALID_PARAM invalid parameter
        HTTP/1.0 400 BAD REQUEST
        {
            "errorId": 2001,
            "message": "param `businesses` not found"
        }

        @apiError CE_NOT_EXIST item not found
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
                return omitError(ErrorMsg='id `{}` not int'.format(id)), 400

            # it could als cascade delete `online` user
            r = obj.query.filter(obj.id == id, obj.isdel == False).scalar()
            if r is None:
                return omitError('CE_NOT_EXIST',
                        'id {} not found'.format(id)), 400

        _details = []
        _pics = []
        _deals = []
        _r = []
        for id in ids:
            id = inputs.natural(id)

            # it could als cascade delete `online` user
            r = obj.query.filter(obj.id == id, obj.isdel == False).scalar()
            r.isdel = True
            _r.append(r)

            # must have
            d = detail.query.filter(detail.business_id == id, detail.isdel == False).scalar()
            d.isdel = True
            _details.append(d)

            p = pics.query.filter(pics.business_id == id, pics.isdel == False).all()
            _pics += p

            __deals = deals.query.filter(deals.business_id == id, deals.isdel == False).all()
            _deals += __deals


        try:
            for v in _deals:
                db.session.delete(v)

            for v in _pics:
                db.session.delete(v)

            for v in _r:
                db.session.merge(v)

            for v in _details:
                db.session.merge(v)

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
