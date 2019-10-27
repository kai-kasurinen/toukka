#

import logging

from gi.repository import GLib, GObject
from .playerctl_manager import PlayerCtlManager


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


# FIXME: fuck you

class SpotifyWatcher(PlayerCtlManager, GObject.GObject):

    __gsignals__ = {
        'track_played_enough': (GObject.SIGNAL_RUN_FIRST, None, (GLib.Variant,))
        }

    def __init__(self):
        GObject.GObject.__init__(self)
        self.last_seen = None
        self.last_ok = None
        self.check_player_timeout_source = None
        super().__init__(watch_only=['spotify'])

    def check_player_timeout_remove(self):
        if self.check_player_timeout_source is None:
            logger.debug('check player timeout source is None?')
        elif GLib.source_remove(self.check_player_timeout_source):
            self.check_player_timeout_source = None
            logger.debug('check player timeout source removed')
        else:
            logger.debug('check player timeout source not removed')

    def check_player_timeout_add(self):
        if self.check_player_timeout_source is not None:
            logger.debug('check player timeout already added')
        else:
            # NOTE: 10 seconds delay for checking
            self.check_player_timeout_source = GLib.timeout_add_seconds(10, self.check_player)
            logger.debug('check player timeout added')

    def on_manager_player_appeared(self, manager, player):
        super().on_manager_player_appeared(manager, player)
        self.player = player
        self.check_track_changed(player, player.props.metadata)

    def on_manager_player_vanished(self, manager, player):
        super().on_manager_player_vanished(manager, player)
        self.player = None
        self.check_player_timeout_source = None

    def on_player_metadata(self, player, metadata):
        super().on_player_metadata(player, metadata)
        self.check_track_changed(player, metadata)

    def on_player_playback_status(self, player, status):
        super().on_player_playback_status(player, status)
        self.check_playback_status(player)

    def check_playback_status(self, player):
        status = player.props.status
        logger.debug('check playback status: %s', status)
        if status == 'Playing':
            self.check_player_timeout_add()
        else:
            self.check_player_timeout_remove()

    def check_track_changed(self, player, metadata):
        track_id = metadata['mpris:trackid']
        if track_id == '':
            return
        elif track_id == self.last_seen:
            return
        else:
            self.last_seen = track_id
            self.on_track_changed(player, metadata)

    def on_track_changed(self, player, metadata):
        logger.debug('on track changed: %s', metadata['mpris:trackid'])
        # self.check_player_timeout_add(player)
        self.check_playback_status(player)

    def check_player(self):

        # hopefully this fixes crash
        if self.player is None:
            logger.debug('player disappeared? removing check')
            self.check_player_timeout_source = None
            return False

        # when not playing, stop watching
        if self.player.props.status != 'Playing':
            logger.debug('player not playing? removing check')
            self.check_player_timeout_source = None
            return False

        metadata = self.player.props.metadata
        track_id = metadata['mpris:trackid']

        # we already send it
        if track_id == self.last_ok:
            logger.debug('track_id is same as last_ok. removing check')
            self.check_player_timeout_source = None
            return False

        # NOTE: position in the current track of the player in microseconds
        position = self.player.props.position
        # NOTE: defaults to 30 seconds
        position_wanted = 30000000

        track_length = metadata['mpris:length']
        # logger.debug('track length: %i', track_length)

        # NOTE: if length is defined, new position wanted is half of length
        if track_length > 0:
            position_wanted = track_length/2

        logger.debug('position is %i, position wanted is %i', position, position_wanted)

        if position <= position_wanted:
            logger.debug('track position not ok')
            # return True, so we keep going
            return True
        else:
            logger.debug('track position is ok')
            self.emit('track_played_enough', metadata)
            self.check_player_timeout_source = None
            return False

    def do_track_played_enough(self, metadata):
        # logger.debug('do_track_played_enough: %s', metadata)
        track_id = metadata['mpris:trackid']
        self.last_ok = track_id


# END
