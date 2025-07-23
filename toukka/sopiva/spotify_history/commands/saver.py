#

import logging
import time

import click

from toukka.sopiva.spotify.util import get_spotify

from ..cli import cli_root

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@cli_root.command()
def save():
    saver = SpotifySaver()
    saver.run()


class SpotifySaver:

    def __init__(self):
        self.spotify = get_spotify()
        self._current_sleep = 600

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

        recently_played = self.spotify.recently_played()

        if recently_played:
            logger.info('recently played tracks found: %s', len(recently_played))
            for track in recently_played:
                logger.info('Track: %s by %s', track['name'], ', '.join(artist['name'] for artist in track['artists']))
        else:
            logger.debug('no recently played tracks found')




# END