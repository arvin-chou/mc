# -*- coding: utf-8 -*-

'''
    Auth-SHA1/HMAC
    ~~~~~~~~~~~~~~

    Securing an Eve-powered API with Basic Authentication (RFC2617).

    Since we are using werkzeug we don't need any extra import (werkzeug being
    one of Flask/Eve prerequisites).

    This snippet by Nicola Iarocci can be used freely for anything you like.
    Consider it public domain.
'''

import os

from flask import url_for, redirect, request, session
from flask.ext.cdn import CDN

from werkzeug.security import check_password_hash
from uuid import UUID

from config.config import app, port, host, route, api, _logging, debug, \
       install_secret_salt, install_secret_key, \
       init_db, init_platform_model, init_cdn
from config.config import settings

DP_ROOT = settings.DP_ROOT
logger = _logging.getLogger(__name__)

#
# Init
#
logger.warning('Init...')

install_secret_salt(app)
install_secret_key(app)

init_db()
init_platform_model()
cdn = CDN()
app.config['CDN_DOMAIN'] = 'mycdnname.cloudfront.net'
app.config['CDN_ENDPOINTS'] = 'static'
cdn.init_app(app)
#init_cdn(app, cdn)

from schema.users import User
#from utils import abort
from flask.ext.restful import abort

from module.login.login import AdminLogin
from module.system.system import Admins, Admin
from module.customer.business import CustomerBusiness, CustomerBusinesses, CustomerBusinessesRef
from module.customer.businessgrp import CustomerBusinessgrp, CustomerBusinessgrps, CustomerBusinessgrpRef
from module.policy.security import PolicySecurity, PolicySecurities

# https://github.com/mitsuhiko/flask
def do_the_login(): pass
def valid_login(username=None, password=None): pass


#
# routing
#
api.add_resource(AdminLogin, route['AdminLogin'])
#api.add_resource(Admin, route['Admin'], endpoint='admins')
api.add_resource(Admin, '/'.join([route['Admins'], '<int:id>']))
api.add_resource(Admins, route['Admins'])
#
# /rest/customer/businesses
#
api.add_resource(CustomerBusiness, \
    '/'.join([route['Customerbusiness'], '<int:id>']), endpoint=route['Customerbusiness']) # put/getone
api.add_resource(CustomerBusinesses, route['CustomerBusinesses']) # delete/create/getall
api.add_resource(CustomerBusinessesRef, route['CustomerBusinessesRef']) # ref
api.add_resource(CustomerBusinessgrp, \
    '/'.join([route['CustomerBusinessgrps'], '<int:id>'])) # put/getone
api.add_resource(CustomerBusinessgrps, route['CustomerBusinessgrps']) # delete/create/getall
api.add_resource(CustomerBusinessgrpRef, route['CustomerBusinessgrpRef']) # ref



api.add_resource(PolicySecurity, \
    '/'.join([route['PolicySecurities'], '<int:id>']))  # put/getone
api.add_resource(PolicySecurities, route['PolicySecurities']) # delete/create/getall

@app.route(route['AdminLogout'] , methods=['POST'])
def adminlogout():
    User.DeleteSession()
#return redirect(url_for('static', filename='zetatauri-web/www/index.html'))
    return redirect(url_for('', filename='zetatauri-web/www/index.html'))


# if no define, we pass here
@app.route('/<path:path>')
def static_proxy(path):
    #logger.info('your request path are: %s', os.path.join(path))
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)
    #return app.send_static_file(os.path.join('zetatauri-web/www/', path))


@app.before_request
def check_valid_login():
    # if cookies alive, it will never timeout
    #login_valid = User.IsSessionAlive()

    if (
        request.endpoint and
        #'rest' not in request.endpoint and
        not request.path.startswith('/rest')):# and
        #not login_valid ):
        #and
        #not getattr(app.view_functions[request.endpoint], 'is_public', False) ) :
        #return render_template('login.html', next=request.endpoint)
        #return app.send_static_file('zetatauri-web/www/index.html')
        #print("xxxx", url_for(request.path))
        #return app.send_static_file(('zetatauri-web/www/' + request.path))
        #return redirect(url_for(request.path))
        #return app.send_static_file(request.path)
        pass # pass to static
        #return app.send_static_file('zetatauri-web/www/index.html')
    elif (request.path.startswith('/rest/admin/login') and
        request.method == 'POST'):
        logger.debug('we only pass /rest/admin/login for login reqest with POST method')
        pass
    elif True:
        #logger.debug('your request path are: %s', os.path.join(request.path))
        logger.warning('NO CHECK FOR VALIDATE API')
        pass

    elif not User.IsSessionAlive(User):
        abort(401)
    else:
        User.UpdateAlive(User)
    #elif (request.endpoint and
    #        'zetatauri-web' in request.endpoint):
    #    #print('ccc', ('zetatauri-web/www/', path))
    #    return app.send_static_file(os.path.join('zetatauri-web/www/', request.endpoint.join('/')))

# this could effect all 404
@app.errorhandler(404)
def not_found(error):
#return app.send_static_file('/'.join([DP_ROOT, 'zetatauri-web/www/index.html'])), 404
    return app.send_static_file('index.html'), 404

"""
# not monitor test* file
extra_dirs = [DP_ROOT,]
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename) and filename not in 'test':
                extra_files.append(filename)
"""
if __name__ == '__main__':
    app.run(processes=3, host=host, port=port, debug=debug, extra_files=[],\
        use_reloader=True)
