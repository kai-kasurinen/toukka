#

import datetime
import dataclasses
import functools
import pprint
import logging

import autologging
import deprecated

import spotipy.model
import spotipy.model.base
import spotipy.model.playlist

from toukka.sopiva.spotify_history.util import get_spotify_history

logger = logging.getLogger(__name__)


@functools.singledispatch
@autologging.traced
def printer(arg):
    print(arg)


@printer.register
@autologging.traced
def print_item(item: spotipy.model.base.Item):
    print(f'{item.type}, {item.id}, {item.uri}')


@printer.register
def print_track(track: spotipy.model.FullTrack,
                use_play_count=True):
    '''print track'''
    print(f'track: {track.name} ({track.uri})',
          f'(popularity: {track.popularity})')

    print(f'\talbum: {track.album.name} ({track.album.uri})')
    print(f'\tartists: {_artists_to_string(track.artists)})')
    print(f'\tduration: {datetime.timedelta(milliseconds=track.duration_ms)}')
    print(f'\ttrack number: {track.track_number},',
          f'disc number: {track.disc_number}')

    if track.external_ids:
        print(f'\texternal ids: {track.external_ids}')
    if track.external_urls:
        print(f'\texternal urls: {track.external_urls}')
    if track.available_markets:
        print(f'\tmarkets: {len(track.available_markets)}')
    if track.linked_from:
        print(f'\tlinked from: {track.linked_from}')
    if track.restrictions:
        print(f'\trestrictions: {track.restrictions}')

    flags = _get_flags(track.asdict(), ['explicit', 'is_playable', 'is_local'])
    if flags:
        print(f'\tflags: {flags}')

    if use_play_count:
        spotify_history = get_spotify_history()
        played_count = spotify_history.count_by_track_id(track.uri)
        print(f'\tplayed: {played_count}')


@printer.register
def print_track_audio_features(features: spotipy.model.AudioFeatures):
    print(f'track features: {features.uri}')
    print(f'\tacousticness: {features.acousticness},',
          f'danceability: {features.danceability},',
          f'energy: {features.energy}')
    print(f'\tinstrumentalness: {features.instrumentalness},',
          f'liveness: {features.liveness},',
          f'speechiness: {features.speechiness},',
          f'valence: {features.valence}')
    print(f'\tkey: {features.key}',
          f'mode: {features.mode}',
          f'tempo: {features.tempo},',
          f'loudness: {features.loudness}')


@printer.register
def print_album(album: spotipy.model.FullAlbum):
    '''print album'''
    print('album: {album.name} ({album.album_type.name}) ({album.uri})'.format(album=album),
          '({album.release_date} {album.release_date_precision.name})'.format(album=album),
          '(popularity: {album.popularity}, tracks: {album.total_tracks})'.format(album=album))
    print('\tartists: %s' % _artists_to_string(album.artists))

    if album.genres:
        print('\tgenres: {album.genres}'.format(album=album))
    if album.external_ids:
        print('\texternal ids: {album.external_ids}'.format(album=album))
    if album.external_urls:
        print('\texternal urls: {album.external_urls}'.format(album=album))
    if album.available_markets:
        print('\tmarkets: %s' % (len(album.available_markets)))
    if album.restrictions:
        print('\trestrictions: {album.restrictions}'.format(album=album))
    if album.label:
        print('\tlabel: {album.label}'.format(album=album))
    if album.copyrights:
        print('\tcopyrights:')
        for copyright_ in album.copyrights:
            print(f'\t\t{copyright_.type}: {copyright_.text}')

    flags = _get_flags(dataclasses.asdict(album), ['is_playable'])
    if flags:
        print('\tflags: %s' % flags)


@printer.register
def print_artist(artist: spotipy.model.FullArtist,
                 use_play_count=True):
    print('artist: {artist.name} ({artist.uri})'.format(artist=artist),
          '(popularity: {artist.popularity},'.format(artist=artist),
          'followers: {artist.followers.total})'.format(artist=artist))

    if artist.genres:
        print('\tgenres: {artist.genres}'.format(artist=artist))
    if artist.external_urls:
        print('\texternal urls: {artist.external_urls}'.format(artist=artist))

    if use_play_count:
        spotify_history = get_spotify_history()
        print('\tplayed: %s' % spotify_history.count_by_artist_name(artist.name))


@printer.register
def print_playlist(playlist: spotipy.model.playlist.Playlist):
    print(f'playlist: {playlist.name} ({playlist.uri})')
    print(f'\towner: {playlist.owner.display_name} ({playlist.owner.uri})')

    flags = _get_flags(playlist.asdict(), ['public', 'collaborative'])
    if flags:
        print(f'\tflags: {flags}')


# OLD

@deprecated.deprecated
def print_tracks(tracks):
    '''print tracks'''
    print()
    for track in tracks:
        print_track(track)
        print()


@deprecated.deprecated
def print_albums(albums):
    print()
    for album in albums:
        print_album(album)
        print()


@deprecated.deprecated
def print_artists(artists):
    print()
    for artist in artists:
        print_artist(artist)
        print()


def _artists_to_string(artists):
    return ", ".join("%s (%s)" % (artist.name, artist.uri) for artist in artists)


# from toukka.utils.misc_utils
# modified
def _get_flags(_dict, _needed, _value_is=True):
    return [key for key, value in _dict.items() if key in _needed and value is _value_is]
