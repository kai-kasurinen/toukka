#

import logging
import itertools
import functools

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_manager.cli import cli_root

logger = logging.getLogger(__name__)


@cli_root.command()
@click.option('--market')
@click.option('--limit', type=int)
def new_albums(limit: int = None, market: str = None):

    def album_to_genres(album):
        artists = list()

        for artist_simple in album.artists:
            artist = spotify.artist(artist_simple.id)
            artists.append(artist)

        artists_genres = [artist.genres for artist in artists]
        artists_genres = list(itertools.chain.from_iterable(artists_genres))
        return artists_genres

    def filter_by_genre(album, wanted_genre=None, contains=False):
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
    #

    spotify = get_spotify()

    search = spotify.search(query='tag:new',
                            types=['album'],
                            market=market)
    paging = search[0]
    print(f'results total: {paging.total}')
    print()

    albums = spotify.all_items(paging)
    genre_filter = functools.partial(filter_by_genre, wanted_genre='post-rock', contains=True)
    albums = filter(genre_filter, albums)

    for count, album in enumerate(albums, start=1):
        printer(album)
        print(f'\tgenres: {album_to_genres(album)}')

        if limit is not None and count >= limit:
            break


# END
