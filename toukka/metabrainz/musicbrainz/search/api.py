#

from beanbag.v2 import BeanBag, GET, BeanBagException
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo


class MusicBrainzError(Exception):
    pass


class MusicBrainzError503(Exception):
    pass


class MusicBrainzSearch:
    def __init__(self,
                 session=None):
        self.api = BeanBag('https://search.musicbrainz.org/ws/2/',
                                      session=session,
                                      use_attrdict=False)
        self.fmt = 'jsonnew'


    @on_exception(expo, MusicBrainzError503, max_tries=8)
    @on_exception(expo, RateLimitException, max_tries=8)
    @limits(calls=1, period=1)
    def _GET(self, url, body=None):
        try:
            ret = GET(url)
        except BeanBagException as error:
            if error.response.status_code == 503:
                raise MusicBrainzError503()

    def artist(self, query, limit=25, offset=None):
        return self._GET(self.api.artist(type='artist', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def track(self, query, limit=25, offset=None):
        return self._GET(self.api.track(type='track', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def recording(self, query, limit=25, offset=None):
        return self._GET(self.api.recording(type='recording', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def release(self, query, limit=25, offset=None):
        return self._GET(self.api.release(type='release', fmt=self.fmt, limit=limit, offset=offset, query=query))



