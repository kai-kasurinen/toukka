#

'''spotify watcher'''

import logging
import time

import click

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# TODO Monitor also playlist changes

@cli_root.command()
def watcher():
    watcher = SpotifyWatcher()
    watcher.run()


class SpotifyMonitor:

    def __init__(self):
        self.spotify = get_spotify()

        self._current_sleep = 60
        self._current_playback = False
        self._last_playback = False

    def sleep(self):
        logger.debug('sleeping for %s seconds', self._current_sleep)
        time.sleep(self._current_sleep)
        self._current_sleep = 60

    def run(self):
        self.looper()

    def looper(self):

        while True:
            self.on_pre_loop()
            self.check_playback()
            self.sleep()
            self.on_post_loop()

    def check_playback(self):
        logger.debug('checking playback')
        self._current_playback = self.spotify.playback()

        if self._last_playback is False:
            logger.debug('no last playback, setting current as last')
            self._last_playback = self._current_playback
            self._current_sleep = 1
            self.on_no_last_playback()
            return
        
        if self._current_playback is None:
            logger.debug('no playback')
            return
        elif self._current_playback == self._last_playback:
            logger.debug('no change in playback')
        else:
            logger.debug('playback changed')
            self.on_changed_playback(self._current_playback)

        if self._current_playback.context is None:
            logger.debug('no context')
        elif self._current_playback.context == self._last_playback.context:
            logger.debug('no change in context')
        else:
            logger.debug('context changed')
            self.on_changed_context(self._current_playback.context)

        if self._current_playback.item is None:
            logger.debug('no item')
        elif self._current_playback.item == self._last_playback.item:
            logger.debug('no change in item')
        else:
            logger.debug('item changed')
            self.on_changed_item(self._current_playback.item)

        if self._current_playback.device is None:
            logger.debug('no device')
        elif self._current_playback.device == self._last_playback.device:
            logger.debug('no change in device')
        else:
            logger.debug('device changed')
            self.on_changed_device(self._current_playback.device)

        # TODO: support is_playing, currently_playing_type, progress_ms, *state

        # Update last playback
        self._last_playback = self._current_playback
        return

    def on_pre_loop(self):
            pass

    def on_post_loop(self):
            pass

    def on_no_last_playback(self):
         pass

    def on_changed_playback(self, playback):
            pass

    def on_changed_context(self, context):
            pass
    
    def on_changed_item(self, item):
            pass

    def on_changed_device(self, device):
            pass

# END


class SpotifyWatcher(SpotifyMonitor):

    def _print_dash_line(self):
            print(''.ljust(100, '='))

    def on_pre_loop(self):
            self._print_dash_line()

    def on_post_loop(self):
            pass

    def on_no_last_playback(self):
         printer(self._current_playback)
         printer(self._current_playback.item)

    def on_changed_playback(self, playback):
            pass

    def on_changed_context(self, context):
            printer(context)
    
    def on_changed_item(self, item):
            printer(item)

    def on_changed_device(self, device):
         printer(device)

# END
