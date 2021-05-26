#


import operator

import click

from click_params import StringListParamType

from toukka.printer import printer
from toukka.sopiva.spotify.cli import cli_root
from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.resource import SpotifyResource


@cli_root.command()
@click.argument('uri')
def get(uri: str):
    spotify = get_spotify()
    resource = SpotifyResource.from_any(uri)
    item = spotify.uri_to_item(resource.to_uri())
    printer(item)


# END
