#

"""Main, Main, Main, Main"""

import argh
import logging

import sopiva.logger
import sopiva.config
import sopiva.spotify_watcher.commands
import sopiva.version

__program_name__ = 'sopiva-spotify-watcher'
__program_description__ = 'spotify watcher'

def main():
    """main, main, main, main"""
    sopiva.logger.init_logging()

    parser = argh.ArghParser(prog=__program_name__, description=__program_description__)
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=sopiva.version.__version__))
    parser.add_argument('--debug',
                        help='Print lots of debugging statements',
                        action='store_const',
                        dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.INFO)
    parser.add_commands(sopiva.config.COMMANDS)
    parser.add_commands(sopiva.spotify_watcher.commands.COMMANDS)
    # HACK
    parser.set_default_command(sopiva.spotify_watcher.commands.COMMANDS[0])
    args = parser.parse_args()

    sopiva.config.lazy_config.set_args(args)
    sopiva.logger.set_logging_level(args.loglevel)

    parser.dispatch()


# END
