#

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.group()
def podcast():
    pass


@podcast.command()
@click.argument('uri')
@click.option('--market')
@click.option('--episodes', is_flag=True)
def show(uri,
         market: str = None,
         episodes: bool = False
         ):
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    show = spotify.show(uri_id, market=market)
    printer(show)
    if episodes:
        for episode in spotify.all_items(show.episodes):
            printer(episode)


@podcast.command()
@click.argument('uri')
@click.option('--market')
def episode(uri,
            market: str = None
            ):
    spotify = get_spotify()
    uri_type, uri_id = spotify.convert.from_uri(uri)
    episode = spotify.episode(uri_id, market=market)
    printer(episode)

# END
