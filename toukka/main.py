#

"""Main, Main, Main, Main"""

import logging
import argh

import toukka.spotify.commands
import toukka.musicbrainz.commands
import toukka.discogs.commands
import toukka.pandas.commands
import toukka.toukka.commands

__prog_name__ = 'spotify-toukka'
__version__ = '0.0.0'


def main():
    """main, main, main, main"""
    logging.basicConfig(
        level=logging.INFO,
        #format='%(name)s %(levelname)s %(message)s'
        format='%(asctime)s %(name)s %(levelname)s %(message)s')
    logging.captureWarnings(True)

    parser = argh.ArghParser()

    parser.add_argument('--debug',
                        help='Print lots of debugging statements',
                        action='store_const',
                        dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.INFO)

    parser.add_commands(toukka.spotify.commands.COMMANDS,
                        namespace=toukka.spotify.commands.NAMESPACE,
                        namespace_kwargs=toukka.spotify.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.musicbrainz.commands.COMMANDS,
                        namespace=toukka.musicbrainz.commands.NAMESPACE,
                        namespace_kwargs=toukka.musicbrainz.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.discogs.commands.COMMANDS,
                        namespace=toukka.discogs.commands.NAMESPACE,
                        namespace_kwargs=toukka.discogs.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.toukka.commands.COMMANDS,
                        namespace=toukka.toukka.commands.NAMESPACE,
                        namespace_kwargs=toukka.toukka.commands.NAMESPACE_KWARGS)

    args = parser.parse_args()

    logging.getLogger().setLevel(args.loglevel)
    logging.debug('%s %s', __prog_name__, __version__)

    parser.dispatch()

# END
