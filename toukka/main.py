#

"""Main, Main, Main, Main"""

import logging
import argh

import toukka.commands.spotify
import toukka.commands.musicbrainz
import toukka.commands.discogs
import toukka.commands.pandas
import toukka.commands.toukka

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

    parser.add_commands(toukka.commands.spotify.COMMANDS,
                        namespace=toukka.commands.spotify.NAMESPACE,
                        namespace_kwargs=toukka.commands.spotify.NAMESPACE_KWARGS)

    parser.add_commands(toukka.commands.musicbrainz.COMMANDS,
                        namespace=toukka.commands.musicbrainz.NAMESPACE,
                        namespace_kwargs=toukka.commands.musicbrainz.NAMESPACE_KWARGS)

    parser.add_commands(toukka.commands.discogs.COMMANDS,
                        namespace=toukka.commands.discogs.NAMESPACE,
                        namespace_kwargs=toukka.commands.discogs.NAMESPACE_KWARGS)

    parser.add_commands(toukka.commands.toukka.COMMANDS,
                        namespace=toukka.commands.toukka.NAMESPACE,
                        namespace_kwargs=toukka.commands.toukka.NAMESPACE_KWARGS)

    args = parser.parse_args()

    logging.getLogger().setLevel(args.loglevel)
    logging.debug('%s %s', __prog_name__, __version__)

    parser.dispatch()

# END
