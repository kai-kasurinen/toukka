#

from typing import Generator

from spotipy.client import Spotify
from spotipy.model.paging import Paging
from spotipy.model.base import Item

import spotipy.convert


class SpotifyExtended(Spotify):

    def uri_to_item(self, uri: str) -> Item:
        uri_type, uri_id = spotipy.convert.from_uri(uri)
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


# END
