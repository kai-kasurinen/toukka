#

import logging
import datetime

from toukka.printer import printer

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
        super().on_player_metadata(player, metadata)
        self.on_spotify_metadata(player, metadata)

    def on_manager_player_appeared(self, manager, player):
        super().on_manager_player_appeared(manager, player)
        self.on_spotify_metadata(player, player.props.metadata)

    def on_spotify_metadata(self, player, metadata):
        track_id = self._get_uri_from_trackid(metadata['mpris:trackid'])

        if track_id == '':
            return

        if track_id == self.last_seen:
            return

        #
        self.print_metadata(metadata)

        if track_id.startswith('spotify:ad:'):
            #logger.info('advertisement: %s', track_id)
            self.last_seen = track_id
            return
        elif track_id.startswith('spotify:track:'):
            GLib.timeout_add_seconds(1, self._print_spotify_metadata_callback)
            self.last_seen = track_id
            return
        elif track_id.startswith('spotify:episode:'):
            GLib.timeout_add_seconds(1, self._print_spotify_metadata_callback)
            self.last_seen = track_id
            return
        else:
            logger.debug('unsupported trackid: %s', track_id)
            return

    def print_metadata(self, metadata):
        print('track: %s (%s) (%f)' %
              (metadata['xesam:title'],
               metadata['mpris:trackid'],
               metadata['xesam:autoRating'])),
        print('\tartists: %s, %s' %
              (metadata['xesam:artist'], metadata['xesam:albumArtist']))
        print('\talbum: %s' %
              (metadata['xesam:album']))
        # print('\turl: %s' % (metadata['xesam:url']))
        print('\tlength: %s' %
              (datetime.timedelta(microseconds=metadata['mpris:length'])))

    def _print_spotify_metadata_callback(self):
        self.print_spotify_metadata()
        # make Glib happy
        return False

    def _get_uri_from_trackid(self, track_id):

        if track_id.startswith('/com/spotify'):
            track_id_new = self._convert_new_trackid_to_uri(track_id)
            logger.debug(f'converted track_id {track_id} to {track_id_new}')
            track_id = track_id_new

        if not track_id.startswith('spotify:'):
            logger.error(f'unsupported track_id: {track_id}')
            raise Exception()

        return track_id

    def _convert_new_trackid_to_uri(self, trackid):
        empty_, com_, spotify_, type_, id_ = trackid.split('/')
        uri = 'spotify:' + type_ + ':' + id_
        return uri

    def print_spotify_metadata(self):

        if self.last_seen.startswith('spotify:'):
            uri = self.last_seen
        elif self.last_seen.startswith('/com/spotify'):
            uri = self._convert_new_trackid_to_uri(self.last_seen)
        else:
            raise Exception()

        self.spotify_printer.print_all_from_uri(uri)


#

def run():
    spotifywatcher = SpotifyWatcher()
    mainloop = MainLoop()
    mainloop.run()


# END
