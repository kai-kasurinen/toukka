#


import operator

import click

from click_params import StringListParamType

from toukka.printer import printer
from toukka.sopiva.spotify.cli import cli_root
from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.resource import SpotifyResource


@cli_root.command()
@click.argument('resource_str')
def get(resource_str: str):
    spotify = get_spotify()
    resource = SpotifyResource.from_any(resource_str)
    item = spotify.uri_to_item(resource.to_uri())
    printer(item)


# END
