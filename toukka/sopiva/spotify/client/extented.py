#

from typing import Generator, Tuple, Optional

import logging
import textwrap

from boltons.funcutils import wraps

from tekore.client import Spotify
from tekore.model.paging import Paging
from tekore.model.base import Item
# from requests import HTTPError

from tekore.client.process import top_item, nothing
from tekore.client.chunked import chunked, return_last
from tekore.client.decor import send_and_process

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


'''
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
'''


class SpotifyExtended(Spotify):

    # for shortening long description
    playlist_change_details = alter_description(Spotify.playlist_change_details)

    # TODO: remove?
    def uri_to_item(self, uri: str) -> Item:
        uri_type, uri_id = self.convert.from_uri(uri)
        if uri_type == 'artist':
            return self.artist(uri_id)
        elif uri_type == 'album':
            return self.album(uri_id)
        elif uri_type == 'track':
            return self.track(uri_id)
        elif uri_type == 'playlist':
            return self.playlist(uri_id)
        elif uri_type == 'show':
            return self.show(uri_id)
        elif uri_type == 'episode':
            return self.episode(uri_id)
        else:
            raise Exception(f'unsupported uri: {uri} ({uri_type}, {uri_id})')

    @property
    def convert(self):
        return tekore.convert

    @chunked('uris', 2, 100, return_last, reverse='position', reverse_pos=3)
    @send_and_process(top_item('snapshot_id'))
    def playlist_uris_add(
            self,
            playlist_id: str,
            uris: list,
            position: int = None
    ) -> str:
        logger.info(uris)
        payload = {'uris': uris}
        return self._post(
            f'playlists/{playlist_id}/tracks',
            payload=payload,
            position=position
        )


# END
