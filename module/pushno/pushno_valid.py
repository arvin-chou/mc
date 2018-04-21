# -*- coding: utf-8 -*-

from utils import fields
from utils import validate

from module.common import GetResource
from module.common import field_inputs_wrap as _field_inputs_wrap
from module.common import field_inputs_ref as _field_inputs_ref
from module.common import field_inputs as _field_inputs
from module.common import field_inputs_wrap_head

# for serialize
from .__init__ import \
        __pushno_head__ as __head__, \
        __pushno_heads__ as __heads__

field_inputs = {}
field_inputs_send = {}
field_inputs_user = {}
field_inputs_wrap = _field_inputs_wrap.copy()

field_inputs['id'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }

field_inputs['business_id'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }

field_inputs['user_id'] =  {
        'validator': validate.natural(),
        'required': True,
        'type': fields.Integer()
        }

field_inputs['type'] =  {
        'validator': validate.natural(),
        'required': True,
        'type': fields.Integer()
        }

field_inputs['dev_id'] =  {
        'type': fields.String(),
        'required': True,
        'validator': validate.str_range(argument={'low': 1, 'high': 255})
        }

field_inputs_wrap['orderBy'] = {
        'validator': validate.str_in_list(
            default='user_id',
            argument=['user_id'],
            ),
        'type': fields.String(default='user_id'),
        }

field_inputs_post = field_inputs.copy()


field_inputs_send['title'] =  {
        'type': fields.String(),
        'required': True,
        'validator': validate.str_range(argument={'low': 1, 'high': 255})
        }
field_inputs_send['message'] =  {
        'type': fields.String(),
        'required': True,
        'validator': validate.str_range(argument={'low': 1, 'high': 255})
        }
field_inputs_send['uri'] =  {
        'type': fields.String(),
        'required': True,
        'validator': validate.str_range(argument={'low': 1, 'high': 255})
        }
field_inputs_send['gcm_nr'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }
field_inputs_send['apns_nr'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }

resource_fields, resource_fields_post, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_post, field_inputs_wrap, field_inputs_wrap_head)
resource_fields_send, resource_fields_post, resource_fields_wrap = GetResource(
        field_inputs_send, field_inputs_post, field_inputs_wrap, field_inputs_wrap_head)
