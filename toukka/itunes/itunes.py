#

from .api import iTunesAPI

class iTunes:
    def __init__(self, session=None):
        self.api = iTunesAPI(session=session)
        self.country = 'FI'

    def search(self, **kwargs):
        return self.api.search(**kwargs)

    def lookup(self, **kwargs):
        return self.api.lookup(**kwargs)
