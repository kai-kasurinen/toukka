#

from typing import Generator, Tuple, Optional

import logging
import textwrap

from boltons.funcutils import wraps

from tekore.client import Spotify
from tekore.model.paging import Paging
from tekore.model.base import Item
from requests import HTTPError

import tekore.convert


logger = logging.getLogger(__name__)


def alter_limit(f, limit=None):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'limit' in kwargs.keys():
            return f(*args, **kwargs)
        else:
            return f(*args, **kwargs, limit=limit)
    return wrapper


def alter_description(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'description' in kwargs.keys():
            if kwargs['description'] is not None:
                description_len = len(kwargs['description'])
                if description_len > 300:
                    logger.warning('playlist description is too long (%i), shortening it', description_len)
                    kwargs['description'] = textwrap.shorten(
                        kwargs['description'], width=300)
        return f(*args, **kwargs)
    return wrapper


def catch_404(f):
    @wraps(f)
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

    # for shortening long description
    playlist_change_details = alter_description(Spotify.playlist_change_details)

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


'''
    # 2020-03-05 test
    def _create_headers(self, content_type: str = 'application/json'):
        return {
            'Authorization': f'Bearer {str(self.token)}',
            'Content-Type': content_type,
            # 'Accept-Language': 'ru'
        }
'''

# END
