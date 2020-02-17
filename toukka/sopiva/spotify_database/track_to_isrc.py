#

import logging

import sqlalchemy.sql

import toukka.config

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_mpris_history.database.current import SpotifyMprisHistory
from toukka.sopiva.spotify_database.database.first import SpotifyDB, SpotifyTrackISRC
from toukka.sopiva.spotify_database.util import get_database_uri_from_config

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def update():
    spotify = get_spotify()

    database_uri = get_database_uri_from_config()
    logger.debug(database_uri)
    db = SpotifyDB(database_uri)
    db._create()

    with db.session_scope() as session:
        query = session.query(SpotifyMprisHistory.mpris_track_id).\
            join(SpotifyTrackISRC,
                 SpotifyMprisHistory.mpris_track_id == SpotifyTrackISRC.track_uri,
                 isouter=True).\
            filter(SpotifyMprisHistory.mpris_track_id.like('spotify:track:%')).\
            filter(SpotifyTrackISRC.track_uri.is_(None)).\
            distinct().all()

    logger.debug('%s mpris_track_ids without isrc', len(query))

    for track_uri, in query:
        logger.debug('%s', track_uri)

        track_uri_type, track_uri_id = spotify.convert.from_uri(track_uri)

        track = spotify.track(track_uri_id, market=None)
        isrc = track.external_ids.get('isrc')

        track_to_isrc_entry = SpotifyTrackISRC(track_uri=track_uri, track_isrc=isrc)
        with db.session_scope() as session:
            session.add(track_to_isrc_entry)
            session.commit()

# END
