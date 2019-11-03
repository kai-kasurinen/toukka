#

import click
import click_log

import toukka.version


@click.group()
@click.version_option(version=toukka.version.__version__)
@click_log.simple_verbosity_option(None, '--loglevel')
def cli_root():
    pass

