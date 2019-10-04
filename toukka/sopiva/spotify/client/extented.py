#

import logging
import spotipy
import spotipy.model.paging


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class SpotifyExtended(spotipy.Spotify):

    def pager(self,
              paging: spotipy.model.paging.OffsetPaging
              ):

        def _log_debug(paging):
            logger.debug('%s: offset:, %s, total: %s, limit: %s',
                         type(paging), paging.offset, paging.total, paging.limit)

        _log_debug(paging)
        yield paging

        while paging.next:
            paging = self.next(paging)
            _log_debug(paging)
            yield paging


# END
