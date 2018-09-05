#

import os
import logging
import requests
import warnings

from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from xdg.BaseDirectory import save_cache_path
from spotipy import SpotifyException
from spotipy.util import prompt_for_user_token

import discogs_client
import wikidata.client

from toukka.spotify import Spotify, SCOPES_ALL
from toukka.musicbrainz import MusicBrainz
from toukka.acousticbrainz import AcousticBrainz
from toukka.utils import Singleton
from toukka.spotify2musicbrainz import Spotify2MusicBrainz
from toukka.finna import Finna


class Hub(metaclass=Singleton):

    def __init__(self):
        self._init_cache_path()
        self._init_session()
        self._init_spotify()
        self._init_discogs()
        self._init_musicbrainz()
        self._init_spotify2musicbrainz()
        self._init_finna()
        self._init_wikidata()

    def _init_cache_path(self):
        cache_path = save_cache_path('toukka')

    def _init_session(self):
        cache_path_cachecontrol = save_cache_path('toukka', 'cachecontrol')
        cache = FileCache(cache_path_cachecontrol)
        self._session = CacheControl(requests.Session(), cache)

    def _init_spotify(self, username=None):
        if not username:
            username = os.getenv('SPOTIPY_USER')
        if not username:
            raise SpotifyException(550, -1, 'no username set')

        cache_path_tokens = save_cache_path('toukka', 'tokens')
        cache_file_for_token = os.path.join(cache_path_tokens, username)

        scope = " ".join(SCOPES_ALL)
        token = prompt_for_user_token(username, scope, cache_path=cache_file_for_token)

        self.sp = Spotify(auth=token, requests_session=self._session)
        self.sp.trace = False
        self.sp.max_get_retries = 1  # default is 10

    def _init_musicbrainz(self):
        self.mb = MusicBrainz()
        self.mbngs = self.mb.mbngs
        self.acousticbrainz = AcousticBrainz(session=self._session)

    def _init_discogs(self):
        self.discogs = discogs_client.Client('toukka/0.0.0')

    def _init_finna(self):
        self.finna = Finna(session=self._session)

    def _init_wikidata(self):
        self.wikidata = wikidata.client.Client()

    def _init_spotify2musicbrainz(self):
        dbfile = os.path.join(save_cache_path('toukka'), 'spotify2musicbrainz')
        self.sp2mb = Spotify2MusicBrainz(hub=self, dbfile=dbfile)


class Toukka(metaclass=Singleton):
    def __init__(self):
        self.hub = Hub()
        self.sp = self.hub.sp
        self.mb = self.hub.mb
        self.mbngs = self.hub.mbngs
        self.acousticbrainz = self.hub.acousticbrainz
        self.discogs = self.hub.discogs
        self.sp2mb = self.hub.sp2mb
        self.finna = self.hub.finna




# END
