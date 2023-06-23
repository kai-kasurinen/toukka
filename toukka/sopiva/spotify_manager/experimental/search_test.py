#

import logging

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO: MOVE!
def search_artists_by_genre(
        genre: str
        ):

    spotify = get_spotify()

    logger.debug('searching artists by genre: %s', genre)
    artists = spotify.artists_by_genre(genre)

    logger.debug('total results after filtering: %s', len(artists))

    for artist in artists:
        printer(artist)


# END
