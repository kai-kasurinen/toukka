#

import logging

from beanbag.v2 import BeanBag, GET, BeanBagException

from ..exceptions import MusicBrainzRateLimitException
from ..ratelimiter import musicbrainz_server_ratelimit_sleeper, musicbrainz_search_server_ratelimit_sleeper


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MusicBrainzSearch:
    def __init__(self, session=None, use_ratelimiter=True):
        self._use_ratelimiter = use_ratelimiter
        self.api = BeanBag('https://search.musicbrainz.org/ws/2/', session=session, use_attrdict=False)
        self.fmt = 'jsonnew'

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
                raise MusicBrainzRateLimitException(error.response, 'MusicBrainz search server ratelimiting')
            else:
                raise

    def artist(self, query, limit=25, offset=None):
        return self._GET(self.api.artist(type='artist', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def track(self, query, limit=25, offset=None):
        return self._GET(self.api.track(type='track', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def recording(self, query, limit=25, offset=None):
        return self._GET(self.api.recording(type='recording', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def release(self, query, limit=25, offset=None):
        return self._GET(self.api.release(type='release', fmt=self.fmt, limit=limit, offset=offset, query=query))


# END
