#

from contextlib import contextmanager

from sqlalchemy import Column, DateTime, Float, Integer, Text, text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()
metadata = Base.metadata


class SpotifyMprisHistory(Base):
    __tablename__ = 'spotify_mpris_history'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime,
                       nullable=False,
                       server_default=func.now(),
                       index=True)
    mpris_track_id = Column(Text, index=True)
    mpris_length = Column(BigInteger)
    xesam_album = Column(Text, index=True)
    xesam_album_artist = Column(Text)
    xesam_artist = Column(Text, index=True)
    xesam_auto_rating = Column(Float)
    xesam_disc_number = Column(Integer)
    xesam_title = Column(Text, index=True)
    xesam_track_number = Column(Integer)
    xesam_url = Column(Text)
    mpris_art_url = Column(Text)


class SpotifyMprisHistoryDB:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri, echo=False, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def last_saved_mpris_track_id(self):
        # FIXME: update to orm
        last = self.engine.execute('''SELECT mpris_track_id
                        FROM spotify_mpris_history
                        ORDER BY id
                        DESC LIMIT 1''').fetchone()
        if last is None:
            return None
        return last[0]


# END
