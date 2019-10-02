#

import logging
import gi

gi.require_version('Playerctl', '2.0')
from gi.repository import Playerctl, GLib

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class PlayerCtlManager:
    def __init__(self, watch_only=None):
        self.watch_only = watch_only
        self.player_manager = Playerctl.PlayerManager()
        self.player_manager.connect('name-appeared', self.on_manager_name_appeared)
        self.player_manager.connect('name-vanished', self.on_manager_name_vanished)
        self.player_manager.connect('player-appeared', self.on_manager_player_appeared)
        self.player_manager.connect('player-vanished', self.on_manager_player_vanished)
        self.connect_current_players()

    def connect_current_players(self):
        logger.debug('connect to current players')
        for name in self.player_manager.props.player_names:
            self.init_player(name)

    def on_manager_name_appeared(self, manager, name):
        logger.debug('name appeared: %s, %s', name, name.name)
        self.init_player(name)

    def on_manager_name_vanished(self, manager, name):
        logger.debug('name vanished: %s, %s', name, name.name)

    def on_manager_player_appeared(self, manager, player):
        logger.debug('player appeared: %s, %s', player, player.props.player_name)
        self.player_status(player)

    def on_manager_player_vanished(self, manager, player):
        logger.debug('player vanished: %s, %s', player, player.props.player_name)

    def init_player(self, name):
        logger.debug('init player: %s, %s', name, name.name)

        if self.watch_only is not None and name.name not in self.watch_only:
            logger.debug('player %s is not in %s', name.name, self.watch_only)
            return False

        player = Playerctl.Player.new_from_name(name)
        player.connect('exit', self.on_player_exit)
        player.connect('loop-status', self.on_player_loop_status)
        player.connect('seeked', self.on_player_seeked)
        player.connect('shuffle', self.on_player_shuffle)
        player.connect('volume', self.on_player_volume)
        player.connect('playback-status', self.on_player_playback_status)
        player.connect('metadata', self.on_player_metadata)
        self.player_manager.manage_player(player)

    def on_player_exit(self, player):
        logger.debug('exit: %s', player)

    def on_player_loop_status(self, player, loop_status):
        logger.debug('loop status: %s', loop_status)

    def on_player_seeked(self, player, position):
        logger.debug('seeked: %s', position)

    def on_player_shuffle(self, player, shuffle_status):
        logger.debug('shuffle: %s', shuffle_status)

    def on_player_volume(self, player, volume):
        logger.debug('volume: %s', volume)

    def on_player_metadata(self, player, metadata):
        logger.debug('metadata: %s', metadata)

    def on_player_playback_status(self, player, status):
        logger.debug('status: %s', status)

    def player_status(self, player):
        logger.debug('player %s status: %s', player.props.player_name, player.props.status)
        logger.debug('player %s metadata: %s', player.props.player_name, player.props.metadata)


class MainLoop:
    def __init__(self):
        self.mainloop = GLib.MainLoop()

    def run(self):
        logger.debug('mainloop run')
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            logger.info('Ctrl+C hit, quitting')
            self.exit()

    def exit(self):
        logger.debug('mainloop quit')
        self.mainloop.quit()


# END
