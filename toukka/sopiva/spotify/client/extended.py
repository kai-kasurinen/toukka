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

                    shorted = textwrap.shorten(description, 298, placeholder='...')
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


class SpotifyExtended(Spotify):
    
    @property
    def client_token(self):
        return self._client_token
    
    @client_token.setter
    def client_token(self, token):
        self._client_token = token

    def client_as(self):
        return self.token_as(self._client_token)
    
    @property
    def user_token(self):
        return self._user_token
    
    @user_token.setter
    def user_token(self, token):
        self._user_token = token

    def user_as(self):
        return self.token_as(self._user_token)

    # for shortening long description
    playlist_change_details = alter_description(Spotify.playlist_change_details)

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

    # TODO: remove?
    def currently_playing_playlist(self):
        playing = self.playback_currently_playing()

        if playing.context and playing.context.type.name == 'playlist':
            # NOTE: still old format
            # return self.convert_old_playlist_uri(playing.context.uri)
            return playing.context.uri
        else:
            return None

    # TODO: move?
    def album_audio_features(self, album_id):
        album_tracks = self.all_items(self.spotify.album_tracks(album_id))
        track_ids = [track.id for track in album_tracks]
        album_audio_features = self.tracks_audio_features(track_ids)
        if len(track_ids) != len(album_audio_features):
            logger.warning('album_audio_features len mismatch: tracks %i, features: %i',
                           len(track_ids), len(album_audio_features))
        return album_audio_features

    # END


# END
