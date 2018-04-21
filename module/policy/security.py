# -*- coding: utf-8 -*-

import traceback
import os.path

from flask import request
from sqlalchemy import exc
from flask.ext.restful import Resource, fields, marshal, reqparse

from utils.error import omitError
from utils import validate

from module.common import GetResource,\
       GetRequestArgs, GetRequest, ExtraParamsIsValid,\
       SerialGroupOutput, PrepareGroupORM,\
       SerialObjOutput, PrepareObjORM
from module.common import field_inputs_wrap as _field_inputs_wrap
from module.common import field_inputs_ref as _field_inputs_ref
from module.common import field_inputs as _field_inputs


from .model import PoliciesSecurities as sec

#
# predefind validate in each column, please ref to MRQ
#
from .__init__ import __policies_security_head__ as __sec_head__, \
        __policies_security_heads__ as __sec_heads__\

#
# init logger
#
from config.config import _logging, api, app, db, platform_model_config
logger = _logging.getLogger(__name__)

#
# our dir structure is just like: module/{modulename}/feature
#
moduleName = os.path.dirname(__file__).rsplit(os.path.sep, 1)[1]
limit = platform_model_config[moduleName][__sec_heads__]
max = limit['max']

#
# init validator
#
field_inputs = _field_inputs.copy()
field_inputs_ref = _field_inputs_ref.copy()
field_inputs_wrap = _field_inputs_wrap.copy()
_reqparse = reqparse.RequestParser()


#
# customise by spec.
#

field_inputs_wrap['orderBy']['type'] = validate.str_in_list(
                    default='name',
                    argument=['name', 'type', 'description']
                )
field_inputs['srcIpAddrs'] = {
# type attribute for marshal
        'type': { fields.List(fields.Nested({
            'id': {'type': fields.Integer()},
            'name': {'type': fields.String(attribute='name')}
            }))
            },
# validate attribute for reqparse
        'validator': { fields.List(fields.Nested({
            'id': {'type': validate.natural(default=1), 'required': True},
            'name':{'type': validate.str_range(argument={'low': 1, 'high': 64})}
            }))
            }
        }

field_inputs['srcIpGroups'] = {
# type attribute for marshal
        'type': { fields.List(fields.Nested({
            'id': {'type': fields.Integer()},
            'name': {'type': fields.String(attribute='name')}
            }))
            },
# validate attribute for reqparse
        'validator': { fields.List(fields.Nested({
            'id': {'type': validate.natural(default=1), 'required': True},
            'name':{'type': validate.str_range(argument={'low': 1, 'high': 64})}
            }))
            }
        }


resource_fields, resource_fields_ref, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_ref, field_inputs_wrap, __sec_heads__)

# not extend to resource_fields
field_inputs['name']['required'] = True
#reqparse only support one-layer, so we check it by munual
#twoed_field_inputs = {}
#twoed_field_inputs['srcIpAddrs'] = {
#        'type': { fields.List(fields.Nested({
#            'id': {'type': validate.natural(default=1), 'required': True},
#            'name':{'type': validate.str_range(argument={'low': 1, 'high': 64})}
#            }))
#            }
#        }
#resource_2ed_fields = GetResource(twoed_field_inputs)
#print(resource_fields)
#print(resource_fields, len(resource_fields), resource_2ed_fields, len(resource_2ed_fields))
#resource_fields.update(resource_2ed_fields[0])
#print(resource_fields)

# for global use
mTag = None


class PolicySecurity(Resource):
    """entry point about '/rest/policies/sec/<int:id>'
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
            self.args = GetRequest(__sec_head__, field_inputs)
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        # 2. get orm from db
        r = sec.query.filter(sec.id == id).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST',
                    'id {} not found'.format(id)), 400

        # 3. assign request data to orm
        try:
            r = PrepareGroupORM(r, obj, mapping, __obj__sec_heads__, self.args.items())
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
        return SerialGroupOutput(r, resource_fields=resource_fields), 200
        #data, field = SerialGroupOutput(r, resource_fields=resource_fields)

        #return marshal(data, field), 200

    def get(self, id):
        """
            retreive one record
        """
        r = sec.query.filter(sec.id == id).scalar()

        if r is None:
            return omitError('CE_NOT_EXIST', 'id {} not found'.format(id)), 400

        #data, field = SerialGroupOutput(r, resource_fields=resource_fields,
        #        omitKeys=['id', 'name'])

        #return marshal(data, field), 200
        return SerialGroupOutput(r, resource_fields=resource_fields,
                omitKeys=['id', 'name']), 200


class PolicySecurities(Resource):
    """entry point about '/rest/policies/sec'
        when user do below actions:
        delete/create/getall
    """
    def __init__(self):
        pass

    def get(self):
        """Get all data
        """
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
            print(self.args, 'self.args', resource_fields_wrap)
            self.response = dict(marshal(self.args, resource_fields_wrap).items())

            self.args[__sec_heads__] = []
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        itemsPerPage = self.response['itemsPerPage']
        page = self.response['page']
        orderBy = getattr(sec, self.response['orderBy'])
        isDesc = getattr(orderBy, 'desc' if self.response['desc'] else 'asc')

        r = sec.query.order_by(isDesc())
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
        self.args[__sec_heads__] = data

        _resource_fields_wrap = resource_fields_wrap.copy()
        _resource_fields_wrap[__sec_heads__] = fields.List(fields.Nested(field))

        return marshal(self.args, _resource_fields_wrap), 200

    #@marshal_with(task_list_format)
    def post(self):
        """Create new record, the content recieve from http such as below:

        Cookie: sid=<string>
        mTag: <string>
        Content:
        {
          "secpolicy" : {
            "name" : <string>,
            "interface" : {
              "ifName" : <string>
            },
            "srcIpGroups" : [
            {
              "id" : <long>
            },
            (more IpGroup objects...)
              ],
            "srcIpAddrs" : [
            {
              "id" : <long>
            },
            (more IpAddr objects...)
              ],
            "dstIpGroups" : [
            {
              "id" : <long>
            },
            (more IpGroup objects...)
              ],
            "dstIpAddrs" : [
            {
              "id" : <long>
            },
            (more IpAddr objects...)
              ],
            "vlanGroups" : [
            {
              "id" : <long>
            },
            (more VlanGroup objects...)
              ],
            "vlans" : [
            {
              "id" : <long>
            },
            (more Vlan objects...)
              ],
            "servGroups" : [
            {
              "id" : <long>
            },
            (more ServGroup objects...)
              ],
            "servs" : [
            {
              "id" : <long>
            },
            (more Serv objects...)
              ],
            "userGroups" : [
            {
              "id" : <long>
            },
            (more UserGroup objects...)
              ],
            "schds" : [
            {
              "id" : <long>
            }
            ],
              "ipprofile" : {
                "id" : <long>
              },
              "ipprofileLogOnly" : <boolean>,
              "acprofile" : {
                "id" : <long>
              },
              "acprofileLogOnly" : <boolean>,
              "scprofile" : {
                "id" : <long>
              },
              "scprofileLogOnly" : <boolean>,
              "action" : <string>,
              "logging" : <string>,
              "enabled" : <string>,
              "description" : <string>
          }
        }

        """
        # 1. parsing reqest
        # 1.1 parsing 1st layer reqest
        try:
            orgArgs, self.args = GetRequestArgs(__sec_head__, field_inputs)
        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())

            return omitError(ErrorMsg=repr(error)), 400

        # 1.2 parsing 2ed layer reqest
        #def t(x):
        #    print('ooooo', x, field_inputs[x], type(field_inputs[x]))
        #    return isinstance(field_inputs[x], set)
        try:
            #print(filter(t, field_inputs.keys()),
            #        'xxxx', field_inputs.items(),
            #        dict((k, v) for k, v in field_inputs.items() if isinstance(v['validator'], set)))
            #for k, v in field_inputs.items():
            #    print('bbbbb', v, type(v))
            for v in set((v) for v in set(field_inputs).intersection(orgArgs)
                    if isinstance(field_inputs[v]['validator'], set)):
            #for v in dict((k, v) for k, v in field_inputs.items()
            #        if isinstance(v['validator'], set)):
            #for v in filter(lambda v: isinstance(field_inputs[v], set), field_inputs):
                print('set(field_inputs).intersection(orgArgs)', field_inputs[v], v)
                _type = field_inputs[v]['validator']

                validator = next(iter(_type)).container.nested.items() \
                      if type(_type) is set else _type.items()

                # validate 2ed value
                # if is list, such as [{id: 1, name:2}, {id: 2, name:2}]
                for _k, _v in validator:
                  for __v in orgArgs[v]:
                    if (_v.get('required', False)):
                      _v['type'](__v[_k])

                #print('self.args[v]',self.args.get(v))
                #self.args[v] = [self.args.get(v, None)]
                self.args[v] = self.args[v] if self.args.get(v, False) else []
                self.args[v].append(__v)

        except Exception as error:
            logger.debug('traceback.format_exc(%s)', traceback.format_exc())
            return omitError(ErrorMsg=repr(error)), 400


        logger.debug('parsed args = (%s)', self.args);


        # 2. validate follows spec
        if db.session.query(sec.id).count() > max:
            return omitError('CE_EXCEED_LIMIT', 'limit is {}'.format(max)), 400

        # 3. assign request data to orm
        r = sec()
        try:
            print(type(self.args.items()), self.args.items())
            r = PrepareObjORM(r, self.args.items())
        except Exception as error:
            return omitError(ErrorMsg=repr(error)), 400

        print('self.args.items()=', self.args.items())

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
        return SerialObjOutput(r, resource_fields=resource_fields), 200
        #data, field = SerialObjOutput(r, resource_fields=resource_fields)

        #return marshal(data, field), 200


    def delete(self):
        """multi delete
        """
        try:
            ids = request.args.get(__sec_heads__).split(',')
        except Exception as error:
            return omitError(ErrorMsg='param `{}` not found'.format(__sec_heads__)), 400

        for id in ids:
            try:
                id = inputs.natural(id)
            except Exception as error:
                db.session.rollback()
                return omitError(ErrorMsg='user id `{}` not int'.format(id)), 400

            # it could als cascade delete `online` user
            r = sec.query.filter(sec.id == id).scalar()
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
