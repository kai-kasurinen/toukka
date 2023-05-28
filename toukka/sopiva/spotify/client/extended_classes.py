#

from typing import Generator, Tuple, Optional

import logging

from tekore import Spotify
from tekore.model import Paging
from tekore.model import Item

from .decorators import alter_description

import toukka.sopiva.spotify.convert


class SpotifyExtendedBase(Spotify):
    pass


class SpotifyExtendedTokens(SpotifyExtendedBase):

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
    
    # END


class SpotifyExtendedTools(SpotifyExtendedBase):

    @property
    def convert(self):
        return toukka.sopiva.spotify.convert

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

    # TODO: remove?
    def currently_playing_playlist(self):
        playing = self.playback_currently_playing()

        if playing.context is None:
            return None

        if playing.context.type == 'playlist':
            return playing.context.uri
        else:
            return None

    # END
