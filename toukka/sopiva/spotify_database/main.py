#

'''main, main, main'''

import logging
import argh

import toukka.logger.simple
import toukka.config
import toukka.version

from . import commands


__program_name__ = 'toukka-spotify-database'
__program_description__ = 'manage database'


def main():
    '''main, main, main'''
    toukka.logger.simple.init_logging()

    parser = argh.ArghParser(prog=__program_name__, description=__program_description__)
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=toukka.version.__version__))
    parser.add_argument('--debug',
                        help='Print lots of debugging statements',
                        action='store_const',
                        dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.INFO)
    # parser.add_commands(toukka.config.COMMANDS)
    parser.add_commands(commands.COMMANDS)
    args = parser.parse_args()

    toukka.config.lazy_config.set_args(args)
    toukka.logger.simple.set_logging_level(args.loglevel)

    parser.dispatch()


# END
