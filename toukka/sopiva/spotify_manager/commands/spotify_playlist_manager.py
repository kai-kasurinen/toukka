#

import spotipy.convert

from toukka.util import _get_flags, _list_to_string
from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer import first as printer
from toukka.sopiva.spotify_history.util import get_spotify_history


def playlists(
        user=None,
        filter_own: bool = False,
        filter_public: bool = False,
        filter_collaborative: bool = False,
        filter_by_userid: bool = None
        ):
    '''get user playlists'''

    spotify = get_spotify()
    paging = spotify.playlists()

    print(f'user has {paging.total} playlists')
    playlists = spotify.all_items_from_paging(paging)

    # FIXME:
    '''
    if filter_own:
        playlists = [p for p in playlists if p.get('owner').get('id') == user]

    if filter_public:
        playlists = [p for p in playlists if p.get('public') is True]

    if filter_collaborative:
        playlists = [p for p in playlists if p.get('collaborative') is True]

    if filter_by_userid:
        playlists = [p for p in playlists if p.get('owner').get('id') == filter_by_userid]

    _print_playlists(playlists, one_line=True)
    print('\nfiltered to {} of total {}'.format(len(playlists), total))
    '''


'''
def _print_playlists(playlists, one_line=True):

    if one_line:
        line = 'id: {id} name: {name:40}  owner: {owner[id]:30} tracks: {tracks[total]:5} flags: {flags}'
    else:
        line = 'name: {name}\nid: {id}\nowner: {owner[id]}\nflags: {flags}\ntracks: {tracks[total]}\n'

    for playlist in playlists:
        pprint.pprint(playlist)
        print(line.format(
            **playlist,
            flags=_list_to_string(_get_flags(playlist, ['public', 'collaborative']))))
'''


def playlist(uri: str,
             remove_played_tracks: bool = False
             ):
    '''get and modify playlist'''

    uri_type, uri_id = spotipy.convert.from_uri(uri)

    spotify = get_spotify()
    spotify_history = get_spotify_history()

    playlist = spotify.playlist(playlist_id=uri_id, market=None)
    playlist.pprint(depth=2)

    playlist_tracks = spotify.all_items_from_paging(playlist.tracks)

    played_tracks = set()
    for playlist_track in playlist_tracks:
        track = playlist_track.track
        played_count = spotify_history.count_by_track_id(track.uri)

        if played_count > 0:
            print(f'{track.uri} played {played_count} times')
            played_tracks.add(track.id)

    print(f'{playlist.tracks.total} total tracks')
    print(f'{len(played_tracks)} already played tracks')

    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    if remove_played_tracks:
        played_tracks_list = list(played_tracks)
        snapshot_id = playlist.snapshot_id

        for chunk in chunks(played_tracks_list, 100):
            print(f'removing {len(chunk)} tracks')
            snapshot_id = spotify.playlist_tracks_remove(
                playlist_id=playlist.id,
                track_ids=chunk,
                snapshot_id=snapshot_id)
            print(f'new snapshot id: {snapshot_id}')


#

COMMANDS = [
    playlist,
    playlists]

# END
