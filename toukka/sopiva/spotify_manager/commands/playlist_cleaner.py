#

import logging
import click
import spotipy.convert
import enlighten

import toukka.sopiva.spotify.util
import toukka.sopiva.spotify_history.util

from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify_manager.cli import cli_root

logger = logging.getLogger(__name__)


@cli_root.command()
@click.argument('uri')
@click.option('--filter-played-tracks', is_flag=True, default=False)
@click.option('--filter-played-isrcs', is_flag=True, default=False)
@click.option('--filter-duplicate-isrc', is_flag=True, default=False)
@click.option('--filter-not-playable', is_flag=True, default=False)
@click.option('--remove-tracks', is_flag=True, default=False)
@click.option('--progress-bar', is_flag=True, default=False)
def playlist_cleaner(uri: str,
                     remove_tracks: bool = False,
                     filter_played_tracks: bool = False,
                     filter_played_isrcs: bool = False,
                     filter_duplicate_isrc: bool = False,
                     filter_not_playable: bool = False,
                     progress_bar: bool = False
                     ):
    '''clean playlist'''

    if uri == 'current':
        uri_current = _playlist_current()
        if uri_current:
            uri = uri_current
        else:
            raise click.ClickException('not currently playing playlist?')

    uri_type, uri_id = spotipy.convert.from_uri(uri)

    spotify = toukka.sopiva.spotify.util.get_spotify()
    spotify_history = toukka.sopiva.spotify_history.util.get_spotify_history()
    market = spotify.current_user().country
    tracks_to_remove = set()
    isrcs = set()

    playlist = spotify.playlist(playlist_id=uri_id, market=market)
    printer(playlist)

    playlist_tracks = spotify.all_items_from_paging(playlist.tracks)

    enlighten_manager = enlighten.get_manager(enabled=progress_bar)
    progress_tracks = enlighten_manager.counter(
        desc='Playlist Tracks', unit='tracks',
        total=playlist.tracks.total,
        color='green')

    # main loop for doing things
    for playlist_track in playlist_tracks:
        track = playlist_track.track
        isrc = track.external_ids.get('isrc')

        if filter_not_playable:
            if track.is_playable is False:
                logger.info(f'{track.uri}: not playable')
                tracks_to_remove.add(track.id)

        if filter_duplicate_isrc and isrc is not None:
            if isrc in isrcs:
                logger.info(f'{track.uri}: isrc {isrc} is already seen')
                tracks_to_remove.add(track.id)
            else:
                isrcs.add(isrc)

        if filter_played_tracks:
            played_count = spotify_history.count_by_track_id(track.uri)
            if played_count > 0:
                logger.info(f'{track.uri}: played {played_count} times')
                tracks_to_remove.add(track.id)

        if filter_played_isrcs and isrc is not None:
            played_count_isrc = spotify_history.count_by_track_isrc(isrc)
            if played_count_isrc > 0:
                logger.info(f'{track.uri}: {isrc} played {played_count_isrc} times')
                tracks_to_remove.add(track.id)
        progress_tracks.update()

    logger.info(f'{playlist.tracks.total} total tracks')
    logger.info(f'{len(tracks_to_remove)} tracks remove')

    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    if remove_tracks:
        progress_remove = enlighten_manager.counter(
            desc='Remove Tracks', unit='tracks',
            total=playlist.tracks.total,
            color='red')
        tracks_to_remove_list = list(tracks_to_remove)
        snapshot_id = playlist.snapshot_id

        for chunk in chunks(tracks_to_remove_list, 100):
            logger.info(f'removing {len(chunk)} tracks')
            snapshot_id = spotify.playlist_tracks_remove(
                playlist_id=playlist.id,
                track_ids=chunk,
                snapshot_id=snapshot_id)
            logger.info(f'new snapshot id: {snapshot_id}')
            progress_remove.update()
    else:
        logger.info(f'remove-tracks not enabled')
    # grii
    enlighten_manager.stop()


def _playlist_current():
    '''get currently playing playlist'''

    # FIXME: do not init spotifys
    spotify = toukka.sopiva.spotify.util.get_spotify()
    playing = spotify.playback_currently_playing()

    if playing.context and playing.context.type.name == 'playlist':
        uri = playing.context.uri
        username = uri.split(':')[2]
        playlist_id = uri.split(':')[4]
        new_uri = spotipy.convert.to_uri('playlist', playlist_id)
        return new_uri
    else:
        return False


# END
