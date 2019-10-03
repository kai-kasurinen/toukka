#

from .api import iTunesAPI

class iTunes:
    def __init__(self, session=None):
        self.api = iTunesAPI(session=session)
        self._country = 'FI'
        self._lang = 'en_us'

    def search(self, country=None, lang=None, **kwargs):
        if country is None:
            country = self._country
        if lang is None:
            lang = self._lang
        return self.api.search(country=country, lang=lang, **kwargs)

    def lookup(self, country=None, lang=None, **kwargs):
        if country is None:
            country = self._country
        if lang is None:
            lang = self._lang
        return self.api.lookup(country=country, lang=lang, **kwargs)
