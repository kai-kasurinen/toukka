#

import logging

from .playerctl_manager import PlayerCtlManager, MainLoop, GLib
from .spotify_printer import SpotifyPrinter

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class SpotifyWatcher(PlayerCtlManager):
    def __init__(self):
        self.spotify_printer = SpotifyPrinter()
        self.last_seen = None
        super().__init__(watch_only='spotify')

    def on_player_metadata(self, player, metadata):
        #super().on_player_metadata(player, metadata)
        self.on_spotify_metadata(player, metadata)

    def on_manager_player_appeared(self, manager, player):
        #super().on_manager_player_appeared(manager, player)
        self.on_spotify_metadata(player, player.props.metadata)

    def on_spotify_metadata(self, player, metadata):
        track_id = metadata['mpris:trackid']

        if track_id == '':
            return

        if track_id == self.last_seen:
            return

        if 'spotify:ad:' in track_id:
            logger.debug('advertisement: %s', track_id)
            self.last_seen = track_id
            return
        elif 'spotify:track:' in track_id:
            GLib.timeout_add_seconds(1, self._print_spotify_metadata_callback)
            self.last_seen = track_id
            return
        else:
            logger.debug('unsupported track id: %s', track_id)
            return

    def _print_spotify_metadata_callback(self):
        self.print_spotify_metadata()
        # make Glib happy
        return False

    def print_spotify_metadata(self):
        print(''.ljust(80, '='))
        self.spotify_printer.print_all_from_track(self.last_seen)
        print(''.ljust(80, '='))


#

def run():
    spotifywatcher = SpotifyWatcher()
    mainloop = MainLoop()
    mainloop.run()


# END
