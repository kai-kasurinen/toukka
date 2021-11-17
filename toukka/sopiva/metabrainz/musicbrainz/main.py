#

'''main, main, main'''

import logging
import click_logging
import toukka.logger.simple
import toukka.sopiva.metabrainz.musicbrainz.cli
import toukka.sopiva.metabrainz.musicbrainz.commands


def main():
    toukka.logger.simple.init_logging()
    # FIXME: format?
    #click_logging.basic_config()
    toukka.sopiva.metabrainz.musicbrainz.cli.cli_root.main()


# END
