#

import sys
import logging
import pprint
import dataclasses
import re

import click
import click_logging

import toukka.logger.simple


from toukka.sopiva.spotify_manager.commands.playlist_generator import (
    from_uris,
    from_genres,
    from_genres_re,
    from_search,
    from_recommendations
)


from toukka.sopiva.spotify_manager.genres import click_genre_completer

#

__version__ = '0.0.0'
__program_name__ = 'toukka-play'
__program_description__ = 'some personal shortcuts'


##

kwargs_for_playlist = {
    'progress_bar': True,
    'expand_playlist_to_items': True,
    'expand_track_to_album': True,
    'expand_track_to_artists': False,
    'expand_album_to_tracks': True,
    'expand_artist_to_albums': False,
    'expand_artist_to_recommendations': False
}

kwargs_for_genre = {
    'progress_bar': True,
    'expand_genre_to_playlists': True,
    'expand_genre_to_related_genres': True,
    'expand_playlist_to_items': True,
    'expand_track_to_album': True,
    'expand_track_to_artists': False,
    'expand_album_to_tracks': True,
    'expand_artist_to_albums': False,
    'expand_artist_to_recommendations': False,
    'ignore_various_artists_albums': True,
    'ignore_played_albums': True
}

kwargs_for_genre_artists = {
    'progress_bar': True,
    'expand_genre_to_artists': True,
    'expand_artist_to_random_album': True,
    'expand_artist_to_related_artists': True,
    'expand_album_to_tracks': True,
    'randomize_artists': True,
    'ignore_various_artists_albums': True,
    'ignore_played_albums': True
}

kwargs_for_genre_artists_re = {
    'progress_bar': True,
    'expand_genre_to_artists': True,
    'expand_artist_to_random_album': True,
    'expand_artist_to_related_artists': True,
    'expand_album_to_tracks': True,
    'randomize_artists': True,
    'randomize_genres': True,
    'ignore_various_artists_albums': True,
    'ignore_played_albums': True
}

kwargs_for_uri = {
    'progress_bar': True,
    'expand_playlist_to_items': True,
    'expand_track_to_album': True,
    'expand_track_to_artists': False,
    'expand_album_to_tracks': True,
    'expand_artist_to_albums': True,
    'expand_artist_to_related_artists': True,
    'expand_artist_to_recommendations': False,
    'expand_show_to_episodes': True
}

kwargs_for_uri_second = {
    'progress_bar': True,
    'expand_playlist_to_items': True,
    'expand_track_to_album': True,
    'expand_track_to_artists': True,
    'expand_album_to_tracks': True,
    'expand_artist_to_albums': False,
    'expand_artist_to_related_artists': False,
    'expand_artist_to_recommendations': True
}

kwargs_for_uri_third = {
    'progress_bar': True,
    'expand_playlist_to_items': True,
    'expand_track_to_album': True,
    'expand_track_to_artists': True,
    'expand_album_to_tracks': True,
    'expand_artist_to_albums': False,
    'expand_artist_to_top_tracks': True,
    'expand_artist_to_related_artists': True,
    'expand_artist_to_recommendations': False
}


@click.group()
@click.version_option(version=__version__)
@click_logging.simple_verbosity_option(None, '--loglevel')
def cli():
    pass


@cli.command()
@click.argument('uris', required=True, nargs=-1)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--ignore-non-instrumental-albums', '--instrumental-only', is_flag=True)
def uri(uris: tuple,
        **kwargs):
    args = locals()
    context = click.get_current_context()
    context.invoke(from_uris, **args, **kwargs, **kwargs_for_uri)


@cli.command()
@click.argument('uris', required=True, nargs=-1)
@click.option('--dry-run', is_flag=True, default=False)
def uri2(uris: tuple,
         **kwargs):
    args = locals()
    context = click.get_current_context()
    context.invoke(from_uris, **args, **kwargs, **kwargs_for_uri_second)


@cli.command()
@click.argument('uris', required=True, nargs=-1)
@click.option('--dry-run', is_flag=True, default=False)
def uri3(uris: tuple,
         **kwargs):
    args = locals()
    context = click.get_current_context()
    context.invoke(from_uris, **args, **kwargs, **kwargs_for_uri_third)


# FIXME: autocompletion
@cli.command()
@click.argument('genre_name', required=True, nargs=-1, shell_complete=click_genre_completer)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--ignore-non-instrumental-albums', '--instrumental-only', is_flag=True)
def genre(genre_name: tuple,
          **kwargs
          ):
    args = locals()
    context = click.get_current_context()
    context.invoke(from_genres, **args, **kwargs, **kwargs_for_genre)


@cli.command()
@click.argument('genre_name_re', required=True, nargs=-1)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--ignore-non-instrumental-albums', '--instrumental-only', is_flag=True)
def genre_re(genre_name_re: str,
             **kwargs
             ):
    args = locals()
    context = click.get_current_context()
    context.invoke(from_genres_re, **args, **kwargs, **kwargs_for_genre)

##


@cli.command()
@click.argument('genre_name', required=True, nargs=-1, shell_complete=click_genre_completer)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--ignore-non-instrumental-albums', '--instrumental-only', is_flag=True)
def genre_artists(genre_name: tuple, **kwargs):
    args = locals()
    context = click.get_current_context()
    context.invoke(from_genres, **args, **kwargs, **kwargs_for_genre_artists)


@cli.command()
@click.argument('genre_name_re', required=True, nargs=-1, shell_complete=click_genre_completer)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--ignore-non-instrumental-albums', '--instrumental-only', is_flag=True)
def genre_artists_re(genre_name_re: str, **kwargs):
    args = locals()
    context = click.get_current_context()
    context.invoke(from_genres_re, **args, **kwargs, **kwargs_for_genre_artists_re)


def main():
    toukka.logger.simple.init_logging()
    # toukka.logger.simple.set_logging_level_to_trace()
    # FIXME: format?
    # click_logging.basic_config()
    cli.main()


# END
