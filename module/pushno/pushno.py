# -*- coding: utf-8 -*-

# sys
import json
import traceback
import os.path
import math
from datetime import datetime

# flask
from flask import Flask, request
from sqlalchemy import exc
from pushjack import GCMClient, APNSClient


# config
from config.config import _logging, db, platform_model_config, settings
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
from .model import Pushno as obj
from module.customer.model import CustomerBusinesses as business
from module.user.model import Users

from .__init__ import \
        __pushno_head__ as __head__, \
        __pushno_heads__ as __heads__


from .pushno_valid import \
    resource_fields, resource_fields_wrap, \
    field_inputs, field_inputs_wrap,\
    field_inputs_post, resource_fields_post,\
    field_inputs_send, resource_fields_send

gcm_client = GCMClient(api_key=settings.GCM_API_KEY)
#FIXME: use config
apns_client = APNSClient(certificate=settings.APNS_API_KEY,
                    default_error_timeout=10,
                    default_expiration_offset=2592000,
                    default_batch_size=1000)


# TODO: need limit max sender?

class PushnoReg(Resource):
    response = None
    args = None
    args_wrap = None

    def __init__(self):
        request.dataDictWrap = dict((col, request.args.get(col)) for col in request.args)
        if request.dataDictWrap:
            _add_argument(reqparse, field_inputs_wrap, location=['dataDictWrap'])

        super(PushnoReg, self).__init__()

    # id: business_id
    def post(self, id):
        """regist devices to one business for push notification

        @api {post} /rest/pushno/reg/:id regist devices
        @apiVersion 0.0.4
        @apiName RegistOneDevice
        @apiGroup pushno
        @apiPermission registered user

        @apiParam {Number} id business id, you can get from GetAllCustomerBusinesses.

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiParam {Object[]}        devices         List of devices
        @apiParam {Number}          devices.user_id registered user id
        @apiParam {Number=1, 2}     devices.type    device's type, 1 for andriod, 2 for ios
        @apiParam {String{..254}}   devices.dev_id  device's id
        @apiExample {curl} Example usage:

        curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "
        {  
           "data":[  
              {  
                 "type":1,
                 "user_id":1,
                 "dev_id":"eh2AM5l18K8:APA91bFsjAU_FmdkdTeErJ_BRSiz7_Iipi_r12QTscHciTVJmj1gcSK_p9l6BfgYtudntv0Ht7JNiyCe8lS-WdrL8zHOwCdGFdRutEDglPV1I9EeROVbhwVX0rcd_PS_jdCTQZ22inFq"
              }
           ]
        }" http://localhost/rest/pushno/reg/1
        """
        # 1. parsing reqest
        try:
            # TODO:validate by array
            #orgArgs, self.args = GetTwoLayerRequestArgs(field_inputs_wrap_head, field_inputs_post)
            self.args = []
            j = request.get_json()
            for v in j[field_inputs_wrap_head]:
                v['business_id'] = id
                self.args.append(v)

        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400


        # 2. get orm from db
        r = business.query.filter(business.id == id, business.isdel == False).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST',
                    'id {} not found'.format(id)), 400

        # TODO: UniqueConstraint at __pushno_tablename__ 
        # 3. assign request data to orm
        _r = []
        try:
            for v in self.args:
                #print("v=", v)
                r = obj()
                _r.append(PrepareObjORM(r, v.items()))

        except Exception as error:
            return omitError(ErrorMsg=repr(error)), 400

        # 4. commit to save
        try:
            for v in _r:
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
        # FIXME: return array
        out = SerialObjOutput(r, objname=field_inputs_wrap_head,
                resource_fields=resource_fields_post), 200

        next(iter(out))['type'] = 'pushno'
        next(iter(out))['subtype'] = 'reg'

        return out



    def get(self, id):
        """get all devices info by business id

        @api {get} /rest/pushno/reg/:id registed devices under business id
        @apiVersion 0.0.4
        @apiName GetAllDeviceByBusinessId
        @apiGroup pushno
        @apiPermission registered user

        @apiParam {Number} id business id, you can get from GetAllCustomerBusinesses.

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiExample {curl} Example usage:

        curl -X GET -H "mTag: xx" -H "Content-Type:application/json" http://localhost/rest/pushno/reg/1

        {  
            "orderBy":"user_id",
            "desc":0,
            "subtype":"reg",
            "itemsPerPage":25,
            "page":1,
            "data":[  
                {  
                    "dev_id":"eh2AM5l18K8:APA91bFsjAU_FmdkdTeErJ_BRSiz7_Iipi_r12QTscHciTVJmj1gcSK_p9l6BfgYtudntv0Ht7JNiyCe8lS-WdrL8zHOwCdGFdRutEDglPV1I9EeROVbhwVX0rcd_PS_jdCTQZ22inFq",
                    "id":4,
                    "user_id":1,
                    "business_id":1,
                    "type":1
                },
                {  
                    "dev_id":"eh2AM5l18K8:APA91bFsjAU_FmdkdTeErJ_BRSiz7_Iipi_r12QTscHciTVJmj1gcSK_p9l6BfgYtudntv0Ht7JNiyCe8lS-WdrL8zHOwCdGFdRutEDglPV1I9EeROVbhwVX0rcd_PS_jdCTQZ22inFq",
                    "id":5,
                    "user_id":1,
                    "business_id":1,
                    "type":1
                },
                {  
                    "dev_id":"eh2AM5l18K8:APA91bFsjAU_FmdkdTeErJ_BRSiz7_Iipi_r12QTscHciTVJmj1gcSK_p9l6BfgYtudntv0Ht7JNiyCe8lS-WdrL8zHOwCdGFdRutEDglPV1I9EeROVbhwVX0rcd_PS_jdCTQZ22inFq",
                    "id":6,
                    "user_id":1,
                    "business_id":1,
                    "type":1
                }
            ],
            "total":3,
            "type":"pushno"
        }

        @apiSuccess {Number}   total         total items for pagination
        @apiSuccess {String}   orderBy       the items order by column you specified
        @apiSuccess {Number}   page          page you want to request from, start with 1
        @apiSuccess {Number}   itemsPerPage  items for each request
        @apiSuccess {String}   desc          the items order by descending or asceding order
        @apiSuccess {String}   type          request's type

        @apiSuccess {Object[]}   devices       object of devices
        @apiSuccess {Number}     devices.id    device's uniq id
        @apiSuccess {Number}     devices.user_id registered user id
        @apiSuccess {Number=1, 2}devices.type    device's type, 1 for andriod, 2 for ios
        @apiSuccess {String{..254}}   devices.dev_id  device's id
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

        r = obj.query.filter(obj.business_id == id, obj.isdel == False).order_by(isDesc())
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
        self.args['type'] = "pushno"
        self.args['subtype'] = "reg"
        return marshal(self.args, _resource_fields_wrap), 200

class PushnoUnReg(Resource):
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

        super(PushnoUnReg, self).__init__()

    def delete(self, business_id):
        """delete devices by device id under business id

        @api {delete} /rest/pushno/unreg/:id registed devices under business id
        @apiVersion 0.0.4
        @apiName DeleteDevicesByBusinessId
        @apiGroup pushno
        @apiPermission registered user

        @apiParam {Number} id business id
        @apiParam {String{..254}} [pushnos] the items id seperate with common

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiExample {curl} Example usage:

        curl -X DELETE -H "mTag: xx" -H "Content-Type:application/json" http://localhost/rest/pushno/unreg/1?pushnos=4
        """


        try:
            ids = request.args.get(__heads__).split(',')
        except Exception as error:
            return omitError(ErrorMsg='param `{}` not found'.format(__heads__)), 400

        r = business.query.filter(business.id == business_id, business.isdel == False).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST',
                    'id {} not found'.format(id)), 400

        _r = []
        for id in ids:
            try:
                id = inputs.natural(id)
            except Exception as error:
                return omitError(ErrorMsg='id `{}` not int'.format(id)), 400

            # it could als cascade delete `online` user
            r = obj.query.filter(obj.business_id == business_id, obj.id == id, obj.isdel == False).scalar()
            if r is None:
                return omitError('CE_NOT_EXIST',
                        'id {} not found'.format(id)), 400
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


class PushnoSend(Resource):
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

        super(PushnoSend, self).__init__()

    def post(self, business_id):
        """push notification to all device under business id

        @api {post} /rest/pushno/send/:id send message to registed devices under business id
        @apiVersion 0.0.4
        @apiName SendNoticeToDevicesByBusinessId
        @apiGroup pushno
        @apiPermission registered user

        @apiParam {Number} id business id

        @apiDescription
        todo certificate with cookies / oauth 2.0<br />
        todo long/lat validation<br />
        todo metadata for counter of registerd devices<br />
        todo error / success return code in api

        @apiParam {Object}          data        push notification's body
        @apiParam {String{..254}}   data.title  message's title
        @apiParam {String{..254}}   data.message  message
        @apiParam {String{..254}}   data.url  message's url
        @apiExample {curl} Example usage:

        curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "
        {  
            "data":{  
                "title":"XXXX",
                "message":"scscs",
                "uri":"xxxxx"
            }
        }" http://localhost/rest/pushno/reg/1

        """


        # 1. parsing reqest
        # 1.1 parsing 1st layer reqest

        try:
            orgArgs, self.args = GetTwoLayerRequestArgs(field_inputs_wrap_head, field_inputs_send)
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        # 2. get orm from db
        r = business.query.filter(business.id == business_id, business.isdel == False).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST',
                    'id {} not found'.format(business_id)), 400


        # 2. validate follows spec
        r = obj.query.filter(obj.business_id == business_id,
                obj.isdel == False).all()

        alert = {}
        alert['title'] = self.args['title']
        alert['message'] = self.args['message']
        alert['uri'] = self.args['uri']

        gcms = []
        apns = []
        for _r in r:
            # (1, 'andriod'), (2, 'ios')
            if _r.type == 1:
                gcms.append(_r.dev_id)
            elif _r.type == 2:
                apns.append(_r.dev_id)

        # ref: http://pushjack.readthedocs.io/en/latest/
        #logger.debug('gcm len %d, all items: %s', len(gcms), gcms)
        #>>> l = [1, 2, 3, 4]
        #>>> [l[i:i + 2] for i in range(0, len(l), 2)]
        #[[1, 2], [3, 4]]]
        _l = gcms
        itemsPerPage = settings.GCM_MAX_BATCH_SEND
        for chunk in [_l[i:i + itemsPerPage] for i in range(0, len(_l), itemsPerPage)]:
            # FIXME: config it
            response  = gcm_client.send(chunk, alert,
              collapse_key='mi',
              delay_while_idle=True,
              time_to_live=604800)
            #logger.debug("gcm r:", response, dir(response))

            #gcm errors: [GCMInvalidRegistrationError (code=InvalidRegistration): Invalid registration ID for identifier XXXXX, GCMInvalidRegistrationError (code=InvalidRegistration): Invalid registration ID for identifier XXXXX, GCMInvalidRegistrationError (code=InvalidRegistration): Invalid registration ID for identifier XXXXX]
            #gcm failures: ['XXXXX', 'XXXXX', 'XXXXX']
            #gcm data: [{'multicast_id': 5353943955785430694, 'results': [{'error': 'InvalidRegistration'}, {'error': 'InvalidRegistration'}, {'error': 'InvalidRegistration'}], 'success': 0, 'failure': 3, 'canonical_ids': 0}]
            #logger.debug('gcm errors: %s', response.errors)
            #logger.debug('gcm failures: %s', response.failures)
            #logger.debug('gcm data: %s', response.data)

            # Successfully handled registration_ids
            for reg_id in response.successes:
                logger.debug('Successfully sent notification for reg_id %d', (reg_id))
            
            # Handling errors
            # FIXME: add error code
            if len(response.errors) > 0:
                logger.debug('gcm data: %s', response.data)
                return omitError('CE_NOT_EXIST',
                    '{} not found'.format(response.errors)), 400
            
        _l = apns
        itemsPerPage = settings.APNS_MAX_BATCH_SEND
        for chunk in [_l[i:i + itemsPerPage] for i in range(0, len(_l), itemsPerPage)]:
            response = apns_client.send(apns,
                alert,
                expiration=int(time.time() + 604800),
                error_timeout=5,
                batch_size=1000)

            print("apns r:", dir(response))

            if len(response.errors) or len(response.token_errors) > 0:
                return omitError('CE_NOT_EXIST',
                    '{} not '.format(response)), 400

        apns_client.close()


        # 5. return all data to user
        out = SerialObjOutput(r, objname=field_inputs_wrap_head,
                resource_fields=resource_fields_send), 200

        next(iter(out))[field_inputs_wrap_head].update({'gcm_nr': len(gcms)})
        next(iter(out))[field_inputs_wrap_head].update({'apns_nr': len(apns)})
        next(iter(out))['type'] = 'pushno'
        next(iter(out))['subtype'] = 'send'

        return out

