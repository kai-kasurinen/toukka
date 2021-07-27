#

import re
import logging
import datetime
import statistics

import iso8601
import humanize
import tabulate
import argh

from toukka.sopiva.spotify.util import get_spotify
from ..cli import cli_root


@cli_root.group()
def me():
    pass


@me.command('info')
def current_user():
    '''get current user information'''
    return get_spotify().current_user().pprint()

# END
