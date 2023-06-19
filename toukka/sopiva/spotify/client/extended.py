#

from typing import Generator, Tuple, Optional

import logging

from tekore import Spotify

from .decorators import check_from_token
# from .cached_dogpile import SpotifyDogpileCached

from ..audio_features import TracksFeaturesDF, AlbumFeaturesDF

from .extended_classes import (
    SpotifyExtendedBase,
    SpotifyExtendedTokens,
    SpotifyExtendedTools
)

from toukka.cache.durations import DAY, WEEK, MONTH, HALF_YEAR, YEAR
from toukka.cache.dogpile import region_spotify
dogpile_region = region_spotify
# logging.getLogger("dogpile.cache").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


class SpotifyExtended(SpotifyExtendedTokens, SpotifyExtendedTools):

    track_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=MONTH)(Spotify.track))
    tracks_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=MONTH)(Spotify.tracks))

    artist_cached = dogpile_region.cache_on_arguments(expiration_time=MONTH)(Spotify.artist)
    artist_albums_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=WEEK)(Spotify.artist_albums))

    artist_related_artists_cached = dogpile_region.cache_on_arguments(expiration_time=WEEK)(Spotify.artist_related_artists)
    artist_top_tracks_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=DAY)(Spotify.artist_top_tracks))

    album_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=MONTH)(Spotify.album))
    albums_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=MONTH)(Spotify.albums))
    album_tracks_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=MONTH)(Spotify.album_tracks))

    track_audio_features_cached = dogpile_region.cache_on_arguments(expiration_time=YEAR)(Spotify.track_audio_features)
    track_audio_analysis_cached = dogpile_region.cache_on_arguments(expiration_time=YEAR)(Spotify.track_audio_analysis)

    def album_tracks_all_list(self, album_id: str, market: str = None):
        return list(self.all_items(self.album_tracks(album_id, market=market)))

    album_tracks_all_list_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=YEAR)(album_tracks_all_list))

    def tracks_features_df(self, track_ids):
        tracks = list(self.tracks(track_ids))
        audio_features = list(self.tracks_audio_features(track_ids))
        return TracksFeaturesDF(tracks, audio_features)

    def album_features_df(self, album_id):
        album_tracks = self.album_tracks_all_list(album_id)
        track_ids = [track.id for track in album_tracks]
        album_audio_features = list(self.tracks_audio_features(track_ids))
        return AlbumFeaturesDF(album_tracks, album_audio_features)

    @dogpile_region.cache_on_arguments(expiration_time=YEAR)
    def album_features_df_cached(self, album_id):
        album_tracks = self.album_tracks_all_list_cached(album_id)
        track_ids = [track.id for track in album_tracks]
        album_audio_features = list(self.tracks_audio_features(track_ids))
        return AlbumFeaturesDF(album_tracks, album_audio_features)

    # END


# END
