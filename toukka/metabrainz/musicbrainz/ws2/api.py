#

import logging

from beanbag.v2 import BeanBag, GET, BeanBagException

from ..exceptions import MusicBrainzRateLimitException
from ..ratelimiter import musicbrainz_server_ratelimit_sleeper


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MusicBrainzWS2:
    def __init__(self, session=None, use_ratelimiter=True):
        self._use_ratelimiter = use_ratelimiter
        self.api = BeanBag('https://musicbrainz.org/ws/2/', session=session, use_attrdict=False)
        self.fmt = 'json'

    def _ratelimiter(self):
        return musicbrainz_server_ratelimit_sleeper()

    def _GET(self, url, body=None):
        if self._use_ratelimiter:
            self._ratelimiter()
        try:
            return GET(url)
        except BeanBagException as error:
            if error.response.status_code == 503:
                logger.debug('got musicbrainz ratelimiting error')
                logger.debug(error.response.headers)
                raise MusicBrainzRateLimitException(error.response, 'musicbrainz ratelimiting')
            else:
                raise

    def _GET_ENTITY(self, entity_type, mbid, includes=None):
        return self._GET(self.api[entity_type][mbid](fmt=self.fmt, inc=includes))

    def _BROWSE_ENTITY(self, entity_type, filters, limit=None, offset=None, includes=None):
        return self._GET(self.api[entity_type](filters, fmt=self.fmt, limit=limit, offset=offset, inc=includes))

    def area(self, mbid, includes=None):
        return self._GET_ENTITY('area', mbid, includes=includes)

    def artist(self, mbid, includes=None):
        return self._GET_ENTITY('artist', mbid, includes=includes)

    def event(self, mbid, includes=None):
        return self._GET_ENTITY('event', mbid, includes=includes)

    def instrument(self, mbid, includes=None):
        return self._GET_ENTITY('instument', mbid, includes=includes)

    def label(self, mbid, includes=None):
        return self._GET_ENTITY('label', mbid, includes=includes)

    def place(self, mbid, includes=None):
        return self._GET_ENTITY('place', mbid, includes=includes)

    def recording(self, mbid, includes=None):
        return self._GET_ENTITY('recording', mbid, includes=includes)

    def release(self, mbid, includes=None):
        return self._GET_ENTITY('release', mbid, includes=includes)

    def release_group(self, mbid, includes=None):
        return self._GET_ENTITY('release-group', mbid, includes=includes)

    def series(self, mbid, includes=None):
        return self._GET_ENTITY('series', mbid, includes=includes)

    def work(self, mbid, includes=None):
        return self._GET_ENTITY('work', mbid, includes=includes)

    def url(self, mbid, includes=None):
        return self._GET_ENTITY('url', mbid, includes=includes)

    def discid(self, discid, includes=None, toc=None):
        return self._GET_ENTITY('discid', discid, includes=includes, toc=toc)

    def isrc(self, isrc, includes=None):
        return self._GET_ENTITY('isrc', isrc, includes=includes)

    def iswc(self, iswc, includes=None):
        return self._GET_ENTITY('iswc', iswc, includes=includes)


# END
