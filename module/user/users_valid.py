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
        __user_users_head__ as __head__

field_inputs = {}
field_inputs_user = {}
field_inputs_wrap = _field_inputs_wrap.copy()
field_inputs['id'] =  {
        'validator': validate.natural(),
        #'required': True,
        'type': fields.Integer()
        }

field_inputs['name'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
        'type': fields.String(default="")
        }
#field_inputs['sid'] = {
#        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
#        'type': fields.String()
#        }
# TODO: validator with email
field_inputs['login'] =  {
        'validator': validate.email(),
        'type': fields.String(default="")
        }
#field_inputs['email'] =  {
#        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
#        'type': fields.String(default="")
#        }
#field_inputs['preferences'] =  {
#        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
#        'type': fields.String(default="")
#        }
#field_inputs['clientIp'] =  {
#        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
#        'type': fields.String(default="")
#        }
#field_inputs['admingroup'] =  {
#        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
#        'type': fields.String(default="")
#        }

field_inputs['access_token'] =  {
        'type': fields.String(default=''),
        'validator': validate.str_range(argument={'low': 1, 'high': 255})
        }

field_inputs['passHash'] =  {
        'type': fields.String(default=''),
        'validator': validate.str_range(argument={'low': 1, 'high': 255})
        }

field_inputs_post = field_inputs.copy()
resource_fields, resource_fields_post, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_post, field_inputs_wrap, field_inputs_wrap_head)
