#

import logging
import pprint

import spotipy
import spotipy.util

import sopiva.spotify.client_cached
import sopiva.spotify.state
import toukka.config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _read_from_config():
    client_id = toukka.config.lazy_config['spotify']['client_id'].get()
    client_secret = toukka.config.lazy_config['spotify']['client_secret'].get()
    redirect_uri = toukka.config.lazy_config['spotify']['redirect_uri'].get()
    return client_id, client_secret, redirect_uri


def get_spotify_with_client_credentials():
    # client_id, client_secret, client_redirect = spotipy.util.read_environment()
    client_id, client_secret, redirect_uri = _read_from_config()
    credentials = spotipy.auth.Credentials(client_id, client_secret, redirect_uri)
    token = credentials.request_client_token()
    #token_refresh = spotipy.util.RefreshingToken(token, credentials)
    #client = sopiva.spotify.client_cached.CachedSpotify(token_refresh,
    #                                                    sender=spotipy.sender.PersistentSender())
    client = sopiva.spotify.client_cached.CachedSpotify(token)
    return client


def get_user_refresh_token():
    logger.debug('get user refresh token from statedb')
    db = sopiva.spotify.state.get_statedb()
    return db.get('user_refresh_token')


def set_user_refresh_token(refresh_token):
    logger.debug('set user refresh token to statedb')
    db = sopiva.spotify.state.get_statedb()
    db.set('user_refresh_token', refresh_token)


def get_user_token():
    client_id, client_secret, redirect_uri = _read_from_config()
    # client_id, client_secret, client_redirect = read_environment()
    refresh_token = get_user_refresh_token()
    if refresh_token:
        logger.debug('refresh token found from config, using it')
        token = spotipy.util.token_from_refresh_token(client_id, client_secret, redirect_uri, refresh_token)
    else:
        logger.debug('referesh token not found from config, prompt user input')
        scope = spotipy.Scope(spotipy.scope.every)
        token = spotipy.util.prompt_for_user_token(client_id, client_secret, redirect_uri, scope)
        set_user_refresh_token(token.refresh_token)
    return token


def get_spotify_with_user_credentials():
    token = get_user_token()
    client = sopiva.spotify.client_cached.CachedSpotify(token=token)
    return client


def get_spotify():
    return get_spotify_with_user_credentials()


# END
