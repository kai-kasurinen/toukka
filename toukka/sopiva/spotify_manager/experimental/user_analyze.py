#

import logging

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def analyze_user_1(**kwargs):

    spotify = get_spotify()

    user = spotify.current_user()
    printer(user)

    playlists_paging = spotify.followed_playlists()
    print(f'user has {playlists_paging.total} playlists')

    playlists = spotify.all_items(playlists_paging)

    intresting_playlists = dict()

    for playlist in playlists:
        if playlist.owner.id == user.id:
            continue

        if playlist.owner.id == 'spotify':
            if playlist.name.startswith('Daily Mix'):
                logger.debug('found: %s', playlist.name)
                intresting_playlists[playlist.name] = playlist
            if playlist.name.startswith('Your Top Songs'):
                logger.debug('found: %s', playlist.name)
                intresting_playlists[playlist.name] = playlist
            if playlist.name == 'Discover Weekly':
                logger.debug('found: %s', playlist.name)
                intresting_playlists[playlist.name] = playlist
            if playlist.name == 'Release Radar':
                logger.debug('found: %s', playlist.name)
                intresting_playlists[playlist.name] = playlist
            if playlist.name == 'Repeat Rewind':
                logger.debug('found: %s', playlist.name)
                intresting_playlists[playlist.name] = playlist
            if playlist.name == 'On Repeat':
                logger.debug('found: %s', playlist.name)
                intresting_playlists[playlist.name] = playlist
            if playlist.name == 'Tastebreakers':
                logger.debug('found: %s', playlist.name)
                intresting_playlists[playlist.name] = playlist




# END
