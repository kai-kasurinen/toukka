#

import logging

from .config import lazy_config
from .spotify_watcher import SpotifyWatcher
from .database.current import SpotifyMprisHistory, SpotifyMprisHistoryDB

logger = logging.getLogger(__name__)


class SpotifySaver:
    def __init__(self):
        self.last_seen = None
        database_uri = lazy_config['database_uri'].get()
        logger.debug('database_uri is %s', database_uri)
        self.db = SpotifyMprisHistoryDB(database_uri)
        self.last_saved = self.db.last_saved_mpris_track_id()
        logger.debug('last saved is %s', self.last_saved)

        self.watcher = SpotifyWatcher()
        self.watcher.connect('track_played_enough', self.on_track_played_enough)

    # TODO: why this obj?
    def on_track_played_enough(self, obj, metadata):
        # NOTE: metadata is gi.overrides.GLib.Variant
        metadata_dict = metadata.unpack()
        track_id = metadata_dict.get('mpris:trackid')

        # TODO: no need all of this
        if track_id is None:
            return
        elif track_id == '':
            return
        elif track_id == self.last_seen:
            return
        elif track_id == self.last_saved:
            return
        #
        #elif 'spotify:ad:' in track_id:
        #    return
        #
        else:
            self.last_seen = track_id
            self.saver(metadata_dict)

    def saver(self, metadata):
        # NOTE: metadata is now python dict
        track_id = metadata.get('mpris:trackid')

        # convert metadata to columns
        columns = {
            'mpris_track_id':     metadata.get('mpris:trackid'),
            'mpris_length':       metadata.get('mpris:length'),
            'mpris_art_url':      metadata.get('mpris:artUrl'),
            'xesam_album':        metadata.get('xesam:album'),
            'xesam_album_artist': metadata.get('xesam:albumArtist')[0],
            'xesam_artist':       metadata.get('xesam:artist')[0],
            'xesam_auto_rating':  metadata.get('xesam:autoRating'),
            'xesam_disc_number':  metadata.get('xesam:discNumber'),
            'xesam_title':        metadata.get('xesam:title'),
            'xesam_track_number': metadata.get('xesam:trackNumber'),
            'xesam_url':          metadata.get('xesam:url')
            }

        history_entry = SpotifyMprisHistory(**columns)
        # session_scope handles commit, rollback, close session
        with self.db.session_scope() as session:
            session.add(history_entry)
            session.commit()

        self.last_saved = track_id
        logger.debug('saved %s', track_id)


# END
