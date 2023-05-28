#

from typing import Generator, Tuple, Optional

import logging

from tekore import Spotify
from tekore.model import Paging
from tekore.model import Item
from tekore._error import NotFound, BadRequest

from .decorators import check_from_token
# from .cached_dogpile import SpotifyDogpileCached

from ..album_audio_features import AlbumAudioFeatures

from .extended_classes import (
    SpotifyExtendedBase,
    SpotifyExtendedTokens,
    SpotifyExtendedTools
)

from toukka.cache.dogpile import region_spotify
dogpile_region = region_spotify

#
logger = logging.getLogger(__name__)
logging.getLogger("dogpile.cache").setLevel(logging.DEBUG)


class SpotifyExtended(SpotifyExtendedTokens, SpotifyExtendedTools):

    track_cached = check_from_token(
        dogpile_region.cache_on_arguments()(Spotify.track))
    tracks_cached = check_from_token(
        dogpile_region.cache_on_arguments()(Spotify.tracks))

    artist_cached = dogpile_region.cache_on_arguments()(Spotify.artist)
    artist_albums_cached = check_from_token(
        dogpile_region.cache_on_arguments()(Spotify.artist_albums))
    artist_related_artists_cached = dogpile_region.cache_on_arguments()(Spotify.artist_related_artists)
    artist_top_tracks_cached = check_from_token(
        dogpile_region.cache_on_arguments()(Spotify.artist_top_tracks))

    album_cached = check_from_token(
        dogpile_region.cache_on_arguments()(Spotify.album))
    albums_cached = check_from_token(
        dogpile_region.cache_on_arguments()(Spotify.albums))
    album_tracks_cached = check_from_token(
        dogpile_region.cache_on_arguments()(Spotify.album_tracks))

    track_audio_features_cached = dogpile_region.cache_on_arguments()(Spotify.track_audio_features)
    track_audio_analysis_cached = dogpile_region.cache_on_arguments()(Spotify.track_audio_analysis)

    def album_tracks_all_list(self, album_id: str, market: str = None):
        return list(self.all_items(self.album_tracks(album_id, market=market)))

    album_tracks_all_list_cached = check_from_token(
        dogpile_region.cache_on_arguments()(album_tracks_all_list))

    @dogpile_region.cache_on_arguments()
    def album_audio_features(self, album_id):
        album_tracks = self.album_tracks_all_list_cached(album_id)
        track_ids = [track.id for track in album_tracks]
        album_audio_features = list(self.tracks_audio_features(track_ids))
        return AlbumAudioFeatures(album_tracks, album_audio_features)

    # END


# END
