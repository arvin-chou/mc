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
        __customer_comment_head__ as __head__, \
        __customer_comment_heads__ as __heads__, \
        __customer_business_detail_head__ as __head_detail__, \
        __customer_business_detail_rates_head__ as __head_detail_rates__, \
        __customer_business_detail_deals_head__ as __head_detail_deals__, \
        __customer_business_detail_images_url_head__ as __head_detail_images_url__

field_inputs = {}
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
        'type': fields.Integer()
        }

field_inputs['rate'] =  {
        'validator': validate.natural(),
        'required': True,
        'type': fields.Integer()
        }

field_inputs_wrap['orderBy'] = {
        'validator': validate.str_in_list(
            default='rate',
            argument=['rate'],
            ),
        'type': fields.String(default='rate'),
        }

field_inputs_post = field_inputs.copy()

resource_fields, resource_fields_post, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_post, field_inputs_wrap, field_inputs_wrap_head)
