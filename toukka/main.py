#

"""Main, Main, Main, Main"""

import logging
import argh

import toukka.commands.spotify.me
import toukka.commands.spotify.pandas
import toukka.commands.spotify.playlist
import toukka.commands.spotify.fun

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

    parser.add_commands(toukka.commands.spotify.me.COMMANDS,
                        namespace='me',
                        title='Current user related commands')

    parser.add_commands(toukka.commands.spotify.playlist.COMMANDS,
                        namespace='playlist',
                        title='Playlist related commands')

    parser.add_commands(toukka.commands.spotify.pandas.COMMANDS,
                        namespace='pandas',
                        title='Pandas related commands')

    parser.add_commands(toukka.commands.spotify.fun.COMMANDS,
                        namespace='fun',
                        title='just for fun')

    args = parser.parse_args()

    logging.getLogger().setLevel(args.loglevel)
    logging.debug('%s %s', __prog_name__, __version__)

    parser.dispatch()

# END
