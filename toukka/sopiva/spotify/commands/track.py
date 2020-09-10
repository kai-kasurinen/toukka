#

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from ..cli import cli_root


@cli_root.command()
@click.argument('uri')
@click.option('--market')
def track(uri: str,
          market: str = None):
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    track = spotify.track(uri_id, market=market)
    printer(track)


@cli_root.command()
@click.argument('uri')
def track_audio_features(uri: str):
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    track_features = spotify.track_audio_features(uri_id)
    printer(track_features)


@cli_root.command()
@click.argument('uri')
def track_audio_analysis(uri: str):
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    track_analysis = spotify.track_audio_analysis(uri_id)
    printer(track_analysis)

# END
