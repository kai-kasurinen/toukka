#

import logging

from tekore import Spotify

from toukka.cache.dogpile import region_spotify


from .decorators import check_from_token

# TODO: handle from_token better
# TODO: do something when pickling fails?

dogpile_region = region_spotify

logging.getLogger("dogpile.cache").setLevel(logging.DEBUG)

class SpotifyDogpileCached(Spotify):

    # cache-control: public, max-age>0
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

    # cache-control: private, max-age=0
    track_audio_features_cached = dogpile_region.cache_on_arguments()(Spotify.track_audio_features)
    track_audio_analysis_cached = dogpile_region.cache_on_arguments()(Spotify.track_audio_analysis)

# END
