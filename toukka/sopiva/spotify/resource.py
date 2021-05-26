#

import toukka.sopiva.spotify.convert


class SpotifyResource:

    def __init__(self,
                 resource_type: str,
                 resource_id: str,
                 resource_str: str = None
                 ):

        self._resource_type = resource_type
        self._resource_id = resource_id
        self._resource_str = resource_str

    @classmethod
    def from_any(cls, resource_str: str):
        if resource_str.startswith('spotify:'):
            return cls.from_uri(resource_str)
        elif resource_str.startswith('https://open.spotify.com'):
            return cls.from_url(resource_str)
        else:
            raise Exception(f'unknown resource: {resource_str}')

    @classmethod
    def from_uri(cls, uri_str):
        uri = toukka.sopiva.spotify.convert.from_uri(uri_str)
        return cls(uri.type, uri.id, resource_str=uri_str)

    @classmethod
    def from_url(cls, url_str):
        url = toukka.sopiva.spotify.convert.from_url(url_str)
        return cls(url.type, url.id, resource_str=url_str)

    @property
    def id(self):
        return self._resource_id

    @property
    def type(self):
        return self._resource_type

    def to_uri(self):
        return toukka.sopiva.spotify.convert.to_uri(self.type, self.id)

    def to_url(self):
        return toukka.sopiva.spotify.convert.to_url(self.type, self.id)

    def __str__(self):
        return self.to_uri()
