#


import click_logging
import toukka.logger.simple
import toukka.config
import toukka.version

import toukka.sopiva.spotify_manager.commands
import toukka.sopiva.spotify_manager.cli


def main():
    toukka.logger.simple.init_logging()
    # click_logging.basic_config()
    toukka.sopiva.spotify_manager.cli.cli_root.main()


# END
