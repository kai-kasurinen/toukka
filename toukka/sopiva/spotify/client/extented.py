#

from typing import Generator, Tuple

from tekore.client import Spotify
from tekore.model.paging import Paging
from tekore.model.base import Item

import tekore.convert


class SpotifyExtended(Spotify):

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

    # FIXME: move?
    def convert_from_uri(self, uri: str) -> Tuple:
        return tekore.convert.from_uri(uri)

# END
