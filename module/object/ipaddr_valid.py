# -*- coding: utf-8 -*-

from utils import fields
from utils import validate

from module.common import GetResource
from module.common import field_inputs_wrap as _field_inputs_wrap
from module.common import field_inputs_ref as _field_inputs_ref
from module.common import field_inputs as _field_inputs

# for serialize
from .__init__ import __objects_ipaddr_head__ as __head__, \
        __objects_ipaddr_heads__ as __heads__

field_inputs = _field_inputs.copy()
field_inputs_ref = _field_inputs_ref.copy()
field_inputs_wrap = _field_inputs_wrap.copy()

field_inputs['ipVersion'] =  {
        'type': fields.String(),
        'validator': validate.str_in_list(argument=['IPv4', 'IPv6'])
        }

field_inputs['type'] =  {
        'type': fields.String(),
        'validator': validate.str_in_list(argument=['Single', 'Range', 'Subnet'])
        }

field_inputs['addr1'] =  {
        'type': fields.String(),
        'validator': validate.str_range(argument={'low': 1, 'high': 64})
}

field_inputs['addr2'] =  field_inputs['addr1'].copy()

field_inputs_wrap['orderBy'] = {
        'validator': validate.str_in_list(
            default='name',
            argument=['name', 'email', 'description'],
            ),
        'type': fields.String(default='name'),
        }


resource_fields, resource_fields_ref, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_ref, field_inputs_wrap, __heads__)
