#

"""Main, Main, Main, Main"""

import logging
import argh

import toukka
import toukka.logger.simple
import toukka.config

#import toukka.sopiva.spotify.commands
#import toukka.sopiva.discogs.commands
#import toukka.sopiva.experimental.commands
#import toukka.sopiva.finna.commands
#import toukka.sopiva.wikidata.commands
#import toukka.sopiva.itunes.commands
#import toukka.sopiva.player.commands

__program_name__ = 'toukka'
__program_description__ = 'toukka multifunctional tool'

def main():
    """main, main, main, main"""

    toukka.logger.simple.init_logging()

    parser = argh.ArghParser(prog='toukka')

    parser.add_argument('--debug',
                        help='Print lots of debugging statements',
                        action='store_const',
                        dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.INFO)
    '''
    parser.add_commands(toukka.spotify.commands.COMMANDS,
                        namespace=toukka.spotify.commands.NAMESPACE,
                        namespace_kwargs=toukka.spotify.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.finna.commands.COMMANDS,
                        namespace=toukka.finna.commands.NAMESPACE,
                        namespace_kwargs=toukka.finna.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.discogs.commands.COMMANDS,
                        namespace=toukka.discogs.commands.NAMESPACE,
                        namespace_kwargs=toukka.discogs.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.wikidata.commands.COMMANDS,
                        namespace=toukka.wikidata.commands.NAMESPACE,
                        namespace_kwargs=toukka.wikidata.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.itunes.commands.COMMANDS,
                        namespace=toukka.itunes.commands.NAMESPACE,
                        namespace_kwargs=toukka.itunes.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.experimental.commands.COMMANDS,
                        namespace=toukka.experimental.commands.NAMESPACE,
                        namespace_kwargs=toukka.experimental.commands.NAMESPACE_KWARGS)

    parser.add_commands(toukka.player.commands.COMMANDS,
                        namespace=toukka.player.commands.NAMESPACE,
                        namespace_kwargs=toukka.player.commands.NAMESPACE_KWARGS)
    '''
    args = parser.parse_args()

    toukka.config.lazy_config.set_args(args)
    toukka.logger.simple.set_logging_level(args.loglevel)

    parser.dispatch()

# END
