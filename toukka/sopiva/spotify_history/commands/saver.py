#

import logging
import time

import click

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
        self._current_sleep = 300
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

        recently_played = self.spotify.playback_recently_played(after=self._after)

        if recently_played is None:
            logger.debug('no recently played items found')
            return

        logger.debug('after %s, before %s', recently_played.cursors.after, recently_played.cursors.before)
        recent_played_items = list(reversed(recently_played.items))
        logger.debug('found %s recently played items', len(recent_played_items))

        with self.db.session_scope() as session:

            for item in recent_played_items:
                logger.debug('recently played: %s', item.track.uri)

                exists = session.query(database.SpotifyHistory).filter_by(
                    played_at=item.played_at,
                    track_uri=item.track.uri).first()

                if exists is None:
                    logger.debug('newly played: %s', item.track.uri)
                    session.add(database.SpotifyHistory(played_at=item.played_at,
                                                         track_uri=item.track.uri,
                                                         meta=item.track.model_dump_json()))

            session.commit()
            logger.debug('committed recently played items') 

        self._after = recently_played.cursors.after

# END