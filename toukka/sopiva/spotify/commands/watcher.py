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
    
    while True:

        cp = spotify.playback_currently_playing()

        _print_dash_line()
        printer(cp)
        if cp.context and cp.context.uri:
            printer(spotify.uri_to_item(cp.context.uri))
            print()
        if cp.item:
            printer(cp.item)

        time.sleep(60)

def _print_dash_line():
        print(''.ljust(100, '='))
