#

"""Main, Main, Main, Main"""

import logging
import argh

from .commands import COMMANDS


__program_name__ = 'toukka-spotify-mpris-history'
__program_description__ = '...'


def main():
    '''main, main, main'''
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s')
    parser = argh.ArghParser(prog=__program_name__,
                             description=__program_description__)
    parser.add_argument('--debug',
                        help='print lots of debugging statements',
                        action='store_const',
                        dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.INFO)
    parser.add_commands(COMMANDS)
    args = parser.parse_args()
    logging.getLogger().setLevel(args.loglevel)
    parser.dispatch()

# END
