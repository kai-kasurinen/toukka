#
#

import logging
import pprint

import argh
import spotipy.convert

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify_history.util import get_spotify_history
from toukka.sopiva.spotify.printer import first as printer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def playlist_creator(from_artist: str = None):

    '''create playlist'''

    spotify = get_spotify()
    spotify_history = get_spotify_history()

    # FIXME:
    # 'album', 'single', 'appears_on', 'compilation'
    include_album_groups = ['album', 'sinlge', 'compilation']
    bad_word_in_album_names = ['christmas']
    filter_played = True
    filter_duplicate_isrc = True

    def all_artist_tracks(artist_id: str):
        ret = list()
        album_paging = spotify.artist_albums(
            artist_id,
            include_groups=include_album_groups,
            market='FI')
        for album in spotify.all_items_from_paging(album_paging):
            print(f'{album.name}')
            if any(bad in album.name.lower() for bad in bad_word_in_album_names):
                print('bad album name, skipping')
                continue
            album_tracks = list(spotify.all_items_from_paging(
                spotify.album_tracks(album.id, market=None, limit=50)))
            print(f'found {len(album_tracks)} tracks')
            ret.extend(album_tracks)
        return ret

    tracks = list()

    if from_artist:
        uri_type, uri_id = spotipy.convert.from_uri(from_artist)
        artist_tracks = all_artist_tracks(uri_id)
        print(f'found {len(artist_tracks)} tracks for artist {from_artist}')
        tracks.extend(artist_tracks)

    print(f'we have {len(tracks)} tracks')

    if filter_played:
        # NOTE: python is stupid. take copy of list so we can remove items from list
        for track in tracks.copy():
            played_count = spotify_history.count_by_track_id(track.uri)
            if played_count > 0:
                print(f'{track.uri}: played {played_count} times')
                tracks.remove(track)

    print(f'we have {len(tracks)} tracks')

    if filter_duplicate_isrc:
        isrcs = set()
        for track in tracks.copy():
            track_full = spotify.track(track.id)
            isrc = track_full.external_ids.get('isrc')
            if isrc is None:
                continue
            if isrc in isrcs:
                print(f'{track.uri}: isrc {isrc} is already seen')
                tracks.remove(track)
            else:
                isrcs.add(isrc)

    print(f'we have {len(tracks)} tracks')

    # for debugging
    for track in tracks:
        #printer.print_track(spotify.track(track.id))
        pass

    print(f'we have {len(tracks)} tracks')
    print('done')


def recommendations_test(artist_id: str = None,
                         track_id: str = None,
                         genre: str = None):
    '''get recommendations'''
    spotify = get_spotify()
    spotify_history = get_spotify_history()

    # FIXME
    seed_artists = None
    seed_tracks = None
    seed_genres = None

    if artist_id:
        seed_artists = [artist_id]
    if track_id:
        seed_tracks = [track_id]
    if genre:
        seed_genres = [genre]

    recommendations = spotify.recommendations(
        artist_ids=seed_artists,
        track_ids=seed_tracks,
        genres=seed_genres,
        limit=100,
        market=None)

    for seed in recommendations.seeds:
        seed.pprint()

    for track in recommendations.tracks:
        printer.print_track(track)



#

COMMANDS = [
    playlist_creator,
    recommendations_test
]

# END
