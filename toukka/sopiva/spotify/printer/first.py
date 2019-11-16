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
import spotipy.model.play_history
import spotipy.model.podcast

# FIXME: remove
from toukka.sopiva.spotify_history.util import get_spotify_history


@functools.singledispatch
def printer(arg):
    print(arg)


@printer.register
def print_item(item: spotipy.model.base.Item):
    print(f'{type(item)}, {item.type}, {item.id}, {item.uri}')


@printer.register
def print_track(track: spotipy.model.track.Track,
                use_play_count=True):
    print(f'track: {track.name} ({track.uri})', end='')

    if hasattr(track, 'popularity'):
        print(f' (popularity: {track.popularity})')
    else:
        print()

    if hasattr(track, 'album'):
        print(f'\talbum: {track.album.name} ({track.album.uri})')

    print(f'\tartists: {_artists_to_string(track.artists)}')
    print(f'\tduration: {datetime.timedelta(milliseconds=track.duration_ms)}')
    print(f'\ttrack number: {track.track_number},',
          f'disc number: {track.disc_number}')

    if hasattr(track, 'external_ids') and track.external_ids:
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

    # FIXME: move
    if use_play_count:
        _print_track_played_count(track)


def _print_track_played_count(track):
    spotify_history = get_spotify_history()
    played_count_track = spotify_history.count_by_track_id(track.uri)

    played_count_isrc = None
    if hasattr(track, 'external_ids'):
        isrc = track.external_ids.get('isrc')
        if isrc:
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


# FIXME: compine album_simple and album_full
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


# FIXME: use Artist
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

    # FIXME: move
    if use_play_count:
        _print_artist_played_count(artist)


def _print_artist_played_count(artist):
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


# TODO: combine cpt and cpc
@printer.register
def print_currently_playing_track(cpt: spotipy.model.currently_playing.CurrentlyPlayingTrack):
    print(f'currently playing: playing {cpt.is_playing}')
    cpt_timestamp = datetime.datetime.fromtimestamp(cpt.timestamp/1000.0)
    print('\ttimestamp: %s (%s)' % (
            humanize.naturaldate(cpt_timestamp),
            humanize.naturaltime(datetime.datetime.now() - cpt_timestamp)))
    print('\tprogress: %s' % datetime.timedelta(milliseconds=cpt.progress_ms))
    if cpt.context:
        print(f'\tcontext: {cpt.context.type.name} ({cpt.context.uri})')
    print(f'\ttype: {cpt.currently_playing_type}')
    disallows = _get_flags(cpt.actions.disallows.asdict(), cpt.actions.disallows.asdict().keys())
    print(f'\tactions disallows: {disallows}')
    print()
    if cpt.item:
        printer(cpt.item)


@printer.register
def print_currently_playing_context(cpc: spotipy.model.currently_playing.CurrentlyPlayingContext):
    print(f'currently playing context: playing {cpc.is_playing}')
    print(f'\tdevice: {cpc.device}')
    print(f'\tstate: repeat: {cpc.repeat_state}, shuffle: {cpc.shuffle_state}')
    if cpc.context:
        print(f'\tcontext: {cpc.context.type.name} ({cpc.context.uri})')
    print(f'\ttype: {cpc.currently_playing_type.name}')
    print()
    if cpc.item:
        printer(cpc.item)


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


@printer.register
def print_playhistory(playhistory: spotipy.model.play_history.PlayHistory):
    print(f'played at: {playhistory.played_at}')
    if playhistory.context:
        print(f'context: {playhistory.context}')
    printer(playhistory.track)


@printer.register
def print_episode(episode: spotipy.model.podcast.Episode):
    print(f'episode: {episode.name} ({episode.uri})')
    print(f'\treleased: {episode.release_date} {episode.release_date_precision.name}')
    print(f'\tdesc: {episode.description}')
    print(f'\tduration: {datetime.timedelta(milliseconds=episode.duration_ms)}')
    print(f'\tlanguages: {episode.languages}')


    if episode.external_urls:
        print(f'\texternal urls: {episode.external_urls}')

    flags = _get_flags(episode.asdict(), ['explicit', 'is_playable', 'is_externally_hosted'])
    if flags:
        print(f'\tflags: {flags}')

    # FIXME: move
    _print_track_played_count(episode)

    if episode.show:
        print()
        printer(episode.show)


@printer.register
def print_show(show: spotipy.model.podcast.Show):
    print(f'show: {show.name} ({show.uri}) ({show.media_type})')
    print(f'\tdesc: {show.description}')
    print(f'\tpublisher: {show.publisher}')
    print(f'\tlanguages: {show.languages}')

    if show.available_markets:
        print(f'\tmarkets: {len(show.available_markets)}')


# UTILS


def _artists_to_string(artists):
    return ", ".join("%s (%s)" % (artist.name, artist.uri) for artist in artists)


# from toukka.utils.misc_utils
# modified
def _get_flags(_dict, _needed, _value_is=True):
    return [key for key, value in _dict.items() if key in _needed and value is _value_is]

# END
