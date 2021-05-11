#

import logging
import collections

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def analyze_user_1(**kwargs):

    spotify = get_spotify()

    user = spotify.current_user()
    printer(user)

    playlists_paging = spotify.followed_playlists()
    print(f'user has {playlists_paging.total} followed playlists')

    playlists = spotify.all_items(playlists_paging)

    users_counter = collections.Counter()
    intresting_playlists = dict()

    for playlist in playlists:
        users_counter[playlist.owner.id] += 1

        if playlist.owner.id == user.id:
            continue

        if playlist.owner.id == 'spotify':
            if playlist.name.startswith('Daily Mix'):
                intresting_playlists[playlist.name] = playlist
            elif playlist.name.startswith('Your Top Songs'):
                intresting_playlists[playlist.name] = playlist
            elif playlist.name == 'Discover Weekly':
                intresting_playlists[playlist.name] = playlist
            elif playlist.name == 'Release Radar':
                intresting_playlists[playlist.name] = playlist
            elif playlist.name == 'Repeat Rewind':
                intresting_playlists[playlist.name] = playlist
            elif playlist.name == 'On Repeat':
                intresting_playlists[playlist.name] = playlist
            elif playlist.name == 'Tastebreakers':
                intresting_playlists[playlist.name] = playlist
            elif playlist.name == 'Your Time Capsule':
                intresting_playlists[playlist.name] = playlist
            elif playlist.name == 'Missed Hits':
                intresting_playlists[playlist.name] = playlist
            elif playlist.name == 'Your Summer Rewind':
                intresting_playlists[playlist.name] = playlist
            else:
                logger.debug(f'unknown spotify playlist: {playlist.name} ({playlist.uri})')

    print(f'most common owners: {users_counter.most_common(4)}')

    for playlist_name, playlist in intresting_playlists.items():
        logger.debug(f'found: {playlist.name} ({playlist.uri})')


# END
