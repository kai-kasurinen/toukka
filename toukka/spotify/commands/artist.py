#

'''spotify artist commands'''

import argh

from toukka import Toukka
from toukka.utils import json_dump, json_dump_print


def artist_info(uri):
    '''Get artist info'''
    toukka = Toukka()
    artist = toukka.sp.artist(uri)
    _print_artist(artist)


def artist_albums(uri, album_type=None, country=None):
    '''Get artist albums'''
    toukka = Toukka()
    paging = toukka.sp.artist_albums(uri)
    albums = toukka.sp.aggregate_paging_results(paging)

    grouped = False
    if grouped:
        group_album = [a for a in albums if a.get('album_group') == 'album']
        group_single = [a for a in albums if a.get('album_group') == 'single']
        group_compilation = [a for a in albums if a.get('album_group') == 'compilation']
        group_appears_on = [a for a in albums if a.get('album_group') == 'appears_on']

    _print_albums(albums)


def artist_top_tracks(uri, country='FI'):
    '''Get artist top tracks'''
    toukka = Toukka()
    results = toukka.sp.artist_top_tracks(uri)
    tracks = results.get('tracks')
    _print_tracks(tracks)


def artist_related_artists(uri):
    '''Get artist related artists'''
    toukka = Toukka()
    results = toukka.sp.artist_related_artists(uri)
    artists = results.get('artists')
    _print_artists(artists)


def _print_artists(artists):
    for artist in artists:
        _print_artist_oneline(artist)


def _print_artist(artist):

    print('name: {name}'.format(**artist))
    print('uri: {uri}'.format(**artist))
    print('genres: {genres}'.format(**artist))
    print('popularity: {popularity}'.format(**artist))
    print('followers: {followers[total]}'.format(**artist))

    if artist.get('external_urls'):
        for name, url in artist.get('external_urls').items():
            print('{name}: {url}'.format(name=name, url=url))


def _print_artist_oneline(artist):
    print('name: {name:30}, uri: {uri:30}, popularity: {popularity:3}, followers: {followers[total]:10}, genres: {genres}'.format(**artist))


def _print_albums(albums):
    for album in albums:
        _print_album_multiline(album)


def _print_album_multiline(album):
    print('name: {name}'.format(**album))
    print('artists: {artists_string}'.format(
        artists_string=_get_string_from_artists(album.get('artists'))))
    print('uri: {uri}'.format(**album))
    print('type: {album_type}'.format(**album))
    print('group: {album_group}'.format(**album))
    print()


def _print_tracks(tracks):
    for track in tracks:
        _print_track_oneline(track)


def _print_track_oneline(track):
    print('name: {name:40}, uri: {uri:30}, artists: {artists_string:40}, album: {album[name]}'.format(**track, artists_string=_get_string_from_artists(track.get('artists'))))


def _get_string_from_artists(artists):
    return ', '.join('%s' % (artist.get('name')) for artist in artists)


#


COMMANDS = [artist_info,
            artist_albums,
            artist_top_tracks,
            artist_related_artists]

# END
