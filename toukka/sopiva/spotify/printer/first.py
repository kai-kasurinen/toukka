#

import datetime
import dataclasses
import functools
import pprint
import logging
import datetime
import textwrap

import humanize

import deprecated

from toukka.sopiva.spotify.model import *

# FIXME: remove
from toukka.sopiva.spotify_history.util import get_spotify_history


@functools.singledispatch
def printer(arg):
    print(arg)


@printer.register
def print_item(item: Item):
    print(f'{type(item)}, {item.type}, {item.id}, {item.uri}')


@printer.register
def print_track(track: Track,
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

    track_dict = dataclasses.asdict(track)
    flags = _get_flags(track_dict, ['explicit', 'is_playable', 'is_local'])
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
def print_track_audio_features(features: AudioFeatures):
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
def print_album_simple(album: SimpleAlbum):
    # NOTE: popularity is only on FullAlbum
    print(f'album: {album.name} ({album.album_type.name}) ({album.uri})',
          f'({album.release_date} {album.release_date_precision})',
          f'(tracks: {album.total_tracks})')
    print('\tartists: %s' % _artists_to_string(album.artists))
    if album.album_group:
        print(f'\talbum group: {album.album_group}')
    if album.available_markets:
        print(f'\tmarkets: {len(album.available_markets)}')
    if album.is_playable is not None:
        print(f'\tplayable: {album.is_playable}')


@printer.register
def print_album_full(album: FullAlbum):
    '''print album'''
    print('album: {album.name} ({album.album_type.name}) ({album.uri})'.format(album=album),
          '({album.release_date} {album.release_date_precision})'.format(album=album),
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
    if album.is_playable is not None:
        print(f'\tplayable: {album.is_playable}')
    if album.label:
        print('\tlabel: {album.label}'.format(album=album))
    if album.copyrights:
        print('\tcopyrights:')
        for copyright in album.copyrights:
            print(f'\t\t{copyright.type}: {copyright.text}')

    album_dict = dataclasses.asdict(album)
    flags = _get_flags(album_dict, ['is_playable'])
    if flags:
        print('\tflags: %s' % flags)


# FIXME: use Artist
@printer.register
def print_artist(artist: FullArtist,
                 use_play_count=True):
    print(f'artist: {artist.name} ({artist.uri})',
          f'(popularity: {artist.popularity},',
          f'followers: {artist.followers.total})')

    if artist.genres:
        print(f'\tgenres: {list(artist.genres)}')
    if artist.external_urls:
        print(f'\texternal urls: {artist.external_urls}')

    # FIXME: move
    if use_play_count:
        _print_artist_played_count(artist)


def _print_artist_played_count(artist):
    spotify_history = get_spotify_history()
    print('\tplayed: %s' % spotify_history.count_by_artist_name(artist.name))


@printer.register
def print_playlist(playlist: Playlist):
    print(f'playlist: {playlist.name} ({playlist.uri})')
    print(f'\towner: {playlist.owner.display_name} ({playlist.owner.uri})')

    if playlist.description:
        print(f'\tdesc: {playlist.description}')

    if playlist.primary_color:
        print(f'\tprimary color: {playlist.primary_color}')

    playlist_dict = dataclasses.asdict(playlist)
    flags = _get_flags(playlist_dict, ['public', 'collaborative'])
    if flags:
        print(f'\tflags: {flags}')

    # only on FullPlaylist
    if isinstance(playlist, FullPlaylist):
        print(f'\tfollowers: {playlist.followers.total}')


@printer.register
def print_playlist_track(playlist_track: PlaylistTrack):
    plt = playlist_track
    # TODOE: added_at and added_by may be None
    print(f'playlist track:',
          f'added at {plt.added_at} by {plt.added_by.display_name or plt.added_by.id} ({plt.added_by.uri})')
    if plt.primary_color:
        print(f'\tprimary color: {plt.primary_color}')
    # TODO: video_thumbnail?

    plt_dict = dataclasses.asdict(plt)
    flags = _get_flags(plt_dict, ['is_local'])
    if flags:
        print(f'\tflags: {flags}')


@printer.register
def print_category(category: Category):
    print(f'category: {category.name} ({category.id})')


@printer.register
def print_recommendationseed(seed: RecommendationSeed):
    print(f'recommendation seed: {seed}')


# TODO: combine cpt and cpc
@printer.register
def print_currently_playing(cp: CurrentlyPlaying):
    print(f'currently playing: playing {cp.is_playing}')
    cpt_timestamp = datetime.datetime.fromtimestamp(cp.timestamp/1000.0)
    print('\ttimestamp: %s (%s)' % (
            humanize.naturaldate(cpt_timestamp),
            humanize.naturaltime(datetime.datetime.now() - cpt_timestamp)))
    print('\tprogress: %s' % datetime.timedelta(milliseconds=cp.progress_ms))
    if cp.context:
        print(f'\tcontext: {cp.context.type.name} ({cp.context.uri})')
    print(f'\ttype: {cp.currently_playing_type}')

    disallows_dict = dataclasses.asdict(cp.actions.disallows)
    disallows = _get_flags(disallows_dict, disallows_dict.keys())
    print(f'\tactions disallows: {disallows}')
    print()
    if cp.item:
        printer(cp.item)


@printer.register
def print_currently_playing_context(cpc: CurrentlyPlayingContext):
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
def print_track_local(track: LocalTrack):
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

    track_dict = dataclasses.asdict(track)
    flags = _get_flags(track_dict, ['explicit', 'is_playable', 'is_local'])
    if flags:
        print(f'\tflags: {flags}')


@printer.register
def print_playhistory(playhistory: PlayHistory):
    print(f'played at: {playhistory.played_at}')
    if playhistory.context:
        print(f'context: {playhistory.context}')
    printer(playhistory.track)


@printer.register
def print_episode(episode: Episode):
    print(
        f'episode: {episode.name} ({episode.uri})',
        f'({episode.release_date} {episode.release_date_precision})')

    if hasattr(episode, 'show'):
        print(f'\tshow: {episode.show.name} ({episode.show.uri})')
    print(f'\tduration: {datetime.timedelta(milliseconds=episode.duration_ms)}')
    print(f'\tlanguages: {episode.languages}')
    print(f'\tresume point: {episode.resume_point}')

    print(f'\tdescription:')
    print(textwrap.TextWrapper(
        width=70,
        initial_indent='\t\t',
        subsequent_indent='\t\t'
        ).fill(episode.description))

    if episode.external_urls:
        print(f'\texternal urls: {episode.external_urls}')

    episode_dict = dataclasses.asdict(episode)
    flags = _get_flags(
        episode_dict,
        ['explicit', 'is_playable', 'is_externally_hosted'])
    if flags:
        print(f'\tflags: {flags}')

    # FIXME: move
    _print_track_played_count(episode)


@printer.register
def print_show(show: Show):
    print(f'show: {show.name} ({show.uri}) ({show.media_type})')
    print(f'\tpublisher: {show.publisher}')
    print(f'\tlanguages: {show.languages}')

    if show.episodes is not None:
        print(f'\tepisodes: {show.episodes.total}')

    if show.available_markets:
        print(f'\tmarkets: {len(show.available_markets)}')

    if show.copyrights:
        print('\tcopyrights:')
        for copyright in show.copyrights:
            print(f'\t\t{copyright.type}: {copyright.text}')

    print(f'\tdescription:')
    print(textwrap.TextWrapper(
        width=70,
        initial_indent='\t\t',
        subsequent_indent='\t\t'
        ).fill(show.description))

    show_dict = dataclasses.asdict(show)
    flags = _get_flags(
        show_dict,
        ['is_externally_hosted'])
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
