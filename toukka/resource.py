#

from urlobject import URLObject


class ResourceURL:

    def __init__(self, url_string):
        self.url = URLObject(url_string)
        # FIXME
        self._init_resource()

    def _init_resource(self):
        # FIXME: use property or something
        self.service = None
        self.entity_type = None
        self.entity_id = None

        if self.url.hostname == 'musicbrainz.org':
            self.service = 'musicbrainz'
            self.entity_type = self.url.path.segments[0]
            self.entity_id = self.url.path.segments[0]
        # https://www.discogs.com/Marja-Mattlar-Kuu/release/3605462
        # https://www.discogs.com/release/3605462
        elif self.url.hostname == 'www.discogs.com':
            self.service = 'discogs'
            self.entity_type = self.url.path.segments[0]
            self.entity_id = self.url.path.segments[1]
        elif self.url.hostname == 'open.spotify.com':
            self.service = 'spotify'
            self.entity_type = self.url.path.segments[0]
            self.entity_id = self.url.path.segments[1]
        # https://viola.linneanet.fi/vwebv/holdingsInfo?bibId=632917
        elif self.url.hostname == 'viola.linneanet.fi':
            self.service = 'viola'
        else:
            self.service = None


class ResourceURI:
    pass


# END
