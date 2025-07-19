#

'''spotify user information'''

import pprint

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.cli import cli_root
from toukka.printer import printer


@cli_root.command()
@click.argument('user_id')
def user(user_id: str):
    ''' get public profile information about a Spotify user'''
    pprint.pprint(get_spotify().user(user_id))


@cli_root.command()
def me():
    '''get current user information'''
    pprint.pprint(get_spotify().current_user())


# END
