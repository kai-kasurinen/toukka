#

import click
import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.group()
def podcast():
    pass


@podcast.command()
@click.argument('uri')
@click.option('--market')
def show(uri,
         market: str = 'from_token'
         ):
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    spotify = get_spotify()
    show = spotify.show(uri_id, market=market)
    printer(show)


@podcast.command()
@click.argument('uri')
@click.option('--market')
def episode(uri,
            market: str = 'from_token'
            ):
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    spotify = get_spotify()
    episode = spotify.episode(uri_id, market=market)
    printer(episode)

# END
