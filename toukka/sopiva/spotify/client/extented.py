#

import logging
import spotipy
import spotipy.convert
import spotipy.model
import spotipy.model.paging


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class SpotifyExtended(spotipy.Spotify):

    def pager(self,
              paging: spotipy.model.paging.OffsetPaging
              ):
        '''iteraple Paging'''
        def _log_debug(paging):
            logger.debug('%s: offset:, %s, total: %s, limit: %s',
                         type(paging), paging.offset, paging.total, paging.limit)

        _log_debug(paging)
        yield paging

        while paging.next:
            paging = self.next(paging)
            _log_debug(paging)
            yield paging

    def all_items_from_paging(self,
                              paging: spotipy.model.paging.OffsetPaging
                              ):
        '''get all items from pager'''
        for page in self.pager(paging):
            for item in page.items:
                yield item


# END
