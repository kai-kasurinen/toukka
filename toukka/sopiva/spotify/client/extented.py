#

from typing import Generator

from spotipy.client import Spotify
from spotipy.model.paging import Paging
from spotipy.model.base import Item

import spotipy.convert


# TODO: clean (some methods added to spotipy)


class SpotifyExtended(Spotify):

    all_pages_from_paging = Spotify.all_pages
    all_items_from_paging = Spotify.all_items

#    def all_pages_from_paging(self,
#                              paging: Paging
#                              ) -> Generator[Paging, None, None]:
#        '''all pages from Paging generator'''
#        yield paging
#        while paging.next is not None:
#            paging = self.next(paging)
#            yield paging
#
#    def all_items_from_paging(self,
#                              paging: Paging
#                              ) -> Generator[Item, None, None]:
#        '''all items from Paging generator'''
#        for page in self.all_pages_from_paging(paging):
#            yield from page.items

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
