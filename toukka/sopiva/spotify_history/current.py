#

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql import func
from sqlalchemy.sql import select

from toukka.sopiva.spotify_database.util import get_database_uri_from_config
from toukka.sopiva.spotify_database.database.first import SpotifyTrackISRC
from toukka.sopiva.spotify_mpris_history.database.current import SpotifyMprisHistory

Session = sessionmaker()


class SpotifyHistory:
    def __init__(self):
        database_uri = get_database_uri_from_config()
        self.engine = create_engine(database_uri, echo=False)
        # FIXME: Session should be global or something
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.history = SpotifyMprisHistory
        self.isrcs = SpotifyTrackISRC

    # FIXME: hack?
    def __del__(self):
        self.session.close()

    def count_by_track_id(self, track_id):
        return self.session.query(self.history).filter(self.history.mpris_track_id == track_id).count()

    def count_by_artist_name(self, artist_name):
        return self.session.query(self.history).filter(self.history.xesam_artist == artist_name).count()

    def count_by_track_isrc(self, isrc):
        return self.session.query(self.history).\
            join(self.isrcs, self.history.mpris_track_id == self.isrcs.track_uri).\
            filter(self.isrcs.track_isrc == isrc).count()

    def count_by_artist_name_with_timestamps(self, artist_name):
        # select count(xesam_artist), min(timestamp), max(timestamp)
        #    from spotify_mpris_history where xesam_artist = '?';
        stmt = select(
            func.count(self.history.xesam_artist),
            func.min(self.history.timestamp),
            func.max(self.history.timestamp)).where(self.history.xesam_artist == artist_name)
        result = self.session.execute(stmt).fetchone()
        return result

    def count_by_track_id_with_timestamps(self, track_id):
        # select count(mpris_track_id), min(timestamp), max(timestamp)
        #    from spotify_mpris_history where mpris_track_id = '?';
        stmt = select(
            func.count(self.history.mpris_track_id),
            func.min(self.history.timestamp),
            func.max(self.history.timestamp)).where(self.history.mpris_track_id == track_id)
        result = self.session.execute(stmt).fetchone()
        return result

    def count_by_track_isrc_with_timestamps(self, isrc):
        stmt = select(
            func.count(self.history.mpris_track_id),
            func.min(self.history.timestamp),
            func.max(self.history.timestamp)).\
                join(self.isrcs, self.history.mpris_track_id == self.isrcs.track_uri).\
                where(self.isrcs.track_isrc == isrc)
        result = self.session.execute(stmt).fetchone()
        return result


# END
