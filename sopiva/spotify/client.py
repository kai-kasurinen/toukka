#

import logging

from spotipy.util import read_environment
from spotipy import scopes, Scope
from spotipy.util import prompt_for_user_token
from spotipy import Spotify
from spotipy.auth import Credentials
from spotipy.util import read_environment

from .client_cached import CachedSpotify
from ..config import lazy_config


def _read_from_config():
    client_id = lazy_config['spotify']['client_id'].get()
    client_secret = lazy_config['spotify']['client_secret'].get()
    redirect_uri = lazy_config['spotify']['redirect_uri'].get()
    user = lazy_config['spotify']['user'].get()
    return client_id, client_secret, redirect_uri


def get_spotify_with_client_credentials():
    #client_id, client_secret, client_redirect = read_environment()
    client_id, client_secret, client_redirect = _read_from_config()
    cred = Credentials(client_id, client_secret, client_redirect)
    token = cred.request_client_token()
    client = CachedSpotify(token)
    return client


def get_spotify_with_user_credentials():
    client_id, client_secret, client_redirect = read_environment()
    scope = Scope(*scopes)
    token = prompt_for_user_token(client_id, client_secret, client_redirect_uri, scope)
    client = Spotify(token)
    return client


# END
