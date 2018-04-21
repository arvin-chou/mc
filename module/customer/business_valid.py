# -*- coding: utf-8 -*-

from utils import fields
from utils import validate

from module.common import GetResource
from module.common import field_inputs_wrap as _field_inputs_wrap
from module.common import field_inputs_ref as _field_inputs_ref
from module.common import field_inputs as _field_inputs
from module.common import field_inputs_wrap_head

# for serialize
from .__init__ import __customer_business_head__ as __head__, \
        __customer_business_heads__ as __heads__, \
        __customer_business_detail_head__ as __head_detail__, \
        __customer_business_detail_rates_head__ as __head_detail_rates__, \
        __customer_business_detail_deals_head__ as __head_detail_deals__, \
        __customer_business_detail_images_url_head__ as __head_detail_images_url__

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

# TODO: use validate.float
field_inputs_detail = {}
field_inputs_detail_rates = {}
field_inputs_detail_deals = {}
field_inputs_detail_images_url = {}
field_inputs_detail['rate'] =  {
        #'validator': validate.str_range(argument={'low': 1, 'high': 255}),
        #'type': fields.Float(default=0)
        'validator': validate.natural(),
        'type': fields.Integer()
        }
field_inputs_detail_rates['id'] = {
        'validator': validate.natural(),
        'type': fields.Integer()
        }
field_inputs_detail_rates['avatar_url'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
        'type': fields.String()
        }
field_inputs_detail['deals'] =  {
# type attribute for marshal
        'type': { fields.List(fields.Nested({
            'title': {'type': fields.String(attribute='title')},
            'description': {'type': fields.String(attribute='description')},
            }))
            },
# validate attribute for reqparse
        'validator': { fields.List(fields.Nested({
            'title':{'type': validate.str_range(argument={'low': 1, 'high': 64})},
            'description':{'type': validate.str_range(argument={'low': 1, 'high': 64})}
            }))
            }
        }

field_inputs_detail_deals['title'] = {
        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
        'type': fields.String()
        }
field_inputs_detail_deals['description'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
        'type': fields.String()
        }

field_inputs_detail['name'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 254}),
        'type': fields.String()
        }
field_inputs_detail['rate'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        #'validator': validate.str_range(argument={'low': 1, 'high': 255}),
        ## TODO: support fields.Float
        #'type': fields.String()
        }
field_inputs_detail['id'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }
field_inputs_detail['rate_nr'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }
field_inputs_detail['user_nr'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }
#field_inputs_detail['comments'] =  {
## type attribute for marshal
#        'type': { fields.List(fields.Nested({
#            'id': {'type': fields.Integer()},
#            'avatar_url': {'type': fields.String(attribute='description')},
#            }))
#            },
## validate attribute for reqparse
#        'validator': { fields.List(fields.Nested({
#            'id':{'type': fields.Integer()},
#            'avatar_url':{'type': validate.str_range(argument={'low': 1, 'high': 64})}
#            }))
#            }
#        }
field_inputs_detail['gallery_nr'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }
field_inputs_detail['meals'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 254}),
        'type': fields.String()
        }
field_inputs_detail['features'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 254}),
        'type': fields.String()
        }
field_inputs_detail['open'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 4}),
        'type': fields.String()
        }
field_inputs_detail['address'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 254}),
        'type': fields.String()
        }
field_inputs_detail['dist'] =  {
        'validator': validate.natural(),
        'type': fields.Integer()
        }
field_inputs_detail['is_favorite'] =  {
        'validator': validate.natural(default = 0),
        'type': fields.Integer(default = 0)
        }

field_inputs_detail['close'] = field_inputs_detail['open'].copy()

field_inputs_post = field_inputs.copy()
field_inputs_post.pop('image_url')
field_inputs_post.pop('id')

for v in ['dist', 'open', 'close', 'address', 'meals', 'features', 'deals']:
    field_inputs_post[v] = field_inputs_detail[v].copy()

field_inputs_detail_images_url['bg'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
        'type': fields.String()
        }
field_inputs_detail_images_url['icon'] =  {
        'validator': validate.str_range(argument={'low': 1, 'high': 255}),
        'type': fields.String()
        }

# TODO: support multi layer
resource_fields_detail_rates, resource_fields_ref, resource_fields_detail = GetResource(
        field_inputs_detail_rates, field_inputs_ref, field_inputs_detail, __head_detail_rates__)

resource_fields_detail_deals, resource_fields_ref, resource_fields_detail = GetResource(
        field_inputs_detail_deals, field_inputs_ref, field_inputs_detail, __head_detail_deals__)

resource_fields_detail_images_url, resource_fields_ref, resource_fields_detail = GetResource(
        field_inputs_detail_images_url, field_inputs_ref, field_inputs_detail, __head_detail_images_url__)

resource_fields_post, resource_fields_ref, resource_fields_wrap = GetResource(
        field_inputs_post, field_inputs_ref, field_inputs_wrap, field_inputs_wrap_head)

#resource_fields, resource_fields_ref, resource_fields_wrap = GetResource(
#        field_inputs_detail, field_inputs_ref, field_inputs, __head_detail__)

resource_fields, resource_fields_ref, resource_fields_wrap = GetResource(
        field_inputs, field_inputs_ref, field_inputs_wrap, field_inputs_wrap_head)

