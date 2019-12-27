#

import logging
import itertools
import functools
import operator

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_manager.cli import cli_root
from toukka.sopiva.spotify_history.util import get_spotify_history

logger = logging.getLogger(__name__)


@cli_root.command()
@click.option('--market')
@click.option('--limit', type=int)
@click.option('--filter-by-genre')
@click.option('--filter-by-genre-contains')
@click.option('--filter-by-artist-played-count', type=int)
@click.option('--filter-by-album-type')
@click.option('--sort-by-release-date', is_flag=True)
@click.option('--sort-reversed', is_flag=True)
def new_albums(
        limit: int = None,
        market: str = None,
        filter_by_genre: str = None,
        filter_by_genre_contains: str = None,
        filter_by_artist_played_count: int = None,
        filter_by_album_type: str = None,
        sort_by_release_date: bool = False,
        sort_reversed: bool = False,
        ):

    def album_to_genres(album):
        artists = list()

        for artist_simple in album.artists:
            artist = spotify.artist(artist_simple.id)
            artists.append(artist)

        artists_genres = [artist.genres for artist in artists]
        artists_genres = list(itertools.chain.from_iterable(artists_genres))
        return artists_genres

    def artists_played_counts(artists):
        ret = list()
        for artist in artists:
            ret.append((artist.id, spotify_history.count_by_artist_name(artist.name)))
        return ret

    def make_filter_by_genre(wanted_genre, contains=False):
        def filter_by_genre(album):
            album_genres = album_to_genres(album)
            if contains is False:
                if wanted_genre in album_genres:
                    return True
                else:
                    return False
            elif contains is True:
                if any(wanted_genre in genre for genre in album_genres):
                    return True
                else:
                    return False
        return filter_by_genre

    def make_filter_by_played_artist(wanted_count):
        def filter_by_played_artist(album):
            for artist_simple in album.artists:
                played_count = spotify_history.count_by_artist_name(artist_simple.name)
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
    #

    spotify = get_spotify()
    spotify_history = get_spotify_history()

    search = spotify.search(query='tag:new',
                            types=['album'],
                            market=market)
    paging = search[0]
    print(f'results total: {paging.total}')
    print()

    filters = list()
    if filter_by_genre:
        filters.append(make_filter_by_genre(filter_by_genre))
    if filter_by_genre_contains:
        filters.append(make_filter_by_genre(filter_by_genre_contains, contains=True))
    if filter_by_artist_played_count:
        filters.append(make_filter_by_played_artist(filter_by_artist_played_count))
    if filter_by_album_type:
        filters.append(make_filter_by_album_type(filter_by_album_type))

    albums = spotify.all_items(paging)
    albums = filter(make_multi_filter(filters), albums)

    if sort_by_release_date:
        albums = sorted(albums, key=operator.attrgetter('release_date'), reverse=sort_reversed)

    for album in albums:
        printer(album)
        print(f'\tgenres: {album_to_genres(album)}')
        print(f'\tplayed: {artists_played_counts(album.artists)}')

    print(f'results after filters: {len(albums)}')


def make_multi_filter(filters):
    def multi_filter(x):
        return all([f(x) for f in filters])
    return multi_filter

# END
