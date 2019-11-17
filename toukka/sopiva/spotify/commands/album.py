#

import click
import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.command()
@click.argument('uri')
@click.option('--market')
@click.option('--tracks', is_flag=True)
def album(uri,
          market: str = None,
          tracks: bool = False
          ):
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    spotify = get_spotify()
    album = spotify.album(uri_id, market=market)
    printer(album)
    if tracks:
        for track in spotify.all_items_from_paging(album.tracks):
            printer(track)

# END
