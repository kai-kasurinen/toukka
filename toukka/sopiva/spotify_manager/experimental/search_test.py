#

import logging

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_manager.filters import make_multi_filter, make_filter_by_artist_genre

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def search_artists_by_genre(
        genre: str
        ):

    spotify = get_spotify()
    logger.debug('searching artists by genre: %s', genre)

    search = spotify.search(
        query=f'genre:"{genre}"',
        types=['artist'])
    paging = search[0]
    artists = spotify.all_items(paging)
    logger.debug(f'total results: {paging.total}')

    artists = filter(make_filter_by_artist_genre(genre), artists)

    logger.debug('total results after filtering: %s', len(list(artists)))


# END
