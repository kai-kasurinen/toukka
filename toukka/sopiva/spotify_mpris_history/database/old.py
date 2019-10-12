#

from sqlalchemy import Column, DateTime, Float, Integer, Text, text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    mpris_track_id = Column(Text, index=True)
    mpris_length = Column(Integer)
    xesam_album = Column(Text)
    xesam_album_artist = Column(Text)
    xesam_artist = Column(Text)
    xesam_auto_rating = Column(Float)
    xesam_disc_number = Column(Integer)
    xesam_title = Column(Text)
    xesam_track_number = Column(Integer)
    xesam_url = Column(Text)
    mpris_art_url = Column(Text)
