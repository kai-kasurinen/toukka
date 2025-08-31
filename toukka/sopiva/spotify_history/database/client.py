#

import collections


from sqlalchemy import bindparam
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import exists

from sqlalchemy.dialects.postgresql import JSONB

from toukka.sopiva.spotify_database.database import first as database


class SpotifyHistory:
    def __init__(self):
        self.db = database.SpotifyDB()
        self.session = self.db.Session()

    def count_by_track_uri(self, track_uri):
        return self.session.query(func.count(database.SpotifyHistory.id)).filter(database.SpotifyHistory.track_uri == track_uri).scalar()
 
    def count_by_track_id(self, track_id):
        return self.count_by_track_uri(track_id)

    def count_by_artist_name(self, artist_name):
        stmt = select(func.count(database.SpotifyHistory.id)).where(SpotifyHistory.meta.op('@>')(bindparam('value'))).params(value={'artists': [{'name': artist_name}]})
        result = self.session.execute(stmt).scalar()
        return result

    def count_by_artist_uri(self, artist_uri):
        return 0

    def count_by_track_isrc(self, isrc):
        return self.session.query(func.count(database.SpotifyHistory.id)).filter(database.SpotifyHistory.meta['external_ids']['isrc'].as_string() == isrc).scalar()
    
    def count_by_artist_name_with_timestamps(self, artist_name):
        stmt = select(
            func.count(database.SpotifyHistory.track_uri),
            func.min(database.SpotifyHistory.played_at),
            func.max(database.SpotifyHistory.played_at)).where(database.SpotifyHistory.meta.contains({"artists": [{"name": artist_name}]}))
        result = self.session.execute(stmt).fetchone()
        return result

    def count_by_artist_uri_with_timestamps(self, artist_uri):
        stmt = select(
            func.count(database.SpotifyHistory.track_uri),
            func.min(database.SpotifyHistory.played_at),
            func.max(database.SpotifyHistory.played_at)).where(database.SpotifyHistory.meta.contains({"artists": [{"uri": artist_uri}]}))
        result = self.session.execute(stmt).fetchone()
        return result

    def count_by_track_uri_with_timestamps(self, track_uri):
        stmt = select(
            func.count(database.SpotifyHistory.track_uri),
            func.min(database.SpotifyHistory.played_at),
            func.max(database.SpotifyHistory.played_at)).where(database.SpotifyHistory.track_uri == track_uri)
        result = self.session.execute(stmt).fetchone()
        return result

    def count_by_track_id_with_timestamps(self, track_id):
        return self.count_by_track_uri_with_timestamps(track_id)

    def count_by_track_isrc_with_timestamps(self, isrc):
        stmt = select(
            func.count(database.SpotifyHistory.track_uri),
            func.min(database.SpotifyHistory.played_at),
            func.max(database.SpotifyHistory.played_at)).where(database.SpotifyHistory.meta['external_ids']['isrc'].as_string() == isrc)
        result = self.session.execute(stmt).fetchone()
        return result


    def is_track_in_history(self, track_id):
        pass

    def is_track_played(self, track_id):
        # TODO: use is_track_in_history
        if self.count_by_track_id(track_id) > 0:
            return True
        else:
            return False

    def is_tracks_played(self, track_ids):
        return all(self.is_track_played(track_id) for track_id in track_ids)


# END
