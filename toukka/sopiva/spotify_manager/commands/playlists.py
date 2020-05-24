#

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
    playlists = spotify.all_items(paging)

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


def _print_playlists(playlists, one_line=True):
    # FIXME
    if one_line:
        line = 'id: {id} name: {name:40}  owner: {owner[id]:30} tracks: {tracks[total]:5} flags: {flags}'
    else:
        line = 'name: {name}\nid: {id}\nowner: {owner[id]}\nflags: {flags}\ntracks: {tracks[total]}\n'

    for playlist in playlists:
        playlist.pprint()
        print(line.format(
            **playlist,
            flags=_list_to_string(_get_flags(playlist, ['public', 'collaborative']))))


#

COMMANDS = [
    playlists]

# END
