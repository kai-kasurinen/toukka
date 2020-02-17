#

import tekore

from toukka.sopiva.spotify.util import get_spotify


class HelperBase:
    def __init__(
            self,
            spotify: tekore.Spotify = None
            ) -> None:
        self.spotify = spotify or get_spotify()


# END
