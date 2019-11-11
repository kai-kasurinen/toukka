#


from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.group()
def follow():
    pass


@follow.command()
def followed_artists():
    spotify = get_spotify()
    paging = spotify.current_user_followed_artists()
    for artist in spotify.all_items_from_paging(paging):
        printer(artist)


# END
