#

import logging

from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.util import get_spotify

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SpotifyPrinter:
    def __init__(self):
        self.spotify = get_spotify()
        self.market = self.spotify.current_user().country

    def print_all_from_uri(self, uri):
        uri_type, uri_id = self.spotify.convert.from_uri(uri)
        if uri_type == 'track':
            self.print_all_from_track_id(uri_id)
        if uri_type == 'episode':
            self.print_episode(uri_id)

    def check_and_print_relink(self, track_id):
        track = self.spotify.track(track_id, market=self.market)
        if track.linked_from:
            logger.info('track %s is relinked from %s', track.id, track.linked_from.id)
            # re-get _linked_ track without market
            track_relinked = self.spotify.track(track.id, market=None)
            print()
            printer(track_relinked)

    def print_all_from_track_id(self, track_id):
        track = self.spotify.track(track_id, market=None)
        album = self.spotify.album(track.album.id, market=None)

        artists = set()
        artists.update(_get_all_artist_ids_from_item(track))
        artists.update(_get_all_artist_ids_from_item(album))

        print(''.ljust(80, '='))
        for artist_id in artists:
            artist = self.spotify.artist(artist_id)
            printer(artist)
            print()

        printer(album)
        print()
        printer(track)
        self.check_and_print_relink(track_id)
        print()
        printer(self.spotify.track_audio_features(track_id))
        print(''.ljust(80, '='))

    def print_episode(self, episode_id):
        episode = self.spotify.episode(episode_id, market=None)
        print(''.ljust(80, '='))
        printer(episode)
        print(''.ljust(80, '='))


def _get_all_artist_ids_from_item(item):
    artists = set()
    for artist in item.artists:
        artists.add(artist.id)
    return artists

# END
