#

import collections

import click

from click_params import StringListParamType

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_manager.cli import cli_root
from toukka.sopiva.spotify_history.util import get_spotify_history

from toukka.sopiva.spotify_manager.experimental.new_releases import (
    search_new_releases, album_to_genres, artists_played_counts
)

from toukka.sopiva.spotify_manager.experimental.user_analyze import analyze_user_1


@cli_root.command()
@click.option('--market')
@click.option('--filter-by-genre', multiple=True)
@click.option('--filter-by-no-genre', is_flag=True)
@click.option('--filter-by-genre-contains', multiple=True)
@click.option('--filter-by-artist-played-count', type=int)
@click.option('--filter-by-album-type')
@click.option('--filter-by-album-name-lang')
@click.option('--filter-mode')
@click.option('--sort-by-keys', type=StringListParamType())
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


@cli_root.command()
def analyze_user(
        **kwargs
        ):
    analyze_user_1(**kwargs)


@cli_root.command()
def analyze_playlist_test():
    spotify = get_spotify()

    def count_artists(playlist_id: str):
        tracks = spotify.playlist_tracks(playlist_id)
        tracks = spotify.all_items(tracks)
        return collections.Counter([t.track.artists[0].name for t in tracks if t.track is not None])

    def get_artist_counters() -> collections.Counter:
        playlists = spotify.followed_playlists()
        playlists = spotify.all_items(playlists)
        counts = [count_artists(p.id) for p in playlists]
        return sum(counts, collections.Counter())

    artists = get_artist_counters()

    for name, count in artists.most_common(3):
        print(count, name)


# END
