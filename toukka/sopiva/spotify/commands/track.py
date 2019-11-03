#

import click
import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from ..cli import cli_root


@cli_root.command()
@click.argument('uri')
@click.option('--market')
def track(uri: str,
          market: str = None):
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    spotify = get_spotify()
    track = spotify.track(uri_id, market=market)
    printer(track)


# END
