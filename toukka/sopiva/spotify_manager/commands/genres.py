#

import pprint
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


COMMANDS = [
    genres,
    genres_refresh,
    genre
]
