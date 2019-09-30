#

import datetime
import dataclasses

from .. import toukkain


def print_track(track, use_play_count=True):
    print('track: {track.name} ({track.uri}) (popularity: {track.popularity})'.format(track=track))

    print('\talbum: {track.album.name} ({track.album.uri})'.format(track=track))
    print('\tartists: %s' % _artists_to_string(track.artists))
    print('\tduration: %s' % (datetime.timedelta(milliseconds=track.duration_ms)))
    print('\ttrack number: {track.track_number}, disc number: {track.disc_number}'.format(track=track))

    if track.external_ids:
        print('\texternal ids: {track.external_ids}'.format(track=track))
    if track.external_urls:
        print('\texternal urls: {track.external_urls}'.format(track=track))
    if track.available_markets:
        print('\tmarkets: %s' % (len(track.available_markets)))
    if track.linked_from:
        print('\tlinked from: {track.linked_from}'.format(track=track))
    if track.restrictions:
        print('\trestrictions: {track.restrictions}'.format(track=track))

    flags = _get_flags(dataclasses.asdict(track), ['explicit', 'is_playable', 'is_local'])
    if flags:
        print('\tflags: %s' % flags)

    if use_play_count:
        spotify_history = toukkain.get_spotify_history_object()
        print('\tplayed: %s' % spotify_history.count_by_track_id(track.uri))


def print_album(album):
    # FIXME: needs FullAlbum
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
        for copyright in album.copyrights:
            print('\t\t{copyright.type}: {copyright.text}'.format(copyright=copyright))


def print_artist(artist, use_play_count=True):
    print('artist: {artist.name} ({artist.uri})'.format(artist=artist),
          '(popularity: {artist.popularity},'.format(artist=artist),
          'followers: {artist.followers.total})'.format(artist=artist))

    if artist.genres:
        print('\tgenres: {artist.genres}'.format(artist=artist))
    if artist.external_urls:
        print('\texternal urls: {artist.external_urls}'.format(artist=artist))

    if use_play_count:
        spotify_history = toukkain.get_spotify_history_object()
        print('\tplayed: %s' % spotify_history.count_by_artist_name(artist.name))


def _artists_to_string(artists):
    return ", ".join("%s (%s)" % (artist.name, artist.uri) for artist in artists)


# from toukka.utils.misc_utils
def _get_flags(_dict, _needed):
    return [key for key, value in _dict.items() if key in _needed and value is True]
