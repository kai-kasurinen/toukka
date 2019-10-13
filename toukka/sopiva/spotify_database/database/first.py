#

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
metadata = Base.metadata


class SpotifyTrackISRC(Base):
    __tablename__ = 'spotify_track_isrc'
    id = Column(Integer, primary_key=True)
    track_uri = Column(Text, unique=True, index=True)
    track_isrc = Column(Text, index=True)


class SpotifyDB:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def _create(self):
        Base.metadata.create_all(self.engine)


# END
