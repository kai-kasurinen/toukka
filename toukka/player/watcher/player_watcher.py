#

import logging
import gi
gi.require_version('Playerctl', '2.0')
from gi.repository import Playerctl, GLib

logger = logging.getLogger(__name__)


class PlayerWatcher:
    def __init__(self, player_name=None):
        # FIXME: check dbus
        self.player = Playerctl.Player(player_name=player_name)
        self.player.connect('exit', self.on_exit)
        self.player.connect('loop-status', self.on_loop_status)
        self.player.connect('seeked', self.on_seeked)
        self.player.connect('shuffle', self.on_shuffle)
        self.player.connect('volume', self.on_volume)
        self.player.connect('playback-status', self.on_playback_status)
        self.player.connect('metadata', self.on_metadata)
        self.mainloop = GLib.MainLoop()

    def run(self):
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            logger.info('Ctrl+C hit, quitting')
            self.exit()

    def exit(self):
        self.mainloop.quit()

    def on_exit(self, player):
        logger.debug('exit: %s', player)

    def on_loop_status(self, player, loop_status):
        logger.debug('loop status: %s', loop_status)

    def on_seeked(self, player, position):
        logger.debug('seeked: %s', position)

    def on_shuffle(self, player, shuffle_status):
        logger.debug('shuffle: %s', shuffle_status)

    def on_volume(self, player, volume):
        logger.debug('volume: %s', volume)

    def on_metadata(self, player, metadata):
        logger.debug('metadata: %s', metadata)

    def on_playback_status(self, player, status):
        logger.debug('status: %s', status)


# END
