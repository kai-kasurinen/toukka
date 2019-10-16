#

import logging

import deprecated

import spotipy
import spotipy.convert
import spotipy.model
import spotipy.model.paging


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class SpotifyExtended(spotipy.Spotify):

    def iterate_pages_from_paging(self,
                                  paging: spotipy.model.paging.OffsetPaging):
        '''pages from Paging generator'''
        yield paging
        while paging.next:
            paging = self.next(paging)
            yield paging

    def iterate_items_from_paging(self,
                                  paging: spotipy.model.paging.OffsetPaging):
        '''all items from Paging generator'''
        for page in self.iterate_pages_from_paging(paging):
            yield from page.items

    # FIXME: better?
    pages_from_paging = iterate_pages_from_paging
    items_from_paging = iterate_items_from_paging

    @deprecated.deprecated
    def pager(self,
              paging: spotipy.model.paging.OffsetPaging):
        return self.iterate_pages_from_paging(paging)

    @deprecated.deprecated
    def all_items_from_paging(self,
                              paging: spotipy.model.paging.OffsetPaging):
        return self.iterate_items_from_paging(paging)


# END
