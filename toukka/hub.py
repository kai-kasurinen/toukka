#

import os
import logging
import requests
import warnings

from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from xdg.BaseDirectory import save_cache_path
from spotipy.util import prompt_for_user_token
from toukka.spotify import Spotify, SCOPES_ALL
from toukka.musicbrainz import MusicBrainz


class SpotifyScoped:
    def __init__(self, username=None):

        scope = " ".join(SCOPES_ALL)

        if not username:
            username = os.getenv('SPOTIPY_USER')

        if not username:
            raise spotipy.SpotifyException(550, -1, 'no username set')

        cache_path = save_cache_path('toukka')
        cache_path_cachecontrol = save_cache_path('toukka', 'cachecontrol')
        cache_path_tokens = save_cache_path('toukka', 'tokens')
        cache_file_for_token = os.path.join(cache_path_tokens, username)

        token = prompt_for_user_token(username, scope, cache_path=cache_file_for_token)

        cache = FileCache(cache_path_cachecontrol)
        session = CacheControl(requests.Session(), cache)

        self.sp = Spotify(auth=token, requests_session=session)
        self.sp.trace = False
        self.sp.max_get_retries = 1  # default is 10



class Toukka(SpotifyScoped, MusicBrainz):
    def __init__(self):
        SpotifyScoped.__init__(self)
        self.mb = MusicBrainz()
        self.mbngs = self.mb.mbngs


# END
