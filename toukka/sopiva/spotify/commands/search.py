#

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root


@cli_root.command()
@click.argument('type', type=click.Choice(['artist', 'album', 'track', 'playlist']))
@click.argument('query')
def search(type: str,
           query: str,
           limit: int = None):

    # FIXME: remove
    # NOTE: cos default is None, argh (or some else) set it as str
    if limit is not None:
        limit = int(limit)

    spotify = get_spotify()
    search = spotify.search(query=query,
                            types=[type],
                            market=None,
                            limit=50)
    paging = search[0]
    print(f'results total: {paging.total}')
    print()

    for count, item in enumerate(spotify.iterate_items_from_paging(paging), start=1):
        printer(item)

        if limit is not None and count >= limit:
            break


# END
