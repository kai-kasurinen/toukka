#

from toukka.sopiva.spotify_database.database.first import (
    SpotifyDB, SpotifyBannedUri, SpotifyBannedWord)
from toukka.sopiva.spotify_database.util import get_database_uri_from_config
from toukka.sopiva.spotify.util import get_spotify


class Banner:
    def __init__(self):
        self.spotify = get_spotify()
        database_uri = get_database_uri_from_config()
        self.db = SpotifyDB(database_uri)


# END
