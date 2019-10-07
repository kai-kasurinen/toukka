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
        '''iteraple pages from Paging'''
        yield paging
        while paging.next:
            paging = self.next(paging)
            yield paging

    def iterate_items_from_paging(self,
                                  paging: spotipy.model.paging.OffsetPaging):
        '''iteraple items from paging'''
        for page in self.iterate_pages_from_paging(paging):
            for item in page.items:
                yield item

    @deprecated.deprecated
    def pager(self,
              paging: spotipy.model.paging.OffsetPaging):
        return self.iterate_pages_from_paging(paging)

    @deprecated.deprecated
    def all_items_from_paging(self,
                              paging: spotipy.model.paging.OffsetPaging):
        return self.iterate_items_from_paging(paging)


# END
