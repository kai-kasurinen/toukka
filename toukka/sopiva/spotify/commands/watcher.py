#

'''spotify watcher'''

import logging
import time

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@cli_root.command()
def watcher():
    watcher = SpotifyWatcher()
    watcher.loop()


class SpotifyMonitor:

    def __init__(self):
        self.spotify = get_spotify()

        self.current_sleep = 60

        self.current_cp = False
        self.last_cp = False

        self.current_playback = False
        self.last_playback = False

    def sleep(self):
        logger.debug('sleeping for %s seconds', self.current_sleep)
        time.sleep(self.current_sleep)
        self.current_sleep = 60

    def loop(self):

        while True:

            self.check_currently_playing()
            self.check_playback()
            self.sleep()

            
    def check_currently_playing(self):
            logger.debug('checking currently playing')
            
            self.current_cp = self.spotify.playback_currently_playing()

            if self.last_cp is False:
                logger.debug('no last currently playing, setting current as last')
                self.last_cp = self.current_cp
                self.current_sleep = 1
                return

            if self.current_cp is None:
                logger.debug('no currently playing')
            elif self.current_cp == self.last_cp:
                logger.debug('no change in currently playing')
            else:
                logger.debug('currently playing changed')
                self.on_currently_playing()

            if self.current_cp.context is None:
                logger.debug('no context')
            elif self.current_cp.context == self.last_cp.context:
                logger.debug('no change in context')
            else:
                logger.debug('context changed')

            if self.current_cp.item is None:
                logger.debug('no item')
            elif self.current_cp.item == self.last_cp.item:
                logger.debug('no change in item')
            else:
                logger.debug('item changed')

            self.last_cp = self.current_cp
            return

    def check_playback(self):
        logger.debug('checking playback')
        self.current_playback = self.spotify.playback()

        if self.last_playback is False:
            logger.debug('no last playback, setting current as last')
            self.last_playback = self.current_playback
            self.current_sleep = 1
            return

    def on_currently_playing(self):
            pass

# END


class SpotifyWatcher(SpotifyMonitor):

    def _print_dash_line(self):
            print(''.ljust(100, '='))

# END
