#

'''main, main, main'''

import logging
import click_log
import toukka.logger.simple
import toukka.sopiva.spotify.cli
import toukka.sopiva.spotify.commands


def main():
    toukka.logger.simple.init_logging()
    # FIXME: format?
    click_log.basic_config()
    toukka.sopiva.spotify.cli.cli_root.main()


# END
