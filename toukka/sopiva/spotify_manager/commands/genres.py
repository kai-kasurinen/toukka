#

import pprint
import re
import click

import toukka.sopiva.spotify_manager.genres

from toukka.sopiva.spotify_manager.cli import cli_root


@cli_root.command()
def genres():
    genres = toukka.sopiva.spotify_manager.genres.genres()
    for genre in genres.values():
        pprint.pprint(genre)


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
    pprint.pprint(genre)


@cli_root.command()
@click.argument('name_re')
def genre_re(name_re: str):
    regex = re.compile(name_re)
    genres = toukka.sopiva.spotify_manager.genres.genres()
    # NOTE:
    # If the whole string matches this regular expression,
    # return a corresponding match object.
    # Return None if the string does not match the pattern
    #
    # match object is True and None is False
    genre_names_match = filter(regex.fullmatch, genres.keys())

    for g in genre_names_match:
        genre = genres.get(g)
        pprint.pprint(genre)


# END
