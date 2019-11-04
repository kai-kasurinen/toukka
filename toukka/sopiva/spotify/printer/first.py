#

import datetime
import dataclasses
import functools
import pprint
import logging
import datetime

import humanize

import deprecated

import spotipy.model
import spotipy.model.base
import spotipy.model.playlist
import spotipy.model.album
import spotipy.model.category
import spotipy.model.recommendations
import spotipy.model.currently_playing
import spotipy.model.local

# FIXME: remove
from toukka.sopiva.spotify_history.util import get_spotify_history


@functools.singledispatch
def printer(arg):
    print(arg)


@printer.register
def print_item(item: spotipy.model.base.Item):
    print(f'{item.type}, {item.id}, {item.uri}')


@printer.register
def print_track(track: spotipy.model.FullTrack,
                use_play_count=True):
    print(f'track: {track.name} ({track.uri})',
          f'(popularity: {track.popularity})')

    print(f'\talbum: {track.album.name} ({track.album.uri})')
    print(f'\tartists: {_artists_to_string(track.artists)}')
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
        played_count_track = spotify_history.count_by_track_id(track.uri)
        isrc = track.external_ids.get('isrc')
        played_count_isrc = spotify_history.count_by_track_isrc(isrc)
        print(f'\tplayed: {played_count_track} track, {played_count_isrc} isrc')


@printer.register
def print_track_audio_features(features: spotipy.model.AudioFeatures):
    print(f'track features: ({features.uri})')
    print(f'\tacousticness: {features.acousticness:f},',
          f'danceability: {features.danceability:f},',
          f'energy: {features.energy:f}')
    print(f'\tinstrumentalness: {features.instrumentalness:f},',
          f'liveness: {features.liveness:f},',
          f'speechiness: {features.speechiness:f},',
          f'valence: {features.valence:f}')
    print(f'\tkey: {features.key}',
          f'mode: {features.mode}',
          f'tempo: {features.tempo:f},',
          f'loudness: {features.loudness:f}')


@printer.register
def print_album_simple(album: spotipy.model.album.SimpleAlbum):
    # NOTE: popularity is only on FullAlbum
    print(f'album: {album.name} ({album.album_type.name}) ({album.uri})',
          f'({album.release_date} {album.release_date_precision.name})',
          f'(tracks: {album.total_tracks})')
    print('\tartists: %s' % _artists_to_string(album.artists))
    if album.album_group:
        print(f'\talbum group: {album.album_group}')
    if album.available_markets:
        print(f'\tmarkets: {len(album.available_markets)}')
    if album.restrictions:
        print(f'\trestrictions: {album.restrictions}')


@printer.register
def print_album_full(album: spotipy.model.FullAlbum):
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

    # only on FullPlaylist
    if isinstance(playlist, spotipy.model.playlist.FullPlaylist):
        print(f'\tdesc: {playlist.description}')
        print(f'\tfollowers: {playlist.followers.total}')


@printer.register
def print_playlist(playlisttrack: spotipy.model.playlist.PlaylistTrack):
    plt = playlisttrack
    # TODOE: added_at and added_by may be None
    print(f'playlist track:',
          f'added at {plt.added_at} by {plt.added_by.display_name or plt.added_by.id} ({plt.added_by.uri})')
    if plt.primary_color:
        print(f'\tprimary color: {plt.primary_color}')
    # TODO: video_thumbnail?
    flags = _get_flags(plt.asdict(), ['is_local'])
    if flags:
        print(f'\tflags: {flags}')


@printer.register
def print_category(category: spotipy.model.category.Category):
    print(f'category: {category.name} ({category.id})')


@printer.register
def print_recommendationseed(seed: spotipy.model.recommendations.RecommendationSeed):
    print(f'recommendation seed: {seed}')


@printer.register
def print_currently_playing_track(cpt: spotipy.model.currently_playing.CurrentlyPlayingTrack):
    print(f'currently playing: {cpt.is_playing}')
    cpt_timestamp = datetime.datetime.fromtimestamp(cpt.timestamp/1000.0)
    print('\ttimestamp: %s (%s)' % (
            humanize.naturaldate(cpt_timestamp),
            humanize.naturaltime(datetime.datetime.now() - cpt_timestamp)))
    print('\tprogress: %s' % datetime.timedelta(milliseconds=cpt.progress_ms))
    print(f'\tcontext: {cpt.context.type} ({cpt.context.uri})')
    print(f'\ttype: {cpt.currently_playing_type}')
    disallows = _get_flags(cpt.actions.disallows.asdict(), cpt.actions.disallows.asdict().keys())
    print(f'\tactions disallows: {disallows}')
    print()
    printer(cpt.item)


@printer.register
def print_track_local(track: spotipy.model.local.LocalTrack):
    print(f'local track: {track.name} ({track.uri})')

    print(f'\talbum: {track.album.name} ({track.album.uri})')
    print(f'\tartists: {_artists_to_string(track.artists)}')
    print(f'\tduration: {datetime.timedelta(milliseconds=track.duration_ms)}')
    print(f'\ttrack number: {track.track_number},',
          f'disc number: {track.disc_number}')

    if track.external_ids:
        print(f'\texternal ids: {track.external_ids}')
    if track.external_urls:
        print(f'\texternal urls: {track.external_urls}')
    if track.available_markets:
        print(f'\tmarkets: {len(track.available_markets)}')

    flags = _get_flags(track.asdict(), ['explicit', 'is_playable', 'is_local'])
    if flags:
        print(f'\tflags: {flags}')


# UTILS

def _artists_to_string(artists):
    return ", ".join("%s (%s)" % (artist.name, artist.uri) for artist in artists)


# from toukka.utils.misc_utils
# modified
def _get_flags(_dict, _needed, _value_is=True):
    return [key for key, value in _dict.items() if key in _needed and value is _value_is]

# END
