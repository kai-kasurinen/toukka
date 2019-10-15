#

'''spotify artist commands'''

import argh
import spotipy

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer import first as printer

# from toukka.hub import Toukka
# from toukka.util import json_dump, json_dump_print


def artist_info(uri):
    '''get artist info'''
    spotify = get_spotify()
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    artist = spotify.artist(uri_id)
    printer.print_artist(artist)


def artist_albums(uri):
    '''get artist albums'''
    spotify = get_spotify()
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    # FIXME: got type error with default market
    paging = spotify.artist_albums(uri_id, market='FI')

    for album in spotify.all_items_from_paging(paging):
        # FIXME: on items albums are simple and printer only supports full
        # FIXME: we lose album group
        album_full = spotify.album(album.id)
        print()
        # FIXME: print oneline
        printer.print_album(album_full)

    '''
    grouped = False
    if grouped:
        group_album = [a for a in albums if a.get('album_group') == 'album']
        group_single = [a for a in albums if a.get('album_group') == 'single']
        group_compilation = [a for a in albums if a.get('album_group') == 'compilation']
        group_appears_on = [a for a in albums if a.get('album_group') == 'appears_on']
    '''


def artist_top_tracks(uri, country='FI'):
    '''get artist top tracks'''
    spotify = get_spotify()
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    tracks = spotify.artist_top_tracks(uri_id, country=country)
    printer.print_tracks(tracks)


def artist_related_artists(uri):
    '''get artist related artists'''
    spotify = get_spotify()
    uri_type, uri_id = spotipy.convert.from_uri(uri)
    artists = spotify.artist_related_artists(uri_id)
    printer.print_artists(artists)


#

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
