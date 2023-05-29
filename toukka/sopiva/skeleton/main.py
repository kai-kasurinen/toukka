#

'''main, main, main'''

import logging
import click_logging
import toukka.logger.simple

from . import cli
from . import commands


def main():
    toukka.logger.simple.init_logging()
    cli.root.main()


# END
