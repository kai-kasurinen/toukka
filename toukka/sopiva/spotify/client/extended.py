#

from typing import Generator, Tuple, Optional

import logging
import textwrap

from boltons.funcutils import wraps

from tekore import Spotify
from tekore.model import Paging
from tekore.model import Item
from tekore._error import NotFound, BadRequest

import toukka.sopiva.spotify.convert

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
                description = kwargs['description']
                description_len = len(description)
                description_len_raw = len(description.encode('utf-8'))

                if description_len_raw > 300:

                    logger.warning(
                        'playlist description is too long (%i, %i), shortening it',
                        description_len, description_len_raw)

                    shorted = textwrap.shorten(description, 300, placeholder='...')
                    shorted_len = len(shorted)
                    shorted_len_raw = len(shorted.encode('utf-8'))

                    kwargs['description'] = shorted

                    # TODO: remove
                    if shorted_len_raw > 300:
                        logger.warning(
                            'shorted description length: %i, %i',
                            shorted_len, shorted_len_raw)
                        logger.warning(shorted)

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

    # TODO: remove!
    playlist_tracks = Spotify.playlist_items

    # TODO: remove?
    def uri_to_item(self, uri: str) -> Item:
        uri_type, uri_id = self.convert.from_uri(uri)
        
        match uri_type:
            case 'artist':
                return self.artist(uri_id)
            case 'album':
                return self.album(uri_id)
            case 'track':
                return self.track(uri_id)
            case 'playlist':
                return self.playlist(uri_id)
            case 'show':
                return self.show(uri_id)
            case 'episode':
                return self.episode(uri_id)
            case 'user':
                return self.user(uri_id)
            case _:
                raise Exception(f'unsupported uri: {uri} ({uri_type}, {uri_id})')

    @property
    def convert(self):
        return toukka.sopiva.spotify.convert

    # TODO: remove, not needed anymore
    def convert_old_playlist_uri(self, uri):
        playlist_id = uri.split(':')[4]
        new_uri = self.convert.to_uri('playlist', playlist_id)
        return new_uri

    # TODO: remove?
    def currently_playing_playlist(self):
        playing = self.playback_currently_playing()

        if playing.context and playing.context.type.name == 'playlist':
            # NOTE: still old format
            # return self.convert_old_playlist_uri(playing.context.uri)
            return playing.context.uri
        else:
            return None

    # NOTE: 2022-09-22 search artist genre:rock ... offset=1000 returns BadRequest
    def next(self, page: Paging) -> Optional[Paging]:
        try:
            return super().next(page)
        except BadRequest as ex:
            logger.warning(ex)
            return

# END
