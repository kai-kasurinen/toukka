#

import os
import logging

from spotipy.oauth2 import SpotifyOAuth, is_token_expired
from . import SCOPES_ALL

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ClientCredentialsManager:
    def __init__(self,
                 username=None,
                 client_id=None,
                 client_secret=None,
                 redirect_uri=None,
                 cache_path=None,
                 cache_directory=None,
                 scope=None):

        if not client_id:
            client_id = os.getenv('SPOTIPY_CLIENT_ID')
        if not client_secret:
            client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        if not redirect_uri:
            redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
        # we only need this for cache_path filename?
        if not username:
            username = os.getenv('SPOTIPY_USER')
        if not scope:
            scope = " ".join(SCOPES_ALL)
        if cache_directory and not cache_path:
            cache_path = os.path.join(cache_directory, username)
        if not cache_path:
            cache_path = '.cache-' + username

        # cache_path should be named as cache_file
        self.sp_oauth = SpotifyOAuth(client_id,
                                     client_secret,
                                     redirect_uri,
                                     scope=scope,
                                     cache_path=cache_path)
        self.token_info = self.sp_oauth.get_cached_token()
        if not self.token_info:
            self._prompt_for_user_token()

    # is only method need implemented
    def get_access_token(self):
        self._update_expired_token()
        if self.token_info:
            return self.token_info['access_token']
        else:
            logger.debug('someone eat our token_info')
            return None

    def _update_expired_token(self):
        if self.sp_oauth.is_token_expired(self.token_info):
            logger.debug('token is expired, trying refresh it')
            self.token_info = self.sp_oauth.refresh_access_token(self.token_info['refresh_token'])
            # for example 50x
            if self.token_info is None:
                raise Exception('update expired token failed')

    def _prompt_for_user_token(self):
        if not self.token_info:
            print('''
                User authentication requires interaction with your
                web browser. Once you enter your credentials and
                give authorization, you will be redirected to
                a url.  Paste that url you were directed to to
                complete the authorization.
                ''')

            auth_url = self.sp_oauth.get_authorize_url()

            try:
                import webbrowser
                webbrowser.open(auth_url)
                print("Opened %s in your browser" % auth_url)
            except:
                print("Please navigate here: %s" % auth_url)

            print()
            print()
            try:
                response = raw_input("Enter the URL you were redirected to: ")
            except NameError:
                response = input("Enter the URL you were redirected to: ")

            print()
            print() 

            code = self.sp_oauth.parse_response_code(response)
            self.token_info = self.sp_oauth.get_access_token(code)
