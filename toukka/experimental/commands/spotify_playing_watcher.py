#

import logging
import gi

import toukka.log.to_file

gi.require_version('Playerctl', '2.0')
from gi.repository import GLib, Playerctl
from .spotify_playing import PlayingPrinter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def playing_watcher():
    watcher = Watcher()
    watcher.start()


class Watcher:
    def __init__(self):
        self.player = Playerctl.Player(player_name='spotify')
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
            'with_musicbrainz': True,
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
        elif track_id == self.last_seen:
            return
        elif 'spotify:ad:' in track_id:
            return
        elif 'spotify:track:' in track_id:
            GLib.timeout_add_seconds(1, self._print_callback)
        else:
            return

        self.last_seen = track_id

    def _print_callback(self):
        # TODO: skip currently_playing api and use mpris:trackid directly
        self.playing_printer.print()
        print(''.ljust(80, '='))
        # make Glib happy
        return False

#

COMMANDS = [playing_watcher]

# END
