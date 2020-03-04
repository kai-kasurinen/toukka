#

from boltons.funcutils import wraps
from tekore.client import Spotify

from toukka.cache.dogpile import redis

# TODO: handle from_token better
# TODO: do something when pickling fails?

region = redis


def check_from_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # TODO: remove
        if kwargs.get('market') == 'from_token':
            raise Exception('market is from_token')
        # elif 'market' not in kwargs.keys():
        #     raise Exception('market is not defined')
        else:
            return f(*args, **kwargs)
    return wrapper


class SpotifyCached(Spotify):

    # cache-control: public, max-age>0
    track = check_from_token(
        region.cache_on_arguments()(Spotify.track))

    tracks = check_from_token(
        region.cache_on_arguments()(Spotify.tracks))
    artist = region.cache_on_arguments()(Spotify.artist)
    artist_albums = check_from_token(
        region.cache_on_arguments()(Spotify.artist_albums))
    artist_related_artists = region.cache_on_arguments()(Spotify.artist_related_artists)
    artist_top_tracks = check_from_token(
        region.cache_on_arguments()(Spotify.artist_top_tracks))
    album = check_from_token(
        region.cache_on_arguments()(Spotify.album))
    albums = check_from_token(
        region.cache_on_arguments()(Spotify.albums))
    album_tracks = check_from_token(
        region.cache_on_arguments()(Spotify.album_tracks))

    # cache-control: private, max-age=0
    track_audio_features = region.cache_on_arguments()(Spotify.track_audio_features)
    track_audio_analysis = region.cache_on_arguments()(Spotify.track_audio_analysis)

# END
