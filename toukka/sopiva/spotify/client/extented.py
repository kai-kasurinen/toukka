#

import logging

import simplejson
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
            yield self.next(paging)

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

    # NOTE: requests uses simplejson when available
    # NOTE: and spotipy except json exception
    # NOTE: so fix it until it fixes somewhere else
    # SEE: https://github.com/psf/requests/issues/4842
    # SEE: https://github.com/linkedin/cruise-control/issues/927
    @staticmethod
    def _parse_json(response):
        try:
            return response.json()
        except simplejson.decoder.JSONDecodeError:
            return None


# END
