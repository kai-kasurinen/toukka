#

import logging

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def analyze_playlist(playlist_uri=None):
    spotify = get_spotify()

    playlist_uri = playlist_uri or spotify.currently_playing_playlist()

    if playlist_uri is None:
        raise Exception()


