#

'''spotify watcher'''

import time

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root

@cli_root.command()
def watcher():

    spotify = get_spotify()
    sleep= 0
    last_cp = None
    last_context = None
    last_item = None

    while True:

        time.sleep(sleep)
        sleep = 60
        _print_dash_line()
        cp = spotify.playback_currently_playing()
    
        if cp is None:
            last_cp = cp
            continue

        if cp == last_cp:
            last_cp = cp
            continue
        else:
            printer(cp)

        if cp.context is None:
            last_context = cp.context
            continue

        if cp.context == last_context:
            last_context = cp.context
        else:
            last_context = cp.context
            printer(cp.context)
            printer(spotify.uri_to_item(cp.context.uri))

        if cp.item is None:
            last_item = cp.item
            continue
        else:
            last_item = cp.item
            printer(cp.item)

def _print_dash_line():
        print(''.ljust(100, '='))
