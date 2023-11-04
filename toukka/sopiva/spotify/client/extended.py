#

from typing import Generator, Tuple, Optional

import logging
import unidecode

from tekore import Spotify

from .decorators import check_from_token
# from .cached_dogpile import SpotifyDogpileCached

from ..audio_features import TracksFeaturesDF, AlbumFeaturesDF
from ..filters import make_filter_by_artist_genre, make_filter_by_album_label

from .extended_classes import (
    SpotifyExtendedBase,
    SpotifyExtendedTokens,
    SpotifyExtendedTools
)

from toukka.cache.durations import DAY, WEEK, MONTH, HALF_YEAR, YEAR
from toukka.cache.dogpile import region_spotify

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# logging.getLogger("dogpile.cache").setLevel(logging.DEBUG)


dogpile_region = region_spotify


class SpotifyExtended(SpotifyExtendedTokens, SpotifyExtendedTools):

    track_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=HALF_YEAR)(Spotify.track))
    tracks_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=HALF_YEAR)(Spotify.tracks))

    artist_cached = dogpile_region.cache_on_arguments(expiration_time=MONTH)(Spotify.artist)
    artist_albums_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=WEEK)(Spotify.artist_albums))

    artist_related_artists_cached = dogpile_region.cache_on_arguments(
        expiration_time=WEEK)(Spotify.artist_related_artists)

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

    def playlists_all_list(self, user_id: str):
        return list(self.all_items(self.playlists(user_id)))

    playlists_all_list_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=WEEK)(playlists_all_list))
    def playlist_items_all_list(self, playlist_id: str, market: str = None):
        return list(self.all_items(self.playlist_items(playlist_id=playlist_id, market=market)))

    playlist_items_all_list_cached = check_from_token(
        dogpile_region.cache_on_arguments(expiration_time=DAY)(playlist_items_all_list))

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

    def artists_by_genre(self, genre_name):
        # NOTE: genre.name is unicode and artists.genres are ascii
        genre_name = unidecode.unidecode(genre_name)
        # NOTE: search support unicode and ascii genre name
        search = self.search(query=f'genre:"{genre_name}"', types=['artist'])
        paging = search[0]
        artists = list(self.all_items(paging))
        artists_filter = filter(make_filter_by_artist_genre(genre_name), artists)
        artists_filter = list(artists_filter)
        logger.debug('total results %i (pager %i), after filtering %i',
                     len(artists), paging.total, len(artists_filter))

        return artists_filter

    artists_by_genre_cached = dogpile_region.cache_on_arguments(expiration_time=WEEK)(artists_by_genre)

    def albums_by_label(self, label_name, market=None):
        logger.debug('searching albums by label: %s', label_name)
        search = self.search(query=f'label:"{label_name}"', types=['album'], market=market)
        paging = search[0]
        albums = self.all_items(paging)
        albums_ids = [album.id for album in albums]
        albums = self.albums(albums_ids, market=market)
        albums = list(filter(make_filter_by_album_label(label_name), albums))
        logger.debug('total results %i, after filtering %i', paging.total, len(albums))

        return albums

    def simple_to_full(self, items_list):
        if not items_list:
            return []
        item_type = items_list[0].type
        item_ids = [item.id for item in items_list]
        method_name = item_type + "s"
        return getattr(self, method_name)(item_ids)




    # END


# END
