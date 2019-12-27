#

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_manager.cli import cli_root
from toukka.sopiva.spotify_history.util import get_spotify_history

from toukka.sopiva.spotify_manager.experimental.new_releases import (
    search_new_releases, album_to_genres, artists_played_counts
)


@cli_root.command()
@click.option('--market')
@click.option('--filter-by-genre')
@click.option('--filter-by-no-genre', is_flag=True)
@click.option('--filter-by-genre-contains')
@click.option('--filter-by-artist-played-count', type=int)
@click.option('--filter-by-album-type')
@click.option('--sort-by-release-date', is_flag=True)
@click.option('--sort-reversed', is_flag=True)
def new_releases(
        market: str = None,
        filter_by_genre: str = None,
        filter_by_genre_contains: str = None,
        filter_by_no_genre: bool = None,
        filter_by_artist_played_count: int = None,
        filter_by_album_type: str = None,
        sort_by_release_date: bool = False,
        sort_reversed: bool = False,
        ):

    spotify = get_spotify()
    spotify_history = get_spotify_history()

    albums = search_new_releases(**locals())

    count = 0
    for count, album in enumerate(albums, start=1):
        genres = album_to_genres(
            album,
            spotify=spotify)

        played_counts = artists_played_counts(
            album.artists,
            spotify_history=spotify_history)

        printer(album)
        print(f'\tgenres: {genres}')
        print(f'\tplayed: {played_counts}')

    print()
    print(f'results after filters: {count}')


# END
