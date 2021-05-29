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
    paging = spotify.saved_albums()
    for artist in spotify.all_items(paging):
        printer(artist)


@library.command()
def saved_tracks():
    spotify = get_spotify()
    paging = spotify.saved_tracks()
    for track in spotify.all_items(paging):
        printer(track)


@library.command()
def saved_episodes():
    spotify = get_spotify()
    paging = spotify.saved_episodes()
    for episode in spotify.all_items(paging):
        printer(episode)


@library.command()
def saved_shows():
    spotify = get_spotify()
    paging = spotify.saved_shows()
    for show in spotify.all_items(paging):
        printer(show)



# END
