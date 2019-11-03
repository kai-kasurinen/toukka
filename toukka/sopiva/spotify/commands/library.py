#

import click

from toukka.sopiva.spotify.util import get_spotify

from ..cli import cli_root


@cli_root.group()
def library():
    pass


@library.command()
def saved_albums():
    return get_spotify().current_user_albums().pprint()


@library.command()
def saved_tracks():
    return get_spotify().current_user_tracks().pprint()


# END
