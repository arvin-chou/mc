# -*- coding: utf-8 -*-

#
# https://github.com/mitsuhiko/flask/blob/master/examples/minitwit/test_minitwit.py
#
import json

from nose.tools import *
from config.config import route, db

from .__init__ import test_app, teardown, base_url

from ..__init__ import __objects_ipgroup_head__ as __head__, \
    __objects_ipgroup_heads__ as __heads__, \
    __objects_ipaddr_head__ as __obj__head__, \
    __objects_ipaddr_heads__ as __obj__heads__



def check_content_type(headers):
    eq_(headers['Content-Type'], 'application/json')


def test_positive_CRUD():
    rv = test_app.get(route['ObjectIpgroups'], base_url=base_url)
    check_content_type(rv.headers)

    # print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    resp = json.loads(rv.data.decode('utf-8'))

    # make sure we get a response
    eq_(rv.status_code, 200)
    # make sure there are no record
    eq_(len(resp[__heads__]), 0)

    # create one relationship before we create group
    rv = test_app.post(route['ObjectIpaddrs'], base_url=base_url, data='{"ipaddr":{"name": "test109","type": "Subnet", "ipVersion": "IPv6","addr2": "128","description":"test", "addr1": "2001:660::1"}}',
                       headers={'content-type':'application/json'})
    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))

    objId = json.loads(rv.data.decode('utf-8'))[__obj__head__]['id']
    d = {
        __head__: {
            'name': 'test1',
            'description': 'testd',
            __obj__heads__: [
                {
                    'id': objId
                }
            ]
        }
    }
    rv = test_app.post(route['ObjectIpgroups'], base_url=base_url, data=json.dumps(d),
                       headers={'content-type':'application/json'})
    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    check_content_type(rv.headers)
    eq_(rv.status_code, 200)

    # Verify we sent the right data back
    resp = json.loads(rv.data.decode('utf-8'))
    eq_(resp[__head__]['name'], 'test1')
    eq_(resp[__head__]['description'], d[__head__]['description'])
    eq_(resp[__head__][__obj__heads__][0]['id'], objId)
    grpId = resp[__head__]['id']

    # Get all record again...should have one
    rv = test_app.get(route['ObjectIpgroups'], base_url=base_url)
    check_content_type(rv.headers)
    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    resp = json.loads(rv.data.decode('utf-8'))
    # make sure we get a response
    eq_(rv.status_code, 200)
    eq_(len(resp[__heads__]), 1)

    # GET the record with specified ID
    rv = test_app.get('/'.join([route['ObjectIpgroups'], str(grpId)]), base_url=base_url)
    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    check_content_type(rv.headers)
    eq_(rv.status_code, 200)
    resp = json.loads(rv.data.decode('utf-8'))

    eq_(resp[__head__]['name'], d[__head__]['name'])
    eq_(resp[__head__]['description'], d[__head__]['description'])
    eq_(resp[__head__][__obj__heads__][0]['id'], objId)

    # Try and add Duplicate record by name
    rv = test_app.post(route['ObjectIpgroups'], base_url=base_url, data=json.dumps(d),
                       headers={'content-type':'application/json'})
    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    check_content_type(rv.headers)
    eq_(rv.status_code, 400)
    resp = json.loads(rv.data.decode('utf-8'))

    # CE_NAME_CONFLICT
    eq_(resp['errorId'], 2004)

    # try to delete
    rv = test_app.delete(route['ObjectIpgroups'], base_url=base_url,
        query_string='='.join([__heads__, ','.join([str(grpId)])]))
    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
    check_content_type(rv.headers)
    eq_(rv.status_code, 204)
#   resp = json.loads(rv.data.decode('utf-8'))
#eq_(resp, '')

#def test_negative_CRUD():
#    rv = test_app.get(route['ObjectIpgroups'], base_url=base_url)
#    check_content_type(rv.headers)
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
#    rv = test_app.post(route['ObjectIpaddrs'], base_url=base_url, data='{"ipaddr":{"name": "test109","type": "Subnet", "ipVersion": "IPv6","addr2": "128","description":"test", "addr1": "2001:660::1"}}',
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
#    rv = test_app.post(route['ObjectIpgroups'], base_url=base_url, data=json.dumps(d),
#                       headers={'content-type':'application/json'})
#    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
#    check_content_type(rv.headers)
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
#    rv = test_app.get(route['ObjectIpgroups'], base_url=base_url)
#    check_content_type(rv.headers)
#    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
#    resp = json.loads(rv.data.decode('utf-8'))
#    # make sure we get a response
#    eq_(rv.status_code, 200)
#    eq_(len(resp[__heads__]), 1)
#
#    # GET the record with specified ID
#    rv = test_app.get('/'.join([route['ObjectIpgroups'], str(grpId)]), base_url=base_url)
#    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
#    check_content_type(rv.headers)
#    eq_(rv.status_code, 200)
#    resp = json.loads(rv.data.decode('utf-8'))
#
#    eq_(resp[__head__]['name'], d[__head__]['name'])
#    eq_(resp[__head__]['description'], d[__head__]['description'])
#    eq_(resp[__head__][__obj__heads__][0]['id'], objId)
#
#    # Try and add Duplicate record by name
#    rv = test_app.post(route['ObjectIpgroups'], base_url=base_url, data=json.dumps(d),
#                       headers={'content-type':'application/json'})
#    #print('rv.data.decode("utf-8")=', rv.data.decode('utf-8'))
#    check_content_type(rv.headers)
#    eq_(rv.status_code, 400)
#    resp = json.loads(rv.data.decode('utf-8'))
#
#    # CE_NAME_CONFLICT
#    eq_(resp['errorId'], 2004)
