#

import logging
import itertools
import functools
import operator

# import langdetect
# from langdetect.lang_detect_exception import LangDetectException

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history
from toukka.sopiva.spotify.helper import Helper

from toukka.sopiva.spotify.filters import make_multi_filter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO: move filters


# FIXME: move
def album_to_genres(album, spotify=None):

    spotify = spotify or get_spotify()
    artists = list()

    for artist_simple in album.artists:
        artist = spotify.artist(artist_simple.id)
        artists.append(artist)

    artists_genres = [artist.genres for artist in artists]
    artists_genres = list(itertools.chain.from_iterable(artists_genres))
    return artists_genres


# FIXME: move
def artists_played_counts(artists, spotify_history=None):
    spotify_history = spotify_history or get_spotify_history()

    ret = list()
    for artist in artists:
        ret.append((artist.id, spotify_history.count_by_artist_name(artist.name)))
    return ret


def search_new_releases(
        market: str = None,
        filter_by_genre: tuple = None,
        filter_by_genre_contains: tuple = None,
        filter_by_no_genre: bool = None,
        filter_by_artist_played_count: int = None,
        filter_by_album_type: str = None,
        filter_by_album_name_lang: str = None,
        filter_mode: str = None,
        sort_by_keys: tuple = None,
        sort_reversed: bool = False,
        spotify: object = None,
        spotify_history: object = None
        ):

    def make_filter_by_genre(wanted_genre, contains=False, empty=False):
        def filter_by_genre(album):
            album_genres = album_to_genres(album, spotify)
            if empty and not album_genres:
                return True
            elif contains is False:
                if wanted_genre in album_genres:
                    return True
            elif contains is True:
                if any(wanted_genre in genre for genre in album_genres):
                    return True
            return False
        return filter_by_genre

    def make_filter_by_played_artist(wanted_count):
        def filter_by_played_artist(album):
            for artist in album.artists:
                played_count = spotify_history.count_by_artist_name(artist.name)
                if played_count >= wanted_count:
                    return True
            return False
        return filter_by_played_artist

    def make_filter_by_album_type(album_type):
        def filter_by_album_type(album):
            if album.album_type == album_type:
                return True
            else:
                return False
        return filter_by_album_type

    def make_filter_by_album_name_lang(wanted_lang):
        def filter_by_album_name_lang(album):
            try:
                detected_lang = langdetect.detect(album.name)
            except LangDetectException:
                detected_lang = None
            if detected_lang == wanted_lang:
                return True
            else:
                return False
        return filter_by_album_name_lang
    #

    spotify = spotify or get_spotify()
    spotify_history = spotify_history or get_spotify_history()
    helper = Helper(spotify=spotify)

    logger.debug('searching new releases')
    search = spotify.search(query='tag:new',
                            types=['album'],
                            market=market)
    paging = search[0]
    albums = spotify.all_items(paging)
    logger.debug(f'total results: {paging.total}')

    filters = list()
    if filter_by_genre:
        for genre in filter_by_genre:
            filters.append(make_filter_by_genre(genre))
    if filter_by_genre_contains:
        for genre in filter_by_genre_contains:
            filters.append(make_filter_by_genre(genre, contains=True))
    if filter_by_no_genre:
        filters.append(make_filter_by_genre(None, empty=True))
    if filter_by_artist_played_count:
        filters.append(make_filter_by_played_artist(filter_by_artist_played_count))
    if filter_by_album_type:
        filters.append(make_filter_by_album_type(filter_by_album_type))
    if filter_by_album_name_lang:
        filters.append(make_filter_by_album_name_lang(filter_by_album_name_lang))

    filter_mode_mappings = {'any': any, 'all': all}
    filter_mode_function = filter_mode_mappings.get(filter_mode, all)

    logger.debug(f'add {len(filters)} filters')
    albums = filter(make_multi_filter(filters, func=filter_mode_function), albums)

    if sort_by_keys:
        logger.debug(f'add sorting by {sort_by_keys}')
        albums = sorted(albums, key=operator.attrgetter(*sort_by_keys), reverse=sort_reversed)

    logger.debug('done')
    return albums




# END
