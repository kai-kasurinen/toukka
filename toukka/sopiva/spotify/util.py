#

from typing import Tuple

import logging
import pprint

import spotipy
import spotipy.util
import spotipy.sender

import toukka.config
import toukka.hub.requests

import toukka.sopiva.spotify.client.current
import toukka.sopiva.spotify.state


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def _read_from_config() -> Tuple[str, str, str]:
    client_id = toukka.config.lazy_config['spotify']['client_id'].get()
    client_secret = toukka.config.lazy_config['spotify']['client_secret'].get()
    redirect_uri = toukka.config.lazy_config['spotify']['redirect_uri'].get()
    return client_id, client_secret, redirect_uri


def get_user_refresh_token() -> str:
    logger.debug('get user refresh token from statedb')
    statedb = toukka.sopiva.spotify.state.get_statedb()
    return statedb.get('user_refresh_token')


def set_user_refresh_token(refresh_token) -> None:
    logger.debug('set user refresh token to statedb')
    statedb = toukka.sopiva.spotify.state.get_statedb()
    statedb.set('user_refresh_token', refresh_token)


def get_user_token() -> spotipy.util.RefreshingToken:
    client_id, client_secret, redirect_uri = _read_from_config()
    # client_id, client_secret, client_redirect = read_environment()
    refresh_token = get_user_refresh_token()
    token = None

    if refresh_token:
        logger.debug('refresh token found, using it')
        # TODO: catch spotipy.auth.OAuthError
        try:
            token = spotipy.util.request_refreshed_token(client_id, client_secret, redirect_uri, refresh_token)
        except spotipy.auth.OAuthError as e:
            logger.warning(e)

    if token is None:
        logger.debug('referesh token not found, prompt user input')
        scope = spotipy.Scope(spotipy.scope.every)
        token = spotipy.util.prompt_for_user_token(client_id, client_secret, redirect_uri, scope)
        set_user_refresh_token(token.refresh_token)

    return token


def get_sender() -> spotipy.sender.Sender:
    # our session handless retrying, so this not needed
    # retrying_sender = spotipy.sender.RetryingSender(retries=2, sender=sender)
    sender = spotipy.sender.PersistentSender()
    sender.session = toukka.hub.requests.get_cached_session()
    return sender


def get_client_token() -> spotipy.util.RefreshingToken:
    # client_id, client_secret, client_redirect = spotipy.util.read_environment()
    client_id, client_secret, redirect_uri = _read_from_config()
    credentials = spotipy.util.RefreshingCredentials(client_id, client_secret, redirect_uri)
    token = credentials.request_client_token()
    return token


def get_client(token, sender) -> toukka.sopiva.spotify.client.current.Spotify:
    # https://github.com/psf/requests/issues/3070
    requests_kwargs = {'timeout': 10.0}
    client = toukka.sopiva.spotify.client.current.Spotify(
        token=token, sender=sender, requests_kwargs=requests_kwargs)
    return client


# TODO: combine with_user_credentials and with_client_credentialss
def get_spotify_with_user_credentials() -> toukka.sopiva.spotify.client.current.Spotify:
    token = get_user_token()
    sender = get_sender()
    client = get_client(token, sender)
    return client


def get_spotify_with_client_credentials() -> toukka.sopiva.spotify.client.current.Spotify:
    token = get_client_token()
    sender = get_sender()
    client = get_client(token, sender)
    return client


def get_spotify() -> toukka.sopiva.spotify.client.current.Spotify::
    logger.debug('get spotify')
    return get_spotify_with_user_credentials()


# END
