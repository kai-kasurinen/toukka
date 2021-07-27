#

'''spotify user information'''

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.cli import cli_root


@cli_root.command()
@click.argument('user_id')
def user(user_id: str):
    ''' get public profile information about a Spotify user.'''
    return get_spotify().user(user_id).pprint()


@cli_root.command()
def me():
    '''get current user information'''
    return get_spotify().current_user().pprint()


# END
