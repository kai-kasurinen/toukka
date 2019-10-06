#

import argh
import spotipy.convert

import toukka.sopiva.spotify.util
import toukka.sopiva.spotify_history.util
import toukka.sopiva.spotify_manager.database.track_to_isrc


def playlist_cleaner(uri: str,
                     remove_tracks: bool = False,
                     filter_played_tracks: bool = False,
                     filter_played_isrcs: bool = False,
                     filter_duplicate_isrc: bool = False,
                     filter_not_playable: bool = False
                     ):
    '''clean playlist'''

    if uri == 'current':
        uri_current = _playlist_current()
        if uri_current:
            uri = uri_current
        else:
            raise argh.exceptions.CommandError('not currently playing playlist?')

    uri_type, uri_id = spotipy.convert.from_uri(uri)

    spotify = toukka.sopiva.spotify.util.get_spotify()
    spotify_history = toukka.sopiva.spotify_history.util.get_spotify_history()

    # NOTE: not setting market, we should get market from token and relinking information
    #       but it fails with TypeError
    playlist = spotify.playlist(playlist_id=uri_id, market=None)
    playlist.pprint(depth=2)

    # NOTE: make list from iterable
    playlist_tracks = list(spotify.all_items_from_paging(playlist.tracks))
    tracks_to_remove = set()

    # prepare for main loop
    isrcs = set()
    # FIXME: SLOW
    isrcs_played = toukka.sopiva.spotify_manager.database.track_to_isrc.get_listened_isrcs()

    # main loop for doing things
    for playlist_track in playlist_tracks:
        track = playlist_track.track

        # NOTE: not work when market is None
        if filter_not_playable:
            if track.is_playable is False:
                print(f'{track.uri}: not playable')
                tracks_to_remove.add(track.id)

        if filter_duplicate_isrc:
            isrc = track.external_ids.get('isrc')
            if isrc is None:
                continue
            if isrc in isrcs:
                print(f'{track.uri}: isrc {isrc} is already seen')
                tracks_to_remove.add(track.id)
            else:
                isrcs.add(isrc)

        if filter_played_tracks:
            played_count = spotify_history.count_by_track_id(track.uri)
            if played_count > 0:
                print(f'{track.uri}: played {played_count} times')
                tracks_to_remove.add(track.id)

        if filter_played_isrcs:
            isrc = track.external_ids.get('isrc')
            if isrc is None:
                continue
            if isrc in isrcs_played:
                print(f'{track.uri}: isrc {isrc} is already played')
                tracks_to_remove.add(track.id)

    print(f'{playlist.tracks.total} total tracks')
    print(f'{len(tracks_to_remove)} tracks remove')

    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    if remove_tracks:
        tracks_to_remove_list = list(tracks_to_remove)
        snapshot_id = playlist.snapshot_id

        for chunk in chunks(tracks_to_remove_list, 100):
            print(f'removing {len(chunk)} tracks')
            snapshot_id = spotify.playlist_tracks_remove(
                playlist_id=playlist.id,
                track_ids=chunk,
                snapshot_id=snapshot_id)
            print(f'new snapshot id: {snapshot_id}')


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


#

COMMANDS = [
    playlist_cleaner,
    ]

# END
