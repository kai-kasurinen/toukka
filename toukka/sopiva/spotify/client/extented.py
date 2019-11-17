#

from typing import Generator

from spotipy.client import Spotify
from spotipy.model.paging import Paging
from spotipy.model.base import Item


# TODO: clean (methods added to spotipy


class SpotifyExtended(Spotify):

    def all_pages_from_paging(self,
                              paging: Paging
                              ) -> Generator[Paging, None, None]:
        '''all pages from Paging generator'''
        yield paging
        while paging.next is not None:
            paging = self.next(paging)
            yield paging

    def all_items_from_paging(self,
                              paging: Paging
                              ) -> Generator[Item, None, None]:
        '''all items from Paging generator'''
        for page in self.all_pages_from_paging(paging):
            yield from page.items


# END
