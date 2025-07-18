#

from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func


Base = declarative_base()
metadata = Base.metadata


class SpotifyTrackISRC(Base):
    __tablename__ = 'spotify_track_isrc'
    id = Column(Integer, primary_key=True)
    track_uri = Column(Text, unique=True, index=True)
    track_isrc = Column(Text, index=True)


class SpotifyBannedUri(Base):
    __tablename__ = 'spotify_ban_uri'
    id = Column(Integer, primary_key=True)
    uri = Column(Text, unique=True, index=True)
    created_ts = Column(DateTime,
                        nullable=False,
                        server_default=func.now(),
                        index=True)
    reason = Column(Text)


class SpotifyBannedWord(Base):
    __tablename__ = 'spotify_ban_word'
    id = Column(Integer, primary_key=True)
    word = Column(Text, index=True)
    created_ts = Column(DateTime,
                        nullable=False,
                        server_default=func.now(),
                        index=True)
    reason = Column(Text)


class SpotifyDB:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri, echo=False, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        self._create()
        #self.session = self.Session()

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

    def _create(self):
        Base.metadata.create_all(self.engine)


# END
