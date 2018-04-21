# -*- coding: utf-8 -*-

import json
from functools import reduce
from flask import request
from werkzeug.exceptions import BadRequest
#from utils import reqparse, abort, Resource, fields, marshal, inputs
from utils import inputs
from utils import validate
from flask.ext.restful import reqparse, abort, Resource, fields, marshal
from sqlalchemy.inspection import inspect
#from flask.ext.restful import reqparse, abort, Resource, fields, marshal, inputs
from config.config import _logging

# for eval, dynamic create class
from .object.model import ObjectsIpaddrs

_reqparse = reqparse.RequestParser()
logger = _logging.getLogger(__name__)


def add_argument(reqparse, field_inputs={}, location=['dataDict'], *args, **kwargs):
    for k, v in field_inputs.items():
        print(", c", v.get('validator', {}), v)
        _type = v.get('type', str)
        # i have no idea why we must pass action=False
        # in it to get Multiple Values & Lists
        reqparse.add_argument(k, type = _type, location = location,
            required=v.get('required', False),
            argument=v.get('validator', {}).get('argument'),
            help='{} Valid Error'.format(k),
            case_sensitive=True,
            action=False, *args, **kwargs)

def _add_argument(reqparse, request, field_inputs={},
                  location=['dataDict'], *args, **kwargs):
    """only support 1-layer parsing
    """
#print ('type of field_inputs is ', type(field_inputs),
#           [(type(x), 1, x.container, x.container.nested, x.attribute, x.container.__dict__.keys())
#            for x in field_inputs if type(field_inputs) is set])
##    items = next(iter(field_inputs)).container.nested.items() if type(field_inputs) is set\
#        else field_inputs.items()
#
#    _location = location
#    for k, v in items:
    for k, v in field_inputs.items():
#        # i have no idea why we must pass action=False
#        # in it to get Multiple Values & Lists
        #print ('v=', v, 'k=', k, type(v.get('type', str)))
        _type = v.get('validator', str)
#        key = location[0]
#        _key = location[::]
#        _key.append(k)
#
        if type(_type) is set:
            continue
#        if type(_type) is set:
#            # fields.List, flattern it
#            _add_argument(reqparse, request, v['type'],
#                          location=_key, *args, **kwargs)
#
##print (type(v.get('type', str)), k, 'is set')
#        if reduce(lambda v1, v2: v1 and v2,
#                  map(lambda v: v in ['dataDict'], location)):
#            # first head
#            pass
#        else:
#            print('before key:', key, v, k, location, 'xxx', getattr(request,location[0]))
#            if type(getattr(request,location[0])[location[1]]) is list:
#              # move each of Nested value to the 1st layer
#              print('---', getattr(request,location[0])[location[1]])
#              for _k, _v in enumerate(getattr(request,location[0])[location[1]]):
#                __key = _key[::]
#                __key.append(str(_k))
#                print('in =', _k, _v, (__key))
#                setattr(request, ''.join(__key), _v)
#                _location = [''.join(__key)]
#                print('after set, key:', __key, getattr(request, ''.join(__key)))
#
#        print('reqparse.add_argument.location = ', _location,
#            'k=', k)
#
#        if type(_type) is not set:
#          reqparse.add_argument(k, type = _type, location = _location,
#              required=v.get('required', False),
#              help='{} Valid Error'.format(k),
#              case_sensitive=True,
#              action=False, *args, **kwargs)
        reqparse.add_argument(k, type = _type, location = location,
            required=v.get('required', False),
            help='{} Valid Error'.format(k),
            case_sensitive=True,
            action=False, *args, **kwargs)


"""structure for marshal and reqparse use, the structure like below:
    {
        'id': {
            'type': fields.Integer(),
            'validate': validate.natural()
        },
        'name: {
            'type': fields.String(),
            'validate': validate.str_range(argument={'low': 1, 'high': 64}),
        }
    }

    we only support two-layer structure in these project, if u want to custimize,
    plz use api by hand.
    the attribute type indicate that what type flask should response to via marshal
    function with json format.
    the attribute validate indicate that what the data we recieved and parsed by
    specific validator, if parse error, it usually retrun error code 2001.

"""

field_inputs = {
    'id': {
        'validator': validate.natural(),
        'type': fields.Integer()
        },
    'name': {
        'type': fields.String(),
        'validator': validate.str_range(argument={'low': 1, 'high': 64}),
        #'required': True,
        #'validator': {'name': inputs.wrap_str_range, 'argument': '1,64'}
        },
    'description': {
        'type': fields.String(),
        'validator': validate.str_range(argument={'low': 0, 'high': 254}),
        #'validator': {'name': inputs.wrap_str_range, 'argument': '0,254'}
        },
}

field_inputs_wrap = {
    'total': {
        'type': fields.Integer()
        }, # for output
    'itemsPerPage': {
        'validator': validate.int_in_list( default=25, argument=[0, 25, 50, 100]),
        'type': fields.Integer(default=25),
    #'itemsPerPage': {'type': fields.Integer(default=25),
            #,'validator':
            #         {'name':
            #          inputs.int_in_list, 'argument': [0, 25, 50, 100]},
            #         },
            },
    'page': {
        'validator': validate.natural(default=1),
        'type': fields.Integer(default=1),
        #    'validator': {'name': inputs.natural}},
    #'orderBy': {'type': fields.String(default='login'),
    },
    'orderBy': {
        'validator': validate.str_in_list(
                    default='login',
                    argument=['name', 'login', 'email', 'description'],
                ),
        'type': fields.String(default='name'),
            #'validator': {'name': inputs.str_in_list,
            #    'argument': ['name', 'login', 'email', 'description']}},
            },
    #'desc': {'type': fields.Boolean(default=False),
    'desc': {
        'validator': validate.Boolean(default=False),
        'type': fields.Boolean(default=False),
        }
        #    'validator': {'name': inputs.boolean}}
}

field_inputs_ref = {
    'secpolicies': {'type': fields.List(fields.Nested({
        'id': {'type': fields.Integer()},
        'name': {'type': fields.String()},
        }))}
}

def GetResource(field_inputs={}, field_inputs_ref={}, field_inputs_wrap={}, __heads__=''):
    """only support tow layer, such as
    head: {
        name: 'xxx',
        foo: [ {id: 1, name:'test'}, ... ]
    }
    """

    resource_fields = {}
    for k,v in field_inputs.items():
        if type(v['type']) is not set:
            resource_fields[k] = v['type']
        else:
            resource_fields[k] = {}
            for _k, _v in next(iter(v['type'])).container.nested.items():
                resource_fields[k][_k] = _v['type']
    resource_fields_ref = dict((k, v['type']) for k,v in field_inputs_ref.items())
    resource_fields_wrap = dict((k, v['type']) for k,v in field_inputs_wrap.items())
    resource_fields_wrap[__heads__] = fields.List(fields.Nested(resource_fields))
    return resource_fields, resource_fields_ref, resource_fields_wrap

def GetRequestArgs(head, field_inputs, dataDict=None):
    """checking request parameters/body were validated

    Examples::
        {
        'itemsPerPage': {
        'type':
            validate.int_in_list(default=25, argument=[0, 25, 50, 100])
            }
            }
        try:
        except Exception as error:

    :param Str head: the request body head that we wrap. if it is None which
    means it want to check parameters rather than body.
    :param Dict field_inputs: The recieve data struct you expected,
     and each of attributes are send to add_argument to parse.
    :param Str dataDict: The key that indicate add_argument to get all request
    data.
    :returns: The Origin recieve json data, The Dict the user request if valid.
    :raises: ValueError


    """

    try:
        dataDict = request.get_json() if dataDict == None else dataDict
        request.dataDict = dataDict if head == None else dataDict[head]
        _add_argument(_reqparse, request, field_inputs)
        args = _reqparse.parse_args()

    except Exception as error:
        if error == type(BadRequest):
            raise ValueError('maybe json format error')

        raise ValueError('{}, error={}'.format(error.data['message'], error))

    return request.dataDict, args



def GetRequest(head, field_inputs, dataDict=None):
    """
        checking request body is validated
    """

    try:
        dataDict = request.get_json() if dataDict == None else dataDict
        request.dataDict = dataDict if head == None else dataDict[head]
        add_argument(_reqparse, field_inputs)
        args = _reqparse.parse_args()

    except Exception as error:
        if error == type(BadRequest):
            raise ValueError('maybe json format error')

        raise ValueError('{}, error={}'.format(error.args, error))

    return args

def SerialGroupOutput(r, resource_fields,
        groupname='ipgroup', objname='ipaddrs',
        omitKeys=['id']):
    """The actions post/put serialized output.

    We always output group information with its objects, such as:
    {
        "ipgroup": {
            "description": "test",
            "id": 37,
            "ipaddrs": [
                {
                    "id": 22
                },
                ... balabala ...
            ],
            "name": "testtest42"
        }
    }

    Examples::
        data, field = SerialGroupOutput(r, resource_fields=resource_fields)
        return marshal(data, field), 200

    :param sqlalchemy r or iterator: The query result prepares to output,
        we support single or iterator record.
    :param Dict resource_fields: The dictionary that we use to validate output.
    :param Str groupname: The first layer of output, it is usually given by group name.
    :param Str objname: The second layer of output, it is usually given by objects name.
    :param list omitKeys: The keys you want to output,
        the keys list copy from resource_fields.
    :returns: Two attributes, data and field for Marshal outputs.
    :rtype: A tuple (data, field)
    """

    args = {}
    args[groupname] = {}
    args[groupname][objname] = []

    _resource_fields_wrap = {}
    _resource_fields = resource_fields.copy()
    __resource_fields = resource_fields.copy()

    for col in resource_fields.keys():
        if col not in omitKeys:
            del __resource_fields[col]

    _resource_fields[objname] = fields.List(
            fields.Nested(__resource_fields))
    _resource_fields_wrap[groupname] = fields.Nested(_resource_fields)


    try:
        # for iterable, get all
        iter(r)
        args = []
        _resource_fields_wrap = _resource_fields
        for _r in r:
            _args = {}
            _args[objname] = []
            for col in _r.__table__.columns.keys():
                _args[col] = getattr(_r, col)

            for __r in getattr(_r, objname):
                ___r = dict((col, getattr(__r, col)) for col in omitKeys)

                _args[objname].append(___r)
            args.append(_args)

    except (TypeError) as error:
        # get one
        #print r, 'is not iterable'
        for col in r.__table__.columns.keys():
            args[groupname][col] = getattr(r, col)

        for _r in getattr(r, objname):
            __r = dict((col, getattr(_r, col)) for col in omitKeys)

            args[groupname][objname].append(__r)

    return args, _resource_fields_wrap

def PrepareGroupORM(r, obj, mapping, objname, request, mappingattr='mapping'):
    """Prepare data assign to orm

    Examples::
        try:
            r = PrepareGroupORM(r, obj, mapping, obj__heads__, self.args.items())
        except Exception as error:
            return omitError(ErrorMsg=repr(error)), 400

        db.session.merge(r)

    :param sqlalchemy r: The sqlalchemy orm prepares to save.
    :param sqlalchemy obj: The sqlalchemy orm prepares valid that child is exist.
    :param sqlalchemy mapping: The sqlalchemy orm that relationship with r.
    :param Str objname: The second layer that we create one to many, which means
        one group maps many objs.
    :param Dict request: The data reqest from end user want to create.
    :param Str mappingattr: The relationship attribute we want to create.
    :returns: The sqlalchemy ORM if valid.
    :raises: ValueError
    """


    try:
        for k, v in request:
            if v != None :
                if k != objname:
                    setattr(r, k, v)
                else:
                    _mapping = []
                    if isinstance(v, str):
                        v = [v]
                        # when pass one record such as [{"id": "1"}], it could be
                        # deserialized to string type like '{"id": "1"}'
                        # rather than `list` type.

                    for _v in v:
                        objId = json.loads(_v.replace('\'', '"'))['id']

                        if not obj.query.filter(obj.id == objId).scalar():
                        # we make sure atomic
                        # that if one of mapping not found, we exist immediantly.
                            raise ValueError('objId({}) not exist in db'.format(objId))

                        _mapping.append(mapping(objId, r.id))

                    setattr(r, mappingattr, _mapping)

    except Exception as error:
        raise ValueError('deserialize error, error={}'.format(error))

    return r


def ExtraParamsIsValid(requestArgsSet=(), validSet=()):
    if 0 == len(validSet):
        if 0 != len(requestArgsSet):
            return False
    else:
        if not requestArgsSet.issubset(validSet):
            return False

    return True

def PrepareObjORM(r, request):
    """Prepare data assign to orm

    Examples::
        try:
            r = PrepareObjORM(r, args.items())
        except Exception as error:
            return omitError(ErrorMsg=repr(error)), 400

        db.session.merge(r)

    :param sqlalchemy r: The sqlalchemy orm prepares to save.
    :param Dict request: The data reqest from end user want to create.
    :returns: The sqlalchemy ORM if valid.
    :raises: ValueError
    """

    try:
        for k, v in request:
            if type(v) is list:
#print('r\'s :', inspect(r).attrs.keys())
#print('r\'s :', inspect(r).mapper.relationships.__contains__)
                print('r\'s :', inspect(r).mapper.relationships.__weakref__)
                print('r\'s :', inspect(r).mapper.relationships._data)
                print('r\'s :', inspect(r).mapper.relationships._data[k + 'Mapping'])
                print('r\'s :', dir(inspect(r).mapper.relationships._data[k + 'Mapping']))
                print('r\'s :', (inspect(r).mapper.relationships._data[k + 'Mapping'].argument()))
                print('r\'s :', (inspect(r).mapper.relationships._data[k + 'Mapping'].class_attribute))
                print('r\'s :', (inspect(r).mapper.relationships._data[k].backref))
                print('r\'s relationships:', dir(inspect(r).mapper.relationships), dir(inspect(r).mapper))
                # get relationship class and its backref/argument
                relationshipsInstance = \
                  inspect(r).mapper.relationships._data[k + 'Mapping']
                argument = relationshipsInstance.argument()
                backref = eval(relationshipsInstance.backref)()

#backref = inspect(r).mapper.relationships._data[k].backref

#                        _mapping.append(mapping(objId, r.id))

                _mapping = []
                for _v in v:
#constructor = eval(backref)()
                  id =  _v['id']
                  if not backref.query.filter_by(id = id).scalar():
                    # we make sure atomic
                    # that if one of mapping not found, we exist immediantly.
                    raise ValueError('{} id ({}) not exist in db'.\
                        format(backref.__class__, id))

                  _mapping.append(argument(r.id, id))
#for __k, __v in _v:
#print('list', k, r, _v, getattr(r, k))
#setattr(constructor, __k, __v)

                setattr(r, k + 'Mapping', _mapping)
#getattr(r, k).append(constructor)
            elif v is not None:
                setattr(r, k, v)

    except Exception as error:
        raise ValueError('deserialize error, error={}'.format(error))

    return r


def SerialObjOutput(r, resource_fields,
                    objname='secpolicies',
                    omitKeys=['id']):
    """The actions post/put serialized output.

    We always output group information with its objects, such as:
    {
        "ipgroup": {
            "description": "test",
            "id": 37,
            "ipaddrs": [
                {
                    "id": 22
                },
                ... balabala ...
            ],
            "name": "testtest42"
        }
    }

    Examples::
        data, field = SerialObjOutput(r, resource_fields=resource_fields)
        return marshal(data, field), 200

    :param sqlalchemy r or iterator: The query result prepares to output,
        we support single or iterator record.
    :param Dict resource_fields: The dictionary that we use to validate output.
    :param Str objname: The second layer of output,
    it is usually given by objects name.
    :param list omitKeys: The keys you want to output,
        the keys list copy from resource_fields.
    :returns: Two attributes, data and field for Marshal outputs.
    :rtype: A tuple (data, field)
    """

    # make marshal template
    args = {}
    args[objname] = {}

    _resource_fields_wrap = {}
    _resource_fields = resource_fields.copy()
    #__resource_fields = resource_fields.copy()

    #for col in resource_fields.keys():
    #    if col not in omitKeys:
    #        del __resource_fields[col]

    #_resource_fields[objname] = fields.List(
    #    fields.Nested(__resource_fields))

    #_resource_fields['srcIpAddrs'] = fields.List(
    #        fields.Nested(__resource_fields))
    #_resource_fields_wrap[objname] = fields.Nested(_resource_fields)
    _resource_fields_wrap[objname] = fields.Nested(resource_fields)

    try:
        # for iterable, get all
        iter(r)
        args = []
        _resource_fields_wrap = _resource_fields
        for _r in r:
            _args = {}
            _args[objname] = []
            for col in _r.__table__.columns.keys():
                _args[col] = getattr(_r, col)

            for __r in getattr(_r, objname):
                ___r = dict((col, getattr(__r, col)) for col in omitKeys)

                _args[objname].append(___r)
            args.append(_args)

        outer = marshal(args, _resource_fields_wrap)

    except (TypeError) as error:
        # get one
        for col in r.__table__.columns.keys():
            # first layer
            args[objname][col] = getattr(r, col)
            #print ('type of {} = {}'.format(col, type(getattr(r, col))))

        outer = marshal(args, _resource_fields_wrap)
        for k, v in resource_fields.items():
            if isinstance(v, dict):
                #print('resource_fields.keys', k, type(v))
                args[objname][k] = []

                for _r in getattr(r, k):
                    __r = dict((col, getattr(_r, col)) for col in
                            _r.__table__.columns.keys())

                    args[objname][k].append(__r)

                # if inner layer has the same attribute with outer layer, marshal will be
                # ignore last layer :(, so we must pre-marshal inner layer and join to
                # the outer
                outer[objname].update({k:
                        marshal(args[objname][k], resource_fields[k])})


        #args[objname]['srcIpAddrs'] = []
        #for _r in getattr(r, 'srcIpAddrs'):
        #    for col in _r.__table__.columns.keys():
        #        print(_r, col, getattr(_r, col), '_r')
        #    __r = dict((col, getattr(_r, col)) for col in  _r.__table__.columns.keys())

        #    args[objname]['srcIpAddrs'].append(__r)
        #    # if inner layer has the same attribute with outer layer, marshal will be
        #    # ignore last layer :(, so we must pre-marshal inner layer and join to
        #    # the outer

        #outer[objname].update(srcIpAddrs=
        #        marshal(args[objname]['srcIpAddrs'], resource_fields['srcIpAddrs']))
        #print('Marshal,',
        #        'outer=', outer,
        #        #dir(marshal(args[objname]['srcIpAddrs'], resource_fields['srcIpAddrs'])))
        #        [[k, v] for k, v in (marshal(args[objname]['srcIpAddrs'], resource_fields['srcIpAddrs']))])

        ##_resource_fields['srcIpAddrs'] = next(iter(_resource_fields['srcIpAddrs']))
        #print('args= ',args)
        #print ('_resource_fields_wrap=', _resource_fields_wrap,
        #        '_resource_fields_wrap[{}]={}'.format(objname,
        #            _resource_fields_wrap[objname]),
        #        '_resource_fields=', _resource_fields,
        #        marshal(args, _resource_fields_wrap))
    return outer

    #return marshal(args, _resource_fields_wrap)

