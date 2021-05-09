#

from typing import Tuple

import logging
# import pprint

import tekore

import toukka.config
import toukka.hub.requests

import toukka.sopiva.spotify.client.current
import toukka.sopiva.spotify.state

from toukka.sopiva.spotify.sender.requests_sender import RequestsSender
from toukka.sopiva.spotify.sender.caching_sender import SqliteCachingSender

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def _read_from_config() -> Tuple[str, str, str]:
    client_id = toukka.config.lazy_config['spotify']['client_id'].get()
    client_secret = toukka.config.lazy_config['spotify']['client_secret'].get()
    redirect_uri = toukka.config.lazy_config['spotify']['redirect_uri'].get()
    # TODO: return namedtuple or something
    return client_id, client_secret, redirect_uri


def get_user_refresh_token() -> str:
    logger.debug('get user refresh token from statedb')
    statedb = toukka.sopiva.spotify.state.get_statedb()
    return statedb.get('user_refresh_token')


def set_user_refresh_token(refresh_token: str) -> None:
    logger.debug('set user refresh token to statedb')
    statedb = toukka.sopiva.spotify.state.get_statedb()
    statedb.set('user_refresh_token', refresh_token)


def get_user_token() -> tekore.RefreshingToken:
    client_id, client_secret, redirect_uri = _read_from_config()
    # client_id, client_secret, client_redirect = read_environment()
    refresh_token = get_user_refresh_token()
    token = None

    if refresh_token:
        logger.debug('refresh token found, using it')
        # NOTE: use RefreshingCredentials directly to get retrying
        # NOTE: use our sender with urllib3.retry retrying
        # TODO: use RetryingSender
        sender = get_sender()
        cred = tekore.RefreshingCredentials(client_id, client_secret, sender=sender)
        # TODO: exceptions?
        token = cred.refresh_user_token(refresh_token)

    if token is None:
        logger.debug('referesh token not found, prompt user input')
        scope = tekore.Scope(tekore.scope.every)
        token = tekore.prompt_for_user_token(client_id, client_secret, scope)
        set_user_refresh_token(token.refresh_token)

    return token


def get_sender(sender_type='httpx') -> tekore.Sender:

    if sender_type == 'requests':
        session = toukka.hub.requests.get_cached_session()
        sender = RequestsSender(session=session)
    elif sender_type == 'httpx':
        #sender = tekore.CachingSender(max_size=256, sender=tekore.RetryingSender(retries=3))
        sender = SqliteCachingSender(max_size=10000, sender=tekore.RetryingSender(retries=3))
    else:
        raise Exception

    return sender


def get_client_token() -> tekore.RefreshingToken:
    # client_id, client_secret, client_redirect = tekore.util.read_environment()
    client_id, client_secret, redirect_uri = _read_from_config()
    credentials = tekore.RefreshingCredentials(client_id, client_secret)
    token = credentials.request_client_token()
    return token


def get_client(token, sender) -> toukka.sopiva.spotify.client.current.Spotify:
    client = toukka.sopiva.spotify.client.current.Spotify(
        token=token, sender=sender,
        max_limits_on=True, chunked_on=True)
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


def get_spotify() -> toukka.sopiva.spotify.client.current.Spotify:
    logger.debug('get spotify')
    return get_spotify_with_user_credentials()


# END
