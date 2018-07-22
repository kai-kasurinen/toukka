#

"""Main, Main, Main, Main"""

import logging
import argh

import toukka.commands.me
import toukka.commands.pandas
import toukka.commands.playlist

__prog_name__ = 'spotify-toukka'
__version__ = '0.0.0'


def main():
    """main, main, main, main"""
    logging.basicConfig(level=logging.INFO,
                        format='%(name)s %(levelname)s %(message)s')

    parser = argh.ArghParser()

    parser.add_argument('--debug',
                        help='Print lots of debugging statements',
                        action='store_const',
                        dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.INFO)

    parser.add_commands(toukka.commands.me.COMMANDS,
                        namespace='me',
                        title='Current user related commands')

    parser.add_commands(toukka.commands.playlist.COMMANDS,
                        namespace='playlist',
                        title='Playlist related commands')

    parser.add_commands(toukka.commands.pandas.COMMANDS,
                        namespace='pandas',
                        title='Pandas related commands')

    args = parser.parse_args()

    logging.getLogger().setLevel(args.loglevel)
    logging.debug('%s %s', __prog_name__, __version__)

    parser.dispatch()

# END
