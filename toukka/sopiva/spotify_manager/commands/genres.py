#

import pprint
import re
import argh

import toukka.sopiva.spotify_manager.genres


def genres():
    genres = toukka.sopiva.spotify_manager.genres.genres()
    for genre in genres.values():
        pprint.pprint(genre)


def genres_refresh():
    toukka.sopiva.spotify_manager.genres.genres_refresh()


@argh.arg('name', completer=toukka.sopiva.spotify_manager.genres.genres_completer)
def genre(name: str):
    genres = toukka.sopiva.spotify_manager.genres.genres()
    genre = genres.get(name)
    if genre is None:
        raise argh.exceptions.CommandError(f'{name} genre not found')
    pprint.pprint(genre)


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


COMMANDS = [
    genres,
    genres_refresh,
    genre,
    genre_re
]
