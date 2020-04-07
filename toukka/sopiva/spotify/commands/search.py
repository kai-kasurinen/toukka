#

import click

import tekore

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root

# TODO: support multiple types

# GRR
_types = {k[:-1] for k in tekore.client.api.search.paging_type.keys()}


@cli_root.command()
@click.argument('type', type=click.Choice(_types))
@click.argument('query')
@click.option('--market')
@click.option('--limit', type=int)
def search(type: str,
           query: str,
           limit: int = None,
           market: str = None):
    spotify = get_spotify()
    search = spotify.search(query=query,
                            types=[type],
                            market=market)
    paging = search[0]
    print(f'results total: {paging.total}')
    print()

    for count, item in enumerate(spotify.all_items(paging), start=1):
        printer(item)

        if limit is not None and count >= limit:
            break


# END
