#

import pprint
import re
import click

import toukka.sopiva.spotify_manager.genres

from toukka.printer import printer
from toukka.sopiva.spotify_manager.cli import cli_root


@cli_root.command()
def genres():
    genres = toukka.sopiva.spotify_manager.genres.genres()
    for genre in genres.values():
        printer(genre)


@cli_root.command()
def genres_refresh():
    toukka.sopiva.spotify_manager.genres.genres_refresh()


@cli_root.command()
@click.argument('name')
def genre(name: str):
    genres = toukka.sopiva.spotify_manager.genres.genres()
    genre = genres.get(name)
    if genre is None:
        raise click.ClickException(f'genre "{name}" not found')
    printer(genre)


@cli_root.command()
@click.argument('name_re')
def genre_re(name_re: str):
    genres = toukka.sopiva.spotify_manager.genres.genres()
    genre_names_match_list = toukka.sopiva.spotify_manager.genres.genres_re(name_re)

    for genre_name in genre_names_match_list:
        genre = genres.get(genre_name)
        printer(genre)

# END
