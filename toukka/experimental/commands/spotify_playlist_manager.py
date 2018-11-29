#

from toukka.utils import _get_flags, _list_to_string
from toukka.experimental.spotify.playlist_manager import Playlists

def playlists(user,
                   filter_own=False,
                   filter_public=False,
                   filter_collaborative=False,
                   filter_by_userid=None):


    playlists = Playlists().user_playlists_all(user)
    total = len(playlists)


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


def _print_playlists(playlists, one_line=True):

    if one_line:
        line = 'id: {id} name: {name:40}  owner: {owner[id]:30} tracks: {tracks[total]:5} flags: {flags}'
    else:
        line = 'name: {name}\nid: {id}\nowner: {owner[id]}\nflags: {flags}\ntracks: {tracks[total]}\n'

    for playlist in playlists:
        print(line.format(
            **playlist,
            flags=_list_to_string(_get_flags(playlist, ['public', 'collaborative']))))


# 

COMMANDS = [playlists]

# END
