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
@click.option('--filter-by-genre', multiple=True)
@click.option('--filter-by-no-genre', is_flag=True)
@click.option('--filter-by-genre-contains', multiple=True)
@click.option('--filter-by-artist-played-count', type=int)
@click.option('--filter-by-album-type')
@click.option('--filter-by-album-name-lang')
@click.option('--filter-mode')
@click.option('--sort-by-release-date', is_flag=True)
@click.option('--sort-by-album-type', is_flag=True)
@click.option('--sort-reversed', is_flag=True)
def new_releases(
        **kwargs
        ):

    spotify = get_spotify()
    spotify_history = get_spotify_history()

    albums = search_new_releases(**kwargs)

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
