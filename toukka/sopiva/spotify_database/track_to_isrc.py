#

import logging

import sqlalchemy.sql

import spotipy.convert
import toukka.config

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_mpris_history.database.current import SpotifyMprisHistory
from .database.first import SpotifyDB, SpotifyTrackISRC
from .util import get_database_uri_from_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def update():
    spotify = get_spotify()

    database_uri = get_database_uri_from_config()
    logger.debug(database_uri)
    db = SpotifyDB(database_uri)
    db._create()

    # all unique mpris_track_ids not in spotify_track_isrc using subquery
    track_isrc_query = db.session.query(SpotifyTrackISRC.track_uri)
    history_query = db.session.query(SpotifyMprisHistory.mpris_track_id).\
        filter(SpotifyMprisHistory.mpris_track_id.like('spotify:track:%')).\
        filter(SpotifyMprisHistory.mpris_track_id.notin_(track_isrc_query)).\
        distinct().all()

    logger.debug('%s mpris_track_ids without isrc', len(history_query))

    for track_uri, in history_query:
        logger.debug(f'{track_uri}')

        # FIXME: remove, not needed
        # 'cos convert.from_uri does not handle podcasts and other
        if 'spotify:track:' not in track_uri:
            logger.debug(f'{track_uri}: unsupported type')
            continue

        track_uri_type, track_uri_id = spotipy.convert.from_uri(track_uri)

        track = spotify.track(track_uri_id, market=None)
        isrc = track.external_ids.get('isrc')

        track_to_isrc_entry = SpotifyTrackISRC(track_uri=track_uri, track_isrc=isrc)
        db.session.add(track_to_isrc_entry)
        db.session.commit()

# END
