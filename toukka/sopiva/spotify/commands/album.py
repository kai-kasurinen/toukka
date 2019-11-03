#

import click
import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.command()
@click.argument('uri')
@click.option('--market')
def album(uri,
          market='from_token'):
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    spotify = get_spotify()
    album = spotify.album(uri_id)
    printer(album)

#


COMMANDS = [album]

# END
