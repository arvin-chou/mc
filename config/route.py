# -*- coding: utf-8 -*-

from module.login.login import AdminLogin
from module.system.system import Admins, Admin
from module.customer.business import CustomerBusiness, CustomerBusinesses, CustomerBusinessesRef
#from module.customer.businessgrp import CustomerBusinessgrp, CustomerBusinessgrps, CustomerBusinessgrpRef
from module.customer.comment import CustomerComment, CustomerComments
from module.customer.rate import CustomerRate, CustomerRates
#from module.policy.security import PolicySecurity, PolicySecurities
from module.pic.gallery import PicGallery
from module.pushno.pushno import PushnoSend, PushnoReg, PushnoUnReg
#from module.pushno.pushno import PushnoReg, PushnoUnReg

route = {
  'Admins': '/rest/admins',
  'Admin': '/rest/admin',
  'AdminLogin': '/rest/admin/login',
  'AdminLoginGoogle': '/rest/admin/login/google',
  'AdminLoginFacebook': '/rest/admin/login/facebook',
  'AdminLogout': '/rest/admin/logout',
  'CustomerBusinesses': '/rest/customer/businesses',
  'CustomerBusiness': '/rest/customer/business',
  'CustomerBusinessesRef': '/rest/customer/businesses/ref',
  #'CustomerBusinessgrps': '/rest/customer/businessgrps',
  #'CustomerBusinessgrpRef': '/rest/customer/businessgrps/ref',
  'CustomerComment': '/rest/customer/comment',
  'CustomerComments': '/rest/customer/comments',
  'CustomerRate': '/rest/customer/rate',
  'CustomerRates': '/rest/customer/rates',
  'PicGallery': '/rest/pic/gallery',
  'PushnoReg': '/rest/pushno/reg',
  'PushnoUnReg': '/rest/pushno/unreg',
  'PushnoSend': '/rest/pushno/send',
  #'PolicySecurities': '/rest/policies/sec',
}

__all__ = [
  'route',
  'ConfigRoute',
  ]

class ConfigRoute():
    """set flask routing table
    """

    @staticmethod
    def set_route(api):
        api.add_resource(AdminLogin, route['AdminLogin'],
            route['AdminLoginGoogle'], route['AdminLoginFacebook'])
        api.add_resource(Admin, '/'.join([route['Admin'], '<int:id>']),
            endpoint='admin')
        api.add_resource(Admins, route['Admins']) # post / delete

        #
        # /rest/customer/businesses
        #
        api.add_resource(CustomerBusiness, \
                '/'.join([route['CustomerBusiness'], '<int:id>']), \
                endpoint=route['CustomerBusiness']) # put/getone
        api.add_resource(CustomerBusinesses, 
                route['CustomerBusinesses']) # delete/create/getall
        api.add_resource(CustomerBusinessesRef, 
                route['CustomerBusinessesRef']) # ref
        #api.add_resource(CustomerBusinessgrp, \
        #        '/'.join([route['CustomerBusinessgrps'], '<int:id>'])) # put/getone
        #api.add_resource(CustomerBusinessgrps, 
        #        route['CustomerBusinessgrps']) # delete/create/getall
        #api.add_resource(CustomerBusinessgrpRef, 
        #        route['CustomerBusinessgrpRef']) # ref
        api.add_resource(CustomerComment, \
                '/'.join([route['CustomerComment'], '<int:id>'])) # put/getone
        api.add_resource(CustomerComments, \
                '/'.join([route['CustomerComments']])) # delete/create/getall
        api.add_resource(CustomerRate, \
                '/'.join([route['CustomerRate'], '<int:id>'])) # put/getone
        api.add_resource(CustomerRates, \
                '/'.join([route['CustomerRates']])) # delete/create/getall
#        api.add_resource(PicGallery, \
#                '/'.join([route['PicGallery']])) # 
        api.add_resource(PicGallery, \
                '/'.join([route['PicGallery'], '<int:id>']), '/'.join([route['PicGallery']])) # 

        api.add_resource(PushnoReg, \
                '/'.join([route['PushnoReg']]), \
                '/'.join([route['PushnoReg'], '<int:id>'])) # 
        api.add_resource(PushnoUnReg, '/'.join([route['PushnoUnReg'], '<int:business_id>'])) # 
        api.add_resource(PushnoSend, '/'.join([route['PushnoSend'], '<int:business_id>']))



        #api.add_resource(PolicySecurity, \
        #        '/'.join([route['PolicySecurities'], '<int:id>']))  # put/getone
        #api.add_resource(PolicySecurities, route['PolicySecurities']) # delete/create/getall
