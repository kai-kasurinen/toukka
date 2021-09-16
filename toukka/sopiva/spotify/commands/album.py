#

import click

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
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    album = spotify.album(uri_id, market=market)
    printer(album)
    if tracks:
        for track in spotify.all_items(album.tracks):
            printer(track)

# END


@cli_root.command()
@click.argument('uri')
@click.option('--market')
@click.option('--full', is_flag=True)
def album_tracks(
        uri,
        market: str = None,
        full: bool = False
        ):

    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    album_tracks_pager = spotify.album_tracks(uri_id, market=market)
    album_tracks = spotify.all_items(album_tracks_pager)

    for album_track in album_tracks:
        if full:
            printer(spotify.track(album_track.id))
        else: 
            printer(album_track)

# END
