# -*- coding: utf-8 -*-

#
# https://github.com/mitsuhiko/flask/blob/master/examples/minitwit/test_minitwit.py
#
import json

import unittest
from nose.tools import *
from config.route import route

from .__init__ import app, test_app, teardown, base_url, db
from .data import *

from ..__init__ import \
        __customer_businessgrp_head__ as __grp__head__, \
        __customer_businessgrp_heads__ as __grp__heads__, \
        __customer_business_head__ as __obj__head__, \
        __customer_business_heads__ as __obj__heads__


class TestBusiness(unittest.TestCase):
    def setUp(self):
        #app.config.from_object('webapp.config.Testing')
        db.init_app(app)
        #self.app = app.test_client()

    def tearDown(self):
        teardown()

    def check_content_type(self, headers):
        eq_(headers['Content-Type'], 'application/json')


    def test_positive_CRUD(self):
        # get all
        rv = test_app.get(route['CustomerBusinesses'], base_url=base_url)
        self.check_content_type(rv.headers)

        # print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
        resp = json.loads(rv.data.decode('utf-8'))

        # make sure we get a response
        eq_(rv.status_code, 200)
        # make sure there are no record
        eq_(resp['total'], 0)

        # create one relationship before we create group
        rv = test_app.post(route['CustomerBusinesses'], 
                base_url=base_url, 
                data=json.dumps(d_obj_c),
                headers={'content-type':'application/json'})
        #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))

        objId = json.loads(rv.data.decode('utf-8'))[__obj__head__]['id']
        #d = {
        #    __head__: {
        #        'name': 'test1',
        #        'description': 'testd',
        #        __obj__heads__: [
        #            {
        #                'id': objId
        #            }
        #        ]
        #    }
        #}
        #rv = test_app.post(route['CustomerBusiness'], base_url=base_url, data=json.dumps(d),
        #                   headers={'content-type':'application/json'})
        ##print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
        #self.check_content_type(rv.headers)
        #eq_(rv.status_code, 200)

        ## Verify we sent the right data back
        #resp = json.loads(rv.data.decode('utf-8'))
        #eq_(resp[__head__]['name'], 'test1')
        #eq_(resp[__head__]['description'], d[__head__]['description'])
        #eq_(resp[__head__][__obj__heads__][0]['id'], objId)
        #grpId = resp[__head__]['id']

        # Get all record again...should have one
        rv = test_app.get(route['CustomerBusinesses'], base_url=base_url)
        self.check_content_type(rv.headers)
        #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
        resp = json.loads(rv.data.decode('utf-8'))
        # make sure we get a response
        eq_(rv.status_code, 200)
        eq_(resp['total'], 1)
        #eq_(len(resp[__heads__]), 1)

        # GET the record with specified ID
        rv = test_app.get('/'.join([route['CustomerBusiness'], str(objId)]), base_url=base_url)
        #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
        self.check_content_type(rv.headers)
        eq_(rv.status_code, 200)
        resp = json.loads(rv.data.decode('utf-8'))

        eq_(resp[__obj__head__]['name'], d_obj_c[__obj__head__]['name'])
        eq_(resp[__obj__head__]['description'], d_obj_c[__obj__head__]['description'])
        #eq_(resp[__head__][__obj__heads__][0]['id'], objId)

        # Try and add Duplicate record by name
        rv = test_app.post(route['CustomerBusinesses'], 
                base_url=base_url, 
                data=json.dumps(d_obj_c),
                headers={'content-type':'application/json'})
        #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
        self.check_content_type(rv.headers)
        eq_(rv.status_code, 400)
        resp = json.loads(rv.data.decode('utf-8'))

        # CE_NAME_CONFLICT
        eq_(resp['errorId'], 2004)

        # try to delete
        rv = test_app.delete(route['CustomerBusinesses'], base_url=base_url,
            query_string='='.join([__obj__heads__, ','.join([str(objId)])]))
        #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
        self.check_content_type(rv.headers)
        eq_(rv.status_code, 204)
    #   resp = json.loads(rv.data.decode('utf-8'))
    #eq_(resp, '')

    #def test_negative_CRUD():
    #    rv = test_app.get(route['CustomerBusiness'], base_url=base_url)
    #    self.check_content_type(rv.headers)
    #
    #    # print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    #    resp = json.loads(rv.data.decode('utf-8'))
    #
    #    # make sure we get a response
    #    eq_(rv.status_code, 200)
    #    # make sure there are no record
    #    eq_(len(resp[__heads__]), 0)
    #
    #    # create one relationship before we create group
    #    rv = test_app.post(route['CustomerBusinesses'], base_url=base_url, data='{"ipaddr":{"name": "test109","type": "Subnet", "ipVersion": "IPv6","addr2": "128","description":"test", "addr1": "2001:660::1"}}',
    #                       headers={'content-type':'application/json'})
    #    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    #
    #    objId = json.loads(rv.data.decode('utf-8'))[__obj__head__]['id']
    #    d = {
    #        __head__: {
    #            'name': 'test1',
    #            'description': 'testd',
    #            __obj__heads__: [
    #                {
    #                    'id': objId
    #                }
    #            ]
    #        }
    #    }
    #    rv = test_app.post(route['CustomerBusiness'], base_url=base_url, data=json.dumps(d),
    #                       headers={'content-type':'application/json'})
    #    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    #    self.check_content_type(rv.headers)
    #    eq_(rv.status_code, 200)
    #
    #    # Verify we sent the right data back
    #    resp = json.loads(rv.data.decode('utf-8'))
    #    eq_(resp[__head__]['name'], 'test1')
    #    eq_(resp[__head__]['description'], d[__head__]['description'])
    #    eq_(resp[__head__][__obj__heads__][0]['id'], objId)
    #    grpId = resp[__head__]['id']
    #
    #    # Get all record again...should have one
    #    rv = test_app.get(route['CustomerBusiness'], base_url=base_url)
    #    self.check_content_type(rv.headers)
    #    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    #    resp = json.loads(rv.data.decode('utf-8'))
    #    # make sure we get a response
    #    eq_(rv.status_code, 200)
    #    eq_(len(resp[__heads__]), 1)
    #
    #    # GET the record with specified ID
    #    rv = test_app.get('/'.join([route['CustomerBusiness'], str(grpId)]), base_url=base_url)
    #    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    #    self.check_content_type(rv.headers)
    #    eq_(rv.status_code, 200)
    #    resp = json.loads(rv.data.decode('utf-8'))
    #
    #    eq_(resp[__head__]['name'], d[__head__]['name'])
    #    eq_(resp[__head__]['description'], d[__head__]['description'])
    #    eq_(resp[__head__][__obj__heads__][0]['id'], objId)
    #
    #    # Try and add Duplicate record by name
    #    rv = test_app.post(route['CustomerBusiness'], base_url=base_url, data=json.dumps(d),
    #                       headers={'content-type':'application/json'})
    #    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    #    self.check_content_type(rv.headers)
    #    eq_(rv.status_code, 400)
    #    resp = json.loads(rv.data.decode('utf-8'))
    #
    #    # CE_NAME_CONFLICT
    #    eq_(resp['errorId'], 2004)
