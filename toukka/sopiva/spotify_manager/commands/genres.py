#

import pprint
import argh

import toukka.sopiva.spotify_manager.genres


def _genres_completer(prefix, **kwargs):
    genres = toukka.sopiva.spotify_manager.genres.genres().keys()
    return (genre for genre in genres if genre.startswith(prefix))

def genres():
    genres = toukka.sopiva.spotify_manager.genres.genres()
    for genre in genres.values():
        pprint.pprint(genre)


def genres_refresh():
    toukka.sopiva.spotify_manager.genres.genres_refresh()


@argh.arg('name', completer=_genres_completer)
def genre(name: str):
    genres = toukka.sopiva.spotify_manager.genres.genres()
    genre = genres.get(name)
    pprint.pprint(genre)


COMMANDS = [
    genres,
    genres_refresh,
    genre
]
