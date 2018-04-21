from flask import url_for, current_app, redirect, request
from rauth import OAuth2Service, OAuth2Session
import json
import urllib

from config.config import settings, _logging
logger = _logging.getLogger(__name__)

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = getattr(settings, 'OAUTH_CREDENTIALS')[provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']
        print("self.consumer_id:", self.consumer_id, "self.consumer_secret:", self.consumer_secret)

    def authorize(self):
        pass

    def callback(self):
        pass

    #def get(self):
    #    pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                        _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers={}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        req = urllib.request.Request('https://accounts.google.com/.well-known/openid-configuration')

        try:
            with urllib.request.urlopen(req) as resp:
                googleinfo = resp.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.debug('%s encounter urllib.error.URLError.reason %s', u, e.reason)

        print("googleinfo: ", googleinfo)
        google_params = json.loads(googleinfo)
        self.service = OAuth2Service(
                name='google',
                client_id=self.consumer_id,
                client_secret=self.consumer_secret,
                authorize_url=google_params.get('authorization_endpoint'),
                base_url=google_params.get('userinfo_endpoint'),
                access_token_url=google_params.get('token_endpoint')
        )
        #print("xxxxx==,", self.service.get_access_token())
    #def get(self, index, access_token):
    #    return self.service.get(index, access_token=access_token)

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
            )

    def json_loads_wrap(self, data):
        return json.loads(data.decode('utf-8'))

    def callback(self, access_token=None):
        if not access_token:
            if 'code' not in request.args:
                return None, None, None
            access_token = request.args['code']
        # TODO: data: {
# "error": "invalid_grant",
# "error_description": "Code was already redeemed."
#}

        logger.debug('access_token: %s', access_token)
        oauth_session = self.service.get_auth_session(
                data={'code': access_token,
                      'grant_type': 'authorization_code',
                      'redirect_uri': self.get_callback_url()
                     },
                decoder = self.json_loads_wrap
        )
        return oauth_session.get('').json()

    def get_session(self, access_token=None):
        client_id=self.consumer_id,
        client_secret=self.consumer_secret,
        return OAuth2Session(client_id, client_secret, 
                #access_token=access_token).get('http://localhost:5000/access_token')
                access_token=access_token).get('https://www.googleapis.com/oauth2/v3/userinfo').json()
                #access_token=access_token).get('')
                #access_token=access_token).get('/access_token')
        #return OAuth2Session(client_id, client_secret, 
        #access_token=access_token).get('https://www.googleapis.com/oauth2/v4/token').json()
        #access_token=access_token).get('https://www.googleapis.com/oauth2/v4/token')
        #return OAuth2Session(client_id, client_secret, access_token=access_token).get('http://localhost:5000/login2', params={'format': 'json'})
