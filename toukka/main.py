#

"""Main, Main, Main, Main"""

import logging
import argh

import toukka
import toukka.spotify.commands
import toukka.musicbrainzngs.commands
import toukka.discogs.commands
import toukka.pandas.commands
import toukka.experimental.commands
import toukka.finna.commands
import toukka.wikidata.commands
import toukka.metabrainz.listenbrainz.commands
import toukka.metabrainz.acousticbrainz.commands
import toukka.metabrainz.musicbrainz.commands

def main():
    """main, main, main, main"""
    logging.basicConfig(
        level=logging.INFO,
        #format='%(name)s %(levelname)s %(message)s'
        format='%(asctime)s %(name)s %(levelname)s %(message)s')
    logging.captureWarnings(True)

    parser = argh.ArghParser(prog='toukka')

    parser.add_argument('--debug',
                        help='Print lots of debugging statements',
                        action='store_const',
                        dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.INFO)

    parser.add_commands(toukka.spotify.commands.COMMANDS,
                        namespace=toukka.spotify.commands.NAMESPACE,
                        namespace_kwargs=toukka.spotify.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.musicbrainzngs.commands.COMMANDS,
                        namespace=toukka.musicbrainzngs.commands.NAMESPACE,
                        namespace_kwargs=toukka.musicbrainzngs.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.metabrainz.musicbrainz.commands.COMMANDS,
                        namespace=toukka.metabrainz.musicbrainz.commands.NAMESPACE,
                        namespace_kwargs=toukka.metabrainz.musicbrainz.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.metabrainz.acousticbrainz.commands.COMMANDS,
                        namespace=toukka.metabrainz.acousticbrainz.commands.NAMESPACE,
                        namespace_kwargs=toukka.metabrainz.acousticbrainz.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.metabrainz.listenbrainz.commands.COMMANDS,
                        namespace=toukka.metabrainz.listenbrainz.commands.NAMESPACE,
                        namespace_kwargs=toukka.metabrainz.listenbrainz.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.finna.commands.COMMANDS,
                        namespace=toukka.finna.commands.NAMESPACE,
                        namespace_kwargs=toukka.finna.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.discogs.commands.COMMANDS,
                        namespace=toukka.discogs.commands.NAMESPACE,
                        namespace_kwargs=toukka.discogs.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.wikidata.commands.COMMANDS,
                        namespace=toukka.wikidata.commands.NAMESPACE,
                        namespace_kwargs=toukka.wikidata.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.experimental.commands.COMMANDS,
                        namespace=toukka.experimental.commands.NAMESPACE,
                        namespace_kwargs=toukka.experimental.commands.NAMESPACE_KWARGS)

    args = parser.parse_args()

    logging.getLogger().setLevel(args.loglevel)
    logging.debug('%s %s', toukka.__prog_name__, toukka.__version__)

    parser.dispatch()

# END
