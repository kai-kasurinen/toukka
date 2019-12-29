#

import spotipy

from toukka.sopiva.spotify.util import get_spotify


class HelperBase:
    def __init__(
            self,
            spotify: spotipy.Spotify = None
            ) -> None:
        self.spotify = spotify or get_spotify()


# END
