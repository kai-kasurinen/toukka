#

import logging
import gi

gi.require_version('Playerctl', '1.0')
from gi.repository import GLib, Playerctl

from .playing import PlayingPrinter


def playing_watcher():
    watcher = Watcher()
    GLib.MainLoop().run()


class Watcher:
    def __init__(self):
        self.player = Playerctl.Player(player_name='spotify')
        self.player.on('metadata', self.on_metadata)

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

    def on_metadata(self, player, metadata):
        #logging.debug(metadata)
        track_id = metadata['mpris:trackid']

        if track_id == '':
            return
        elif track_id == self.last_seen:
            return
        elif 'spotify:ad:' in track_id:
            return
        else:
            self.playing_printer.print()

        self.last_seen = track_id


#

COMMANDS = [playing_watcher]

# END
