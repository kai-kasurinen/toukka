#

import logging
import gi

gi.require_version('Playerctl', '1.0')
from gi.repository import GLib, Playerctl

from .playing import PlayingPrinter


def playing_watcher():
    watcher = Watcher()
    watcher.start()


class Watcher:
    def __init__(self):
        self.player = Playerctl.Player(player_name='spotify')
        self.player.on('metadata', self._on_metadata)

        playing_printer_args = {
            'with_artist': True,
            'with_album': True,
            'with_track': True,
            'with_track_features': False,
            'with_track_features_delivered': False,
            'with_track_moods': True,
            'with_track_styles': True,
            'with_track_key_and_mode': False,
            'with_musicbrainz': True}
        self.playing_printer = PlayingPrinter(args=playing_printer_args)
        self.last_seen = None
        
        self.mainloop = GLib.MainLoop()

    def start(self):
        self._print_callback()
        self._run()

    def _run(self):
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            print("How rude!")

    def _on_metadata(self, player, metadata):
        logging.debug(metadata)
        track_id = metadata['mpris:trackid']

        if track_id == '':
            return
        elif track_id == self.last_seen:
            return
        elif 'spotify:ad:' in track_id:
            return
        else:
            GLib.timeout_add_seconds(1, self._print_callback)

        self.last_seen = track_id

    def _print_callback(self):
        self.playing_printer.print()
        print(''.ljust(80, '='))
        # make Glib happy
        return False

#

COMMANDS = [playing_watcher]

# END
