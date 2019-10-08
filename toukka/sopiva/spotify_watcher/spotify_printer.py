#

import logging
import spotipy

import toukka.sopiva.spotify.printer.first as printer
from toukka.sopiva.spotify.util import get_spotify

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SpotifyPrinter:
    def __init__(self):
        self.spotify = get_spotify()
        self.market = 'FI'

    def print_all_from_track_uri(self, track_uri):
        uri_type, uri_id = spotipy.convert.from_uri(track_uri)
        track_id = uri_id
        self.print_all_from_track_id(track_id)

    def check_and_print_relink(self, track_id):
        track = self.spotify.track(track_id, market=self.market)
        if track.linked_from:
            logger.info('track %s is relinked from %s', track.id, track.linked_from.id)
            # re-get _linked_ track without market
            track_relinked = self.spotify.track(track.id, market=None)
            print()
            printer.print_track(track_relinked)

    def print_all_from_track_id(self, track_id):
        track = self.spotify.track(track_id, market=None)
        album = self.spotify.album(track.album.id, market=None)

        artists = set()
        artists.update(_get_all_artist_ids_from_item(track))
        artists.update(_get_all_artist_ids_from_item(album))

        print()
        for artist_id in artists:
            artist = self.spotify.artist(artist_id)
            printer.print_artist(artist)
            print()

        printer.print_album(album)
        print()
        printer.print_track(track)
        self.check_and_print_relink(track_id)
        print()
        printer.print_track_audio_features(self.spotify.track_audio_features(track_id))


def _get_all_artist_ids_from_item(item):
    artists = set()
    for artist in item.artists:
        artists.add(artist.id)
    return artists

# END
