#

import pprint
import click

from toukka.sopiva.metabrainz import musicbrainzngs
from toukka.printer.first import printer

from ..cli import cli_root


@cli_root.command()
@click.argument('url')
def browse_url(url):
    printer(musicbrainzngs.browse_urls(resource=url))
