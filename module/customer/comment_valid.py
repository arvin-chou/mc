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

field_inputs['content'] =  {
        'type': fields.String(),
        'required': True,
        'validator': validate.str_range(argument={'low': 1, 'high': 255})
        }

field_inputs['id'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }

field_inputs['business_id'] =  {
        'required': True,
        'validator': validate.natural(),
        'type': fields.Integer()
        }

field_inputs['rate'] =  {
        'required': True,
        'validator': validate.natural(),
        'type': fields.Integer()
        }

field_inputs['mtime'] =  {
        #'validator': validate.natural(),
        #'type': fields.Integer()
        'type': fields.String(),
        'validator': validate.str_range(argument={'low': 1, 'high': 20})
        }

field_inputs_wrap['orderBy'] = {
        'validator': validate.str_in_list(
            default='mtime',
            argument=['mtime'],
            ),
        'type': fields.String(default='mtime'),
        }

field_inputs_user['avatar_url'] =  {
        'type': fields.String(default=""),
        'validator': validate.str_range(default="", argument={'low': 1, 'high': 255})
        }

field_inputs_user['id'] = field_inputs['id'].copy()

field_inputs_post = {}

for v in ['content', 'business_id', 'mtime', 'rate']:
    field_inputs_post[v] = field_inputs[v].copy()
field_inputs_post['user_id'] = field_inputs_user['id'].copy()



resource_fields, resource_fields_user, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_user, field_inputs_wrap, field_inputs_wrap_head)
resource_fields, resource_fields_post, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_post, field_inputs_wrap, field_inputs_wrap_head)
