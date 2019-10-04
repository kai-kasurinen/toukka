#

'''player module'''

import argh

from toukka.player.printer.spotify_printer import PlayingPrinter
from toukka.player.watcher.spotify_watcher import Watcher


def playing(with_artist: bool = True,
            with_album: bool = True,
            with_track: bool = True,
            with_track_features: bool = False,
            with_track_features_delivered: bool = False,
            with_track_moods: bool = True,
            with_track_styles: bool = True,
            with_track_key_and_mode: bool = False,
            with_musicbrainz: bool = False,
            with_discogs: bool = False,
            with_wikidata: bool = False):

    '''show information about current user playing track'''
    # pylint: disable=unused-argument, too-many-arguments

    args = locals()
    p = PlayingPrinter(args=args)
    p.print()


def watcher():
    watcher = Watcher()
    watcher.start()

#


NAMESPACE = 'player'

NAMESPACE_KWARGS = {
    'title': 'player',
    'description': 'player, player, player',
    'help': 'help, help, help'
    }

COMMANDS = [
    playing,
    watcher
    ]

# END
