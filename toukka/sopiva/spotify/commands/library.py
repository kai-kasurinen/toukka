#

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.group()
def library():
    pass


@library.command()
def saved_albums():
    spotify = get_spotify()
    paging = spotify.current_user_albums()
    for artist in spotify.all_items(paging):
        printer(artist)


@library.command()
def saved_tracks():
    spotify = get_spotify()
    paging = spotify.current_user_tracks()
    for track in spotify.all_items(paging):
        printer(track)


# END
