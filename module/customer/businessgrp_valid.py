# -*- coding: utf-8 -*-

from utils import fields
from utils import validate

from module.common import GetResource
from module.common import field_inputs_wrap as _field_inputs_wrap
from module.common import field_inputs_ref as _field_inputs_ref
from module.common import field_inputs as _field_inputs

# for serialize
from .__init__ import __customer_businessgrp_head__ as __head__, \
        __customer_businessgrp_heads__ as __heads__, \
        __customer_business_head__ as __obj__head__, \
        __customer_business_heads__ as __obj__heads__

field_inputs = _field_inputs.copy()
field_inputs_ref = _field_inputs_ref.copy()
field_inputs_wrap = _field_inputs_wrap.copy()

#
# customise by spec.
#
field_inputs_wrap['orderBy']['type'] = fields.String(default='name')
field_inputs_wrap['orderBy']['validator'] = \
        validate.str_in_list(
                default='name',
                argument=['name', 'description'],
                )

resource_fields, resource_fields_ref, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_ref, field_inputs_wrap, __heads__)

# not extend to resource_fields
field_inputs['name']['required'] = True
field_inputs[__obj__heads__] = {
        'type': { fields.List(fields.Nested({
            'id': {'type': fields.Integer(), 'required': True},
            'name': {'type': fields.String()}
            }))
            }
        }



