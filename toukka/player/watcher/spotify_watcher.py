#

import logging
import gi

import toukka.logger.to_file

gi.require_version('Playerctl', '2.0')
from gi.repository import GLib, Playerctl
from ..printer.spotify_printer import PlayingPrinter
from .player_watcher import PlayerWatcher

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)





class Watcher:
    def __init__(self):
        self.player = Playerctl.Player(player_name='spotify')
        # spotify only emits metadata and plaback_status signals
        self.player.connect('metadata', self._on_metadata)

        playing_printer_args = {
            'with_artist': True,
            'with_album': True,
            'with_track': True,
            'with_track_features': False,
            'with_track_features_delivered': False,
            'with_track_moods': True,
            'with_track_styles': True,
            'with_track_key_and_mode': False,
            'with_musicbrainz': False,
            'with_discogs': False,
            'with_wikidata': False,
            }
        self.playing_printer = PlayingPrinter(args=playing_printer_args)
        self.last_seen = None
        self.mainloop = GLib.MainLoop()
        #toukka.log.to_file.set_logging_file()

    def start(self):
        self._print_callback()
        self._run()

    def _run(self):
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            logging.info('Ctrl+C hit, quitting')
            self._exit()

    def _exit(self):
        self.mainloop.quit()

    def _on_metadata(self, player, metadata):
        #logger.debug(metadata)
        track_id = metadata['mpris:trackid']

        if track_id == '':
            return

        if track_id == self.last_seen:
            return

        if 'spotify:ad:' in track_id:
            logger.info('advertisement: %s', track_id)
            self.last_seen = track_id
            return
        elif 'spotify:track:' in track_id:
            GLib.timeout_add_seconds(1, self._print_callback)
            self.last_seen = track_id
            return
        else:
            logger.warning('unsupported track id: %s', track_id)
            return


    def _print_callback(self):
        # TODO: skip currently_playing api and use mpris:trackid directly
        self.playing_printer.print()
        print(''.ljust(80, '='))
        # make Glib happy
        return False

#

def watcher():
    watcher = Watcher()
    watcher.start()

COMMANDS = [watcher]

# END
