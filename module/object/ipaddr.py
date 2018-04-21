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
from .model import ObjectsIpaddrs as obj, ObjectsIpgroups as grp
from .__init__ import __objects_ipaddr_head__ as __head__, \
        __objects_ipaddr_heads__ as __heads__
from .ipaddr_valid import \
    resource_fields, resource_fields_ref, resource_fields_wrap, \
    field_inputs, field_inputs_ref, field_inputs_wrap

# our dir structure is just like: module/{modulename}/feature
moduleName = os.path.dirname(__file__).rsplit(os.path.sep, 1)[1]
limit = platform_model_config[moduleName][__heads__]
max = limit['max']

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
    """entry point about '/rest/policies/sec'
        when user do below actions:
        put/getone
    """

    def __init__(self):
        pass

    #@marshal_with(task_list_format)
    def put(self, id):
        """
            update one record

        @api {put} /rest/objects/ipaddr/:id update a IP Address item
        @apiVersion 0.0.1
        @apiName UpdateIpAddr
        @apiVersion 0.0.1
        @apiGroup objects
        @apiPermission registered user

        @apiParam {Number} id ipdate IP Address ID.
        
        @apiDescription
        todo validation<br />
        todo certificate with cookies / oauth 2.0

        @apiParam {Object}   ipaddrs       List of IP Addresses.
        @apiParam {String{..16}}   ipaddrs.addr1 1st IP Address.
        @apiParam {String{..16}}   ipaddrs.addr2 2ed IP Address.
        @apiParam {String{..255}}   [ipaddrs.description] this items's description.
        @apiParam {String="IPv4","IPv6"}   ipaddrs.ipVersion IP Address version.
        @apiParam {String{..50}}   ipaddrs.name items uniq name for record.
        @apiParam {String="Single","Range","Subnet"}   ipaddrs.type IP Address type, the possible values are 'Single', 'Range', 'Subnet'.
        @apiExample Example usage:
           BODY=$(cat <<'EOF'
             {
               "ipaddr" : {
               "name" : "test-ipaddr-${i}8",
               "type" : "Single",
               "ipVersion" : "IPv4",
               "addr1" : "1.1.1.1",
               "description" : "xxx"
             }
           }
           EOF
           );
             
        curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddr/7
        
        @apiSuccess {Object}   ipaddrs       List of IP Addresses.
        @apiSuccess {String}   ipaddrs.addr1 1st IP Address.
        @apiSuccess {String}   ipaddrs.addr2 2ed IP Address.
        @apiSuccess {String}   ipaddrs.description this items's description.
        @apiSuccess {Number}   ipaddrs.id index in database.
        @apiSuccess {String}   ipaddrs.ipVersion IP Address version.
        @apiSuccess {String}   ipaddrs.name items uniq name for record.
        @apiSuccess {String}   ipaddrs.type IP Address type, the possible values are 'Single', 'Range', 'Subnet'.

        @apiError CE_INVALID_PARAM invalid parameter
        @api {put} /rest/objects/ipaddr/:id
        @apiErrorExample {json} we use invalid member type1 in request body
           BODY=$(cat <<'EOF'
             {
               "ipaddr" : {
               "name" : "test-ipaddr-${i}8",
               "type1" : "Single",
               "ipVersion" : "IPv4",
               "addr1" : "1.1.1.1",
               "description" : "xxx"
             }
           }
           EOF
           );
             
           curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddr/7
           ================================================
           HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2001,
               "message": "ValueError('[type]: (type Valid Error) Missing required parameter in dataDict, error=400: Bad Request',)"
           }

        @apiError CE_NAME_CONFLICT name conflict
        @api {post} /rest/objects/ipaddr/:id 
        @apiErrorExample {json} we use duplicate name.
            BODY=$(cat <<'EOF'
             {
               "ipaddr" : {
               "name" : "test-ipaddr-${i}8",
               "type" : "Single",
               "ipVersion" : "IPv4",
               "addr1" : "1.1.1.1",
               "description" : "xxx"
             }
           }
           EOF
           );
             
           curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddr/7
           ================================================
           HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2004,
               "message": "IntegrityError('(sqlite3.IntegrityError) UNIQUE constraint failed: objects_ipaddrs.name',)"
           }

        @apiError CE_NOT_EXIST item not found
        @api {get} /rest/objects/ipaddr/:id
        @apiErrorExample {json} we use not exist id
           curl -X PUT -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddr/17
            
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


        try:
            checkInputIsValid(self.args)
        except Exception as error:
            return error.args


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
        @api {get} /rest/objects/ipaddr/:id get one IP address item.
        @apiName GetIpAddr
        @apiVersion 0.0.1
        @apiGroup objects
        @apiPermission registered user
        
        @apiDescription
        todo validation
        
        @apiParam {Number} id IP Address item id.

        @apiExample Example usage:
        curl -i http://localhost/rest/objects/ipaddr/7
         
        @apiSuccess {Object[]} ipaddrs       List of IP Addresses.
        @apiSuccess {String}   ipaddrs.addr1 1st IP Address.
        @apiSuccess {String}   ipaddrs.addr2 2ed IP Address.
        @apiSuccess {String}   ipaddrs.description this items's description.
        @apiSuccess {Number}   ipaddrs.id index in database.
        @apiSuccess {String}   ipaddrs.ipVersion IP Address version.
        @apiSuccess {String}   ipaddrs.name items uniq name for record.
        @apiSuccess {String}   ipaddrs.type IP Address type, the possible values are 'Single', 'Range', 'Subnet'.

        @apiError CE_INVALID_PARAM invalid parameter
        @api {get} /rest/objects/ipaddr/:id
        @apiErrorExample {json} we use invalid parameter pages
            curl -X GET -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddr/7?pages=1
            ================================================
            HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2001,
               "message": "{'pages'}"
           }
        
        @apiError CE_NOT_EXIST item not found
        @api {get} /rest/objects/ipaddr/:id
        @apiErrorExample {json} we use not exist id
            curl -X GET -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddr/17
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

class ObjectIpaddrs(Resource):
    """entry point about '/rest/policies/sec'
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

        super(ObjectIpaddrs, self).__init__()

    def get(self):
        """Get all data, getall

         @api {get} /rest/objects/ipaddrs Read IP Addresses
         @apiVersion 0.0.1
         @apiName GetIpAddrs
         @apiVersion 0.0.1
         @apiGroup objects
         @apiPermission registered user
         
         @apiDescription
         todo validation
         
         @apiParam {Number=0, 25, 50, 100} [itemsPerPage=25] items for each request.
         @apiParam {Number} [page=1] page you want to request from, start with 1.
         @apiParam {String="name", "description"} [orderBy=name] the items order by column you specified.
         @apiParam {String="true", "false"} [desc=false] the items order by descending or asceding order.

         
         @apiExample Example usage:
         curl -i http://localhost/rest/objects/ipaddrs?itemsPerPage=50&page=1&orderBy=name&desc=true
         
         @apiSuccess {Number}   total         total items for pagination.
         @apiSuccess {String}   orderBy       the items order by column you specified.
         @apiSuccess {Number}   page          page you want to request from, start with 1.
         @apiSuccess {Number}   itemsPerPage  items for each request.
         @apiSuccess {String}   desc          the items order by descending or asceding order.
         @apiSuccess {Object[]} ipaddrs       List of IP Addresses.
         @apiSuccess {String}   ipaddrs.addr1 1st IP Address.
         @apiSuccess {String}   ipaddrs.addr2 2ed IP Address.
         @apiSuccess {String}   ipaddrs.description this items's description.
         @apiSuccess {Number}   ipaddrs.id index in database.
         @apiSuccess {String}   ipaddrs.ipVersion IP Address version.
         @apiSuccess {String}   ipaddrs.name items uniq name for record.
         @apiSuccess {String}   ipaddrs.type IP Address type, the possible values are 'Single', 'Range', 'Subnet'.

         @apiError CE_INVALID_PARAM invalid parameter
         @api {get} /rest/objects/ipaddrs
         @apiErrorExample {json} we use invalid parameter pages
            curl -i http://localhost/rest/objects/ipaddrs?pages=1
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

         @api {post} /rest/objects/ipaddrs Create a IP Address item
         @apiVersion 0.0.1
         @apiName CreateIpAddr
         @apiVersion 0.0.1
         @apiGroup objects
         @apiPermission registered user
         
         @apiDescription
         todo validation <br/>
         todo certificate with cookies / oauth 2.0 <br/>
         todo muti-create

         @apiParam {Object}   ipaddrs       List of IP Addresses.
         @apiParam {String{..16}}   ipaddrs.addr1 1st IP Address.
         @apiParam {String{..16}}   ipaddrs.addr2 2ed IP Address.
         @apiParam {String{..255}}   [ipaddrs.description] this items's description.
         @apiParam {String="IPv4","IPv6"}   ipaddrs.ipVersion IP Address version.
         @apiParam {String{..50}}   ipaddrs.name items uniq name for record.
         @apiParam {String="Single","Range","Subnet"}   ipaddrs.type IP Address type, the possible values are 'Single', 'Range', 'Subnet'.
         @apiExample Example usage:
            BODY=$(cat <<'EOF'
              {
                "ipaddr" : {
                "name" : "test-ipaddr-${i}8",
                "type" : "Single",
                "ipVersion" : "IPv4",
                "addr1" : "1.1.1.1",
                "description" : "xxx"
              }
            }
            EOF
            );
              
         curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddrs
         
         @apiSuccess {Object}   ipaddrs       List of IP Addresses.
         @apiSuccess {String}   ipaddrs.addr1 1st IP Address.
         @apiSuccess {String}   ipaddrs.addr2 2ed IP Address.
         @apiSuccess {String}   ipaddrs.description this items's description.
         @apiSuccess {Number}   ipaddrs.id index in database.
         @apiSuccess {String}   ipaddrs.ipVersion IP Address version.
         @apiSuccess {String}   ipaddrs.name items uniq name for record.
         @apiSuccess {String}   ipaddrs.type IP Address type, the possible values are 'Single', 'Range', 'Subnet'.

         @apiError CE_INVALID_PARAM invalid parameter
         @api {post} /rest/objects/ipaddrs 
         @apiErrorExample {json} we use invalid parameter pages
            BODY=$(cat <<'EOF'
              {
                "ipaddr" : {
                "name" : "test-ipaddr-${i}8",
                "type1" : "Single",
                "ipVersion" : "IPv4",
                "addr1" : "1.1.1.1",
                "description" : "xxx"
              }
            }
            EOF
            );
              
            curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddrs
            ================================================
            HTTP/1.0 400 BAD REQUEST
            {
                "errorId": 2001,
                "message": "ValueError('[type]: (type Valid Error) Missing required parameter in dataDict, error=400: Bad Request',)"
            }

         @apiError CE_NAME_CONFLICT name conflict
         @api {post} /rest/objects/ipaddrs 
         @apiErrorExample {json} we use duplicate name.
             BODY=$(cat <<'EOF'
              {
                "ipaddr" : {
                "name" : "test-ipaddr-${i}8",
                "type" : "Single",
                "ipVersion" : "IPv4",
                "addr1" : "1.1.1.1",
                "description" : "xxx"
              }
            }
            EOF
            );
              
            curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddrs
            ================================================
            HTTP/1.0 400 BAD REQUEST
            {
                "errorId": 2004,
                "message": "IntegrityError('(sqlite3.IntegrityError) UNIQUE constraint failed: objects_ipaddrs.name',)"
            }

         @apiError CE_EXCEED_LIMIT exceed max limit
         @api {post} /rest/objects/ipaddrs 
         @apiErrorExample {json} we create item exceed max.
            BODY=$(cat <<'EOF'
              {
                "ipaddr" : {
                "name" : "test-ipaddr-${i}8",
                "type" : "Single",
                "ipVersion" : "IPv4",
                "addr1" : "1.1.1.1",
                "description" : "xxx"
              }
            }
            EOF
            );
              
            curl -X POST -H "mTag: xx" -H "Content-Type:application/json" -d "${BODY}" http://localhost/rest/objects/ipaddrs
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


        try:
            checkInputIsValid(self.args)
        except Exception as error:
            return error.args


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
        @api {delete} /rest/objects/ipaddrs delete IP address items.
        @apiName DelIpAddrs
        @apiVersion 0.0.1
        @apiGroup objects
        @apiPermission registered user
        
        @apiDescription
        todo validation
        
        @apiParam {String{..255}} [ids] the items id seperate with common

        @apiExample Example usage:
        curl -X DELETE -v -b $COOKIES -H "Content-Type:application/json" http://localhost/rest/objects/ipaddrs?id=1,2,3
        ================================================
        HTTP/1.0 204 NO CONTENT
         

        @apiError CE_INVALID_PARAM invalid parameter
        @api {delete} /rest/objects/ipaddrs
        @apiErrorExample {json} we use invalid parameter pages
        curl -X DELETE -v -b $COOKIES -H "Content-Type:application/json" http://localhost/rest/objects/pages?id=1,2,3
        ================================================
            HTTP/1.0 400 BAD REQUEST
           {
               "errorId": 2001,
               "message": "param `ipaddrs` not found"
           }
        
        @apiError CE_NOT_EXIST item not found
        @api {delete} /rest/objects/ipaddr
        @apiErrorExample {json} we use not exist id
        curl -X DELETE -v -b $COOKIES -H "Content-Type:application/json" http://localhost/rest/objects/pages?id=7,8,9
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
