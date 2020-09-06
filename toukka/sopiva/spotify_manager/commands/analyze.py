#

from toukka.sopiva.spotify_manager.cli import cli_root

import toukka.sopiva.spotify_manager.analyze.user_playlists_artists_count
import toukka.sopiva.spotify_manager.analyze.user_analyze


@cli_root.group()
def analyze():
    pass


@analyze.command()
def analyze_user(
        **kwargs
        ):
    toukka.sopiva.spotify_manager.analyze.user_analyze.analyze_user_1(**kwargs)


@analyze.command()
def user_playlists_artists_count():
    toukka.sopiva.spotify_manager.analyze.user_playlists_artists_count.user_playlists_artists_count()

# END
