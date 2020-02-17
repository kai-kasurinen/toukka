#

from typing import Generator, Tuple, Optional

import functools

from tekore.client import Spotify
from tekore.model.paging import Paging
from tekore.model.base import Item

import tekore.convert

from requests import HTTPError


def alter_limit(f, limit=None):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'limit' in kwargs.keys():
            return f(*args, **kwargs)
        else:
            return f(*args, **kwargs, limit=limit)
    return wrapper


def catch_404(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            ret = f(*args, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise
        else:
            return ret
    return wrapper


class SpotifyExtended(Spotify):

    # TODO: remove?
    def uri_to_item(self, uri: str) -> Item:
        uri_type, uri_id = tekore.convert.from_uri(uri)
        if uri_type == 'artist':
            return self.artist(uri_id)
        elif uri_type == 'album':
            return self.album(uri_id)
        elif uri_type == 'track':
            return self.track(uri_id)
        elif uri_type == 'playlist':
            return self.playlist(uri_id)
        else:
            raise Exception(f'unsupported uri: {uri} ({uri_type}, {uri_id})')

    @property
    def convert(self):
        return tekore.convert

# END
