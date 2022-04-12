#

import logging
import tekore

from .config import lazy_config
from .spotify_watcher import SpotifyWatcher
from .database.current import SpotifyMprisHistory, SpotifyMprisHistoryDB

logger = logging.getLogger(__name__)


class SpotifySaver:
    def __init__(self,
                 dry_run: bool = False,
                 ):
        self.dry_run = dry_run
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
        track_id = self._get_uri_from_trackid(metadata_dict.get('mpris:trackid'))

        # TODO: no need all of this
        if track_id is None:
            return
        elif track_id == '':
            return
        elif track_id == self.last_seen:
            return
        elif track_id == self.last_saved:
            return
        # TODO: move?
        #elif track_id.startswith('spotify:ad:') or track_id.startswith('/com/spotify/ad/'):
        #    logger.debug(f'advertisement, skipping')
        #    return
        else:
            self.last_seen = track_id
            self.saver(metadata_dict)

    def saver(self, metadata):
        # NOTE: metadata is now python dict
        track_id = metadata.get('mpris:trackid')
        logger.debug('saver %s', track_id)

        track_id = self._get_uri_from_trackid(metadata.get('mpris:trackid'))

        # convert metadata to columns
        columns = {
            'mpris_track_id':     track_id,
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
            if self.dry_run:
                logger.warning('not commit, dry_run is %s', self.dry_run)
            else:
                logger.debug('commit track to database')
                session.add(history_entry)
                session.commit()

        self.last_saved = track_id
        logger.debug('saved %s', track_id)

    def _convert_new_trackid_to_uri(self, trackid):
        empty_, com_, spotify_, type_, id_ = trackid.split('/')
        uri = 'spotify:' + type_ + ':' + id_
        return uri

    def _get_uri_from_trackid(self, track_id):

        if track_id.startswith('/com/spotify'):
            track_id_new = self._convert_new_trackid_to_uri(track_id)
            logger.debug(f'converted track_id {track_id} to {track_id_new}')
            track_id = track_id_new

        if not track_id.startswith('spotify:'):
            logger.error(f'unsupported track_id: {track_id}')
            raise Exception()

        return track_id



# END
