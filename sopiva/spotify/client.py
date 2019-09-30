#

import logging
import spotipy

import sopiva.spotify.client_cached
import sopiva.config


def _read_from_config():
    client_id = sopiva.config.lazy_config['spotify']['client_id'].get()
    client_secret = sopiva.config.lazy_config['spotify']['client_secret'].get()
    redirect_uri = sopiva.config.lazy_config['spotify']['redirect_uri'].get()
    user = sopiva.config.lazy_config['spotify']['user'].get()
    return client_id, client_secret, redirect_uri


def get_spotify_with_client_credentials():
    #client_id, client_secret, client_redirect = spotipy.util.read_environment()
    client_id, client_secret, client_redirect = _read_from_config()
    credentials = spotipy.auth.Credentials(client_id, client_secret, client_redirect)
    token = credentials.request_client_token()
    client = sopiva.spotify.client_cached.CachedSpotify(token,
                                                        sender=spotipy.sender.PersistentSender())
    return client


def get_spotify_with_user_credentials():
    client_id, client_secret, client_redirect = read_environment()
    scope = spotipy.Scope(*spotipy.scopes)
    token = spotipy.util.prompt_for_user_token(client_id, client_secret, client_redirect_uri, scope)
    client = spotipy.Spotify(token)
    return client


# END
