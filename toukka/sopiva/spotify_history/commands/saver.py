#

import logging
import time

import click
from requests import session

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_database.database import first as database


from ..cli import cli_root

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@cli_root.command()
def saver():
    saver = SpotifySaver()
    saver.run()


class SpotifySaver:

    def __init__(self):
        self.spotify = get_spotify()
        self.db = database.SpotifyDB()
        self._current_sleep = 600
        self._after = None

    def sleep(self):
        logger.debug('sleeping for %s seconds', self._current_sleep)
        time.sleep(self._current_sleep)

    def run(self):
        self.looper()

    def looper(self):

        while True:
            self.check_recently_played()
            self.sleep()

    def check_recently_played(self):
        logger.debug('checking recently played')

        # TODO: use after
        recently_played = self.spotify.playback_recently_played(after=self._after))
        logger.debug('after %s, before %s', recently_played.cursors.after, recently_played.cursors.before)
        recent_played_items = list(recently_played.items).reverse()
        logger.debug('found %s recently played items', len(recent_played_items))

        with self.db.session_scope() as session:

            for item in recent_played_items:
                logger.debug('recently played: %s', item)

                exists = session.query(database.TrackHistory).filter_by(played_at=item.played_at, track_id=item.track.id).first()

                if exists is None:
                    logger.debug('newly played: %s', item)
                    session.add(database.TrackHistory(played_at=item.played_at, track_id=item.track.id, meta=item.track))

            session.commit()
            logger.debug('committed recently played items') 

        self._after = recently_played.cursors.after

# END