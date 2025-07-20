#

import datetime
import dataclasses
import pprint
import logging
import datetime
import textwrap

import humanize

import deprecated

from toukka.printer import printer
from toukka.sopiva.spotify.model import *
from toukka.sopiva.spotify.model.audio_features import AudioPitch, AudioMode

# FIXME: remove
from toukka.sopiva.spotify_history.util import get_spotify_history

__SPOTIFY_HISTORY__ = None


def _get_spotify_history():
    global __SPOTIFY_HISTORY__
    if __SPOTIFY_HISTORY__ is None:
        __SPOTIFY_HISTORY__ = get_spotify_history()
    return __SPOTIFY_HISTORY__


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
    if track.available_markets is not None:
        if 0 < len(track.available_markets) < 10:
            print(f'\tmarkets: {len(track.available_markets)} ({list(track.available_markets)})')
        else:
            print(f'\tmarkets: {len(track.available_markets)}')
    if track.linked_from is not None:
        print(f'\tlinked from: {track.linked_from.uri}')
    if track.restrictions:
        print(f'\trestrictions: {track.restrictions.reason}')

    track_dict = track.dict()
    flags = _get_flags(track_dict, ['explicit', 'is_playable', 'is_local'])
    if flags:
        print(f'\tflags: {flags}')

    # FIXME: move
    if use_play_count:
        _print_track_played_count(track)


def _print_track_played_count(track):
    spotify_history = _get_spotify_history()
    track_played_info = spotify_history.count_by_track_id_with_timestamps(track.uri)

    if track_played_info.count >= 1:
        print(f'\tplayed: {track_played_info.count}', 
              f'({track_played_info.min.date()} - {track_played_info.max.date()})')

    isrc = None
    if hasattr(track, 'external_ids') and track.external_ids:
        isrc = track.external_ids.get('isrc')

    if isrc is not None:
        isrc_played_info = spotify_history.count_by_track_isrc_with_timestamps(isrc)

        if isrc_played_info.count >= 1:
            print(f'\tisrc played: {isrc_played_info.count}',
                  f'({isrc_played_info.min.date()} - {isrc_played_info.max.date()})')


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

    key_ = AudioPitch(features.key)
    mode_ = AudioMode(features.mode)

    print(f'\tkey: {features.key} ({key_}),',
          f'mode: {features.mode} ({mode_.name}),',
          f'time signature: {features.time_signature}')

    print(f'\ttempo: {features.tempo:f},',
          f'loudness: {features.loudness:f}')


@printer.register
def print_track_audio_analysis(analysis: AudioAnalysis):
    print(analysis.meta)
    print(analysis)


# FIXME: compine album_simple and album_full
@printer.register
def print_album_simple(album: SimpleAlbum):
    # NOTE: popularity is only on FullAlbum
    print(f'album: {album.name} ({album.album_type}) ({album.uri})',
          f'({album.release_date} {album.release_date_precision})',
          f'(tracks: {album.total_tracks})')
    print('\tartists: %s' % _artists_to_string(album.artists))

    if hasattr(album, 'album_group'):
        print(f'\talbum group: {album.album_group}')

    if album.available_markets is not None:
        if 0 < len(album.available_markets) < 10:
            print(f'\tmarkets: {len(album.available_markets)} ({list(album.available_markets)})')
        else:
            print(f'\tmarkets: {len(album.available_markets)}')
    if album.is_playable is not None:
        print(f'\tplayable: {album.is_playable}')


@printer.register
def print_album_full(album: FullAlbum):
    '''print album'''
    print('album: {album.name} ({album.album_type}) ({album.uri})'.format(album=album),
          '({album.release_date} {album.release_date_precision})'.format(album=album),
          '(popularity: {album.popularity}, tracks: {album.total_tracks})'.format(album=album))
    print('\tartists: %s' % _artists_to_string(album.artists))

    if hasattr(album, 'album_group'):
        if album.album_group and album.album_group != album.album_type:
            print(f'\talbum group: {album.album_group}')

    if album.genres:
        print('\tgenres: {album.genres}'.format(album=album))
    if album.external_ids:
        print('\texternal ids: {album.external_ids}'.format(album=album))
    if album.external_urls:
        print('\texternal urls: {album.external_urls}'.format(album=album))
    if album.available_markets is not None:
        if 0 < len(album.available_markets) < 10:
            print(f'\tmarkets: {len(album.available_markets)} ({list(album.available_markets)})')
        else:
            print(f'\tmarkets: {len(album.available_markets)}')
    if album.label:
        print('\tlabel: {album.label}'.format(album=album))
    if album.copyrights:
        print('\tcopyrights:')
        for copyright in album.copyrights:
            print(f'\t\t{copyright.type}: {copyright.text}')

    album_dict = album.dict()
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
    spotify_history = _get_spotify_history()
    artist_played_info = spotify_history.count_by_artist_name_with_timestamps(artist.name)
    if artist_played_info.count >= 1:
        print(f'\tplayed: {artist_played_info.count}',
              f'({artist_played_info.min.date()} - {artist_played_info.max.date()})')


@printer.register
def print_playlist(playlist: Playlist):
    print(f'playlist: {playlist.name} ({playlist.uri})')

    if playlist.owner:
        print(f'\towner: {playlist.owner.display_name} ({playlist.owner.uri})')

    if playlist.description:
        print(f'\tdesc: {playlist.description}')

    if hasattr(playlist, 'tracks'):
        print(f'\ttracks: {playlist.tracks.total}')

    if playlist.primary_color:
        print(f'\tprimary color: {playlist.primary_color}')

    playlist_dict = playlist.dict()
    flags = _get_flags(playlist_dict, ['public', 'collaborative'])
    if flags:
        print(f'\tflags: {flags}')

    # only on FullPlaylist
    if hasattr(playlist, 'followers'):
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

    plt_dict = plt.dict()
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

    disallows_dict = cp.actions.disallows.dict()
    disallows = _get_flags(disallows_dict, disallows_dict.keys())
    print(f'\tactions disallows: {disallows}')
    print()
    # if cp.item:
    #     printer(cp.item)

# TODO: combine cpt and cpc handing
@printer.register
def print_currently_playing_context(cpc: CurrentlyPlayingContext):
    print(f'currently playing context: playing {cpc.is_playing}')
    # TODO add smart_shuffle
    print(f'\tstate: repeat: {cpc.repeat_state}, shuffle: {cpc.shuffle_state}')
    print(f'\ttype: {cpc.currently_playing_type.name}')

    if cpc.context:
        print(f'\tcontext: {cpc.context.type.name} ({cpc.context.uri})')

    cpc_timestamp = datetime.datetime.fromtimestamp(cpc.timestamp/1000.0)
    print('\ttimestamp: %s (%s)' % (
            humanize.naturaldate(cpc_timestamp),
            humanize.naturaltime(datetime.datetime.now() - cpc_timestamp)))
    print('\tprogress: %s' % datetime.timedelta(milliseconds=cpc.progress_ms))

    disallows_dict = ccp.actions.disallows.dict()
    disallows = _get_flags(disallows_dict, disallows_dict.keys())
    print(f'\tactions disallows: {disallows}')

    printer(cpc.device)
    
@printer.register
def print_device(device: Device):
    print(f'device: {device.name} ({device.id})')
    print(f'\ttype: {device.type},',
          f'is_active: {device.is_active},',
          f'is_private_session: {device.is_private_session},',
          f'is_restricted: {device.is_restricted}')
    print(f'\tvolume_percent: {device.volume_percent}')

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

    track_dict = track.dict()
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
    print(f'\tlanguages: {list(episode.languages)}')
    print(f'\tresume point: {episode.resume_point.asbuiltin()}')

    print(f'\tdescription:')
    print(textwrap.TextWrapper(
        width=70,
        initial_indent='\t\t',
        subsequent_indent='\t\t'
        ).fill(episode.description))

    if episode.external_urls:
        print(f'\texternal urls: {episode.external_urls}')

    episode_dict = episode.dict()
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
    print(f'\tlanguages: {list(show.languages)}')

    if hasattr(show, 'episodes'):
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

    show_dict = show.dict()
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
