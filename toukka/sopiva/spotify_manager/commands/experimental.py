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
        playlist_tracks = spotify.playlist_tracks(playlist_id)
        counter = collections.Counter()
        for playlist_track in spotify.all_items(playlist_tracks):
            if playlist_track.track is None:
                continue
            for artist in playlist_track.track.artists:
                counter += collections.Counter([artist.id])
        return counter

    def get_artist_counters() -> collections.Counter:
        playlists = spotify.followed_playlists()
        print(f'playlists count {playlists.total}')
        counter = collections.Counter()
        for playlist in spotify.all_items(playlists):
            counter += count_artists(playlist.id)
        print('all counts retrieved')
        return counter

    artists = get_artist_counters()

    for artist_id, count in artists.most_common(100):
        artist = spotify.artist(artist_id)
        print(count, artist.id, artist.name)


# END
