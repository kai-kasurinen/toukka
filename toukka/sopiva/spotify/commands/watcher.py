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
        self._current_playback = None
        self._last_playback = None

    def sleep(self):
        logger.debug('sleeping for %s seconds', self._current_sleep)
        time.sleep(self._current_sleep)
        # TODO: add dynamic sleep time
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
        logger.info('checking playback')
        self._current_playback = self.spotify.playback()

        if self._current_playback is None and self._last_playback is None:
            logger.debug('no current playback and no last playback')
            self._current_sleep = 120

        elif self._current_playback is not None and self._last_playback is not None:

            if self._current_playback != self._last_playback:
                logger.debug('playback changed')
                self.on_changed_playback(self._current_playback)

            if self._current_playback.is_playing != self._last_playback.is_playing:
                logger.debug('is playing changed')
                self.on_changed_is_playing(self._current_playback.is_playing)

            if self._current_playback.currently_playing_type != self._last_playback.currently_playing_type:
                logger.debug('currently playing type changed')
                self.on_changed_playing_type(self._current_playback.currently_playing_type)

            if self._current_playback.context != self._last_playback.context:
                logger.debug('context changed')
                self.on_changed_context(self._current_playback.context)

            if self._current_playback.item != self._last_playback.item:
                logger.debug('item changed')
                self.on_changed_item(self._current_playback.item)

            if self._current_playback.device != self._last_playback.device:
                logger.debug('device changed')
                self.on_changed_device(self._current_playback.device)

        elif self._current_playback is not None and self._last_playback is None:
                logger.debug('Playback started for the first time or resumed after being off.')
                self._current_sleep = 1
                self.on_playback_appears(self._current_playback)
        
        elif self._current_playback is None and self._last_playback is not None:
            logger.debug('Playback stopped or paused.')
            self.on_playback_disappears()

        else:
            logger.warning('This should not happen')
            pass

        
        # Update last playback
        self._last_playback = self._current_playback
        return

    def on_pre_loop(self):
        pass

    def on_post_loop(self):
        pass

    def on_playback_appears(self, playback):
        pass
    
    def on_playback_disappears(self):
        pass

    def on_changed_playback(self, playback):
        pass

    def on_changed_is_playing(self, is_playing):
        pass

    def on_changed_playing_type(self, playing_type):
        pass

    def on_changed_context(self, context):
        pass
    
    def on_changed_item(self, item):
        if item is None:
            return
        elif item.type == 'track':
            self.on_changed_track(item)
        elif item.type == 'episode':
            self.on_changed_episode(item)
        else:
            logger.warning('Unknown item type: %s', item.type)

    def on_changed_track(self, track):
        pass

    def on_changed_episode(self, episode):
        pass

    def on_changed_device(self, device):
        pass

# END


class SpotifyWatcher(SpotifyMonitor):

    def printer(self, item):
        printer(item)
        self._something_printed = True

    def _print_dash_line(self):
        print(''.ljust(100, '='))

    def on_pre_loop(self):
        self._something_printed = False

    def on_post_loop(self):
        if self._something_printed:
            self._print_dash_line()

    def on_playback_appears(self, playback):
        self.printer(playback)

        if playback.item is not None:
            self.on_changed_item(playback.item)

    def on_playback_disappears(self):
        logger.info('Playback stopped or paused.')

    def on_changed_playback(self, playback):
        pass

    def on_changed_is_playing(self, is_playing):
        if is_playing:
            logger.info('Playback started')
        else:
            logger.info('Playback stopped')

    def on_changed_playing_type(self, playing_type):
        logger.info('Currently playing type changed to: %s', playing_type)

    def on_changed_context(self, context):
        self.printer(context)
    
    def on_changed_track(self, track):
        self.print_track(track)

    def on_changed_episode(self, episode):
        self.printer(episode)

    def on_changed_device(self, device):
        self.printer(device)

    def print_track(self, track):
        self.print_track_artists(track)
        self.printer(self.spotify.album(track.album.id))
        self.printer(track)
        self.printer(self.spotify.track_audio_features_cached(track.id))

    def print_track_artists(self, track):
        artist_ids = set()
        artists = set()
        for artist in track.artists:
            artist_ids.add(artist.id)
        for artist in track.album.artists:
            artist_ids.add(artist.id)
  
        # NOTE: artist() is usually cached, so this is fast (artists() is usually not cached)
        for artist_id in artist_ids:
            self.printer(self.spotify.artist(artist_id))
  

# END
