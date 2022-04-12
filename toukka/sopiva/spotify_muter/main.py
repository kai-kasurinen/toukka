#!/usr/bin/env python3
#
# https://github.com/serialoverflow/blockify/issues/100


import sys
import logging
import argh
import gi
import pulsectl

gi.require_version('Playerctl', '2.0')
from gi.repository import Playerctl, GLib


__prog_name__ = 'spotify-muter'
__version__ = '0.0.0'


class Muter:

    def __init__(self):
        player_name = 'spotify'
        #self.player = Playerctl.Player.new_for_source(player_name=player_name, source=Playerctl.Source.DBUS_SESSION)
        self.player = Playerctl.Player(player_name=player_name)
        self.player.connect('metadata', self.on_metadata)
        self.pulse = pulsectl.Pulse()
        self.last_mode = False
        self.last_seen = None
        self.last_sinks_count = len(self.get_spotify_sinks())

    def on_metadata(self, player, metadata):
        logging.debug(metadata)
        track_id = metadata['mpris:trackid']

        if track_id == '':
            return
        elif track_id == self.last_seen:
            self.check_spotify_sinks()
        elif 'spotify:ad:' in track_id or '/com/spotify/ad/' in track_id:
            if self.last_mode is False:
                self.mute()
        else:
            if self.last_mode is True:
                self.unmute_delayed()

        self.last_seen = track_id

    def mute(self):
        logging.debug('muting')
        self.mute_spotify_sinks(True)

    def unmute(self):
        logging.debug('unmuting')
        self.mute_spotify_sinks(False)

    def unmute_delayed(self, seconds=2):
        logging.debug('add delayed unmuting')
        GLib.timeout_add_seconds(seconds, self.mute_callback, False)

    def mute_callback(self, mode):
        logging.debug('mute callback')
        self.mute_spotify_sinks(mode)
        return False

    def mute_spotify_sinks(self, mode):
        if self.last_mode is mode:
            logging.debug('mute mode is already %s, but continue anyway', mode)
        sinks = self.get_spotify_sinks()
        for sink in sinks:
            self.mute_sink(sink, mode)
        self.last_mode = mode
        self.last_sinks_count = len(sinks)

    def check_spotify_sinks(self):
        sinks = self.get_spotify_sinks()
        sinks_count = len(sinks)
        if sinks_count != self.last_sinks_count:
            logging.debug('sinks count mismatch (%s != %s), forcing mute mode',
                          sinks_count, self.last_sinks_count)
            self.mute_spotify_sinks(self.last_mode)

    def get_spotify_sinks(self):
        sinks = self.pulse.sink_input_list()
        #sinks_spotify = [s for s in sinks if s.name == 'Spotify']
        sinks_spotify = [s for s in sinks if s.proplist.get('application.process.binary') == 'spotify']
        return sinks_spotify

    def mute_sink(self, sink, mode):
        if mode not in (True, False):
            logging.warning('BUG: mute mode is not True or False.')
            return
        if sink.mute != mode:
            logging.debug('set mute mode (%s) to sink (%s)', mode, sink)
            self.pulse.mute(sink, mode)
        else:
            logging.debug('already mute mode (%s) on sink (%s)', mode, sink)



def loop():
    muter = Muter()
    GLib.MainLoop().run()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s')

    parser = argh.ArghParser()

    parser.add_argument('--debug',
                        help='Print lots of debugging statements',
                        action='store_const',
                        dest='loglevel',
                        const=logging.DEBUG,
                        default=logging.INFO)

    parser.add_commands([loop])

    args = parser.parse_args()

    logging.getLogger().setLevel(args.loglevel)

    parser.dispatch()


if __name__ == "__main__":
    sys.exit(main())

# END
