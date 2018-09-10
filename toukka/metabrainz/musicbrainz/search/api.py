#

from beanbag.v2 import BeanBag, GET
import urllib.parse

class MusicBrainzSearch:
    def __init__(self,
                 session=None,
                 fmt='json'):
        self.api = BeanBag('http://search.musicbrainz.org/ws/2/',
                                      session=session,
                                      use_attrdict=False)
        self.fmt = fmt


    def track(self, query, limit=25, offset=None):
        return GET(self.api.track(type='track', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def recording(self, query, limit=25, offset=None):
        return GET(self.api.recording(type='recording', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def release(self, query, limit=25, offset=None):
        return GET(self.api.release(type='release', fmt=self.fmt, limit=limit, offset=offset, query=query))

    def artist(self, query, limit=25, offset=None):
        return GET(self.api.artist(type='artist', fmt=self.fmt, limit=limit, offset=offset, query=query))


