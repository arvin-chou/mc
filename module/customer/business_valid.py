# -*- coding: utf-8 -*-

from utils import fields
from utils import validate

from module.common import GetResource
from module.common import field_inputs_wrap as _field_inputs_wrap
from module.common import field_inputs_ref as _field_inputs_ref
from module.common import field_inputs as _field_inputs

# for serialize
from .__init__ import __customer_business_head__ as __head__, \
        __customer_business_heads__ as __heads__

field_inputs = _field_inputs.copy()
field_inputs_ref = _field_inputs_ref.copy()
field_inputs_wrap = _field_inputs_wrap.copy()

field_inputs['image_url'] =  {
        'type': fields.String(),
        'required': True,
        'validator': validate.str_range(argument={'low': 1, 'high': 255})
        }

field_inputs['cat'] =  {
        'required': True,
        'validator': validate.natural(),
        'type': fields.Integer()
        }

field_inputs['lat'] =  {
        'required': True,
        #'validator': validate.Float(),
        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
        'type': fields.Float()
        }


field_inputs['long'] =  field_inputs['lat'].copy()
field_inputs['deal'] =  field_inputs['cat'].copy()

field_inputs_wrap['orderBy'] = {
        'validator': validate.str_in_list(
            default='name',
            argument=['name', 'description'],
            ),
        'type': fields.String(default='name'),
        }


resource_fields, resource_fields_ref, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_ref, field_inputs_wrap, __heads__)
