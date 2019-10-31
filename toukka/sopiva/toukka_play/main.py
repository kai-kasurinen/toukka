#

import sys
import logging
import pprint
import dataclasses
import re

import click
import click_log
#import click_completion
#click_completion.init()

import toukka.logger.simple

from toukka.sopiva.spotify_manager.commands.playlist_generator_commands import (
    generate_playlist_from_uris,
    generate_playlist_from_search,
    generate_playlist_from_recommendations,
    generate_playlist_from_genres
)

from toukka.sopiva.spotify_manager.genres import genres_completer

#

__version__ = '0.0.0'
__program_name__ = 'toukka-play'
__program_description__ = 'some personal shortcuts'


##

kwargs_default = {
    'expand_track_to_album': False,
    'expand_track_to_artist': False,
    'expand_artist_to_albums': False,
    'expand_artist_to_top_tracks': False,
    'expand_artist_to_related_artists': False,
    'expand_album_to_tracks': False,
    'expand_playlist_to_tracks': False,
    'expand_generator_to_items': False
}

kwargs_for_playlist = {
    'expand_generator_to_items': True,
    'expand_playlist_to_tracks': True,
    'expand_track_to_album': True,
    'expand_album_to_tracks': True
}

kwargs_for_related_artists = {
    'expand_generator_to_items': True,
    'expand_album_to_tracks': True,
    'expand_artist_to_related_artists': True,
    'expand_artist_to_albums': True
}

kwargs_for_uris = {
    'expand_generator_to_items': True,
    'expand_playlist_to_tracks': True,
    'expand_track_to_album': True,
    'expand_album_to_tracks': True,
    'expand_artist_to_albums': True,
    'expand_artist_to_related_artists': True
}


# FIXME: not work?
#
# ctx - The current click context.
# args - The list of arguments passed in.
# incomplete - The partial word that is being completed, as a string.
#              May be an empty string '' if no characters have been entered yet.
def click_genre_completer(ctx, args, incomplete):
    return genres_completer(incomplete)


@click.group()
@click.version_option(version=__version__)
@click_log.simple_verbosity_option(None, '--loglevel')
def cli():
    pass


@cli.command()
@click.argument('uris', required=True, nargs=-1)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--randomize', is_flag=True, default=False)
def uri(uris: tuple,
        dry_run: bool = False,
        randomize: bool = False
        ):
    generate_playlist_from_uris(**locals(), **kwargs_for_uris)


# FIXME: autocompletion
@cli.command()
@click.argument('genre_name', required=True, nargs=-1, autocompletion=click_genre_completer)
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--randomize', is_flag=True, default=False)
def genre(genre_name: tuple,
          dry_run: bool = False,
          randomize: bool = False
          ):
    generate_playlist_from_genres(**locals(), **kwargs_for_playlist)


@cli.command()
@click.argument('genre_name_re')
@click.option('--dry-run', is_flag=True, default=False)
@click.option('--randomize', is_flag=True, default=False)
def genre_re(genre_name_re: str,
             dry_run: bool = False,
             randomize: bool = False
             ):
    args = locals()
    args.pop('genre_name_re')
    regex = re.compile(genre_name_re)
    genres = toukka.sopiva.spotify_manager.genres.genres()
    genre_names_match = filter(regex.fullmatch, genres.keys())
    generate_playlist_from_genres(genre_name=genre_names_match, **args, **kwargs_for_playlist)

##


def main():
    toukka.logger.simple.init_logging()
    #toukka.logger.simple.set_logging_level_to_trace()
    # FIXME: format?
    click_log.basic_config()
    cli()


# END
