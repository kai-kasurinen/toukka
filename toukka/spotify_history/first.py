#

import os

from xdg.BaseDirectory import save_data_path

from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


class SpotifyHistory:
    def __init__(self):

        data_path = save_data_path('spotify-saver')
        database_file = os.path.join(data_path, '%s.db' % 'spotify-saver')
        database_uri = 'sqlite:///%s' % database_file

        self.engine = create_engine(database_uri)
        self.metadata = MetaData()
        self.metadata.reflect(self.engine)

        self.Base = automap_base(metadata=self.metadata)
        self.Base.prepare()

        self.history = self.Base.classes.history

        self.session = Session(self.engine)

    def count_by_track_id(self, track_id):
        return self.session.query(self.history).filter(self.history.mpris_track_id == track_id).count()


    def count_by_artist_name(self, artist_name):
        return self.session.query(self.history).filter(self.history.xesam_artist == artist_name).count()
