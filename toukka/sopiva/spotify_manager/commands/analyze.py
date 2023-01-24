#

import click

from toukka.sopiva.spotify_manager.cli import cli_root

import toukka.sopiva.spotify_manager.analyze.user_playlists_artists_count
import toukka.sopiva.spotify_manager.analyze.user_analyze
import toukka.sopiva.spotify_manager.analyze.playlist
import toukka.sopiva.spotify_manager.analyze.artist_related_artists


@cli_root.group()
def analyze():
    pass


@analyze.command()
def analyze_user(**kwargs):
    toukka.sopiva.spotify_manager.analyze.user_analyze.analyze_user_1(**kwargs)


@analyze.command()
def user_playlists_artists_count():
    toukka.sopiva.spotify_manager.analyze.user_playlists_artists_count.user_playlists_artists_count()


@analyze.command()
def playlist():
    toukka.sopiva.spotify_manager.analyze.playlist.analyze_playlist()


@analyze.command()
def album(**kwargs):
    toukka.sopiva.spotify_manager.analyze.album.analyze_album(**kwargs)


@analyze.command()
@click.argument('artist_uri')
def artist_related_test(**kwargs):
    toukka.sopiva.spotify_manager.analyze.artist_related_artists.artist_related_artists_test(**kwargs)

# END
