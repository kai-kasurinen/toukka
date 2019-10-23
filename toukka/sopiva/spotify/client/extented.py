#

from typing import Generator

import spotipy.client

from spotipy.model.paging import Paging
from spotipy.model.base import Item


class SpotifyExtended(spotipy.client.Spotify):

    def pages_from_paging(self,
                          paging: Paging
                          ) -> Generator[Paging, None, None]:
        '''all pages from Paging generator'''
        yield paging
        while paging.next:
            paging = self.next(paging)
            yield paging

    def items_from_paging(self,
                          paging: Paging
                          ) -> Generator[Item, None, None]:
        '''all items from Paging generator'''
        for page in self.pages_from_paging(paging):
            yield from page.items

    # FIXME: remove
    iterate_pages_from_paging = pages_from_paging
    iterate_items_from_paging = items_from_paging
    all_items_from_paging = items_from_paging

# END
