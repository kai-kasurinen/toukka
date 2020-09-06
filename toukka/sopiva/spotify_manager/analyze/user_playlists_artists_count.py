#

import collections

from toukka.sopiva.spotify.util import get_spotify


def user_playlists_artists_count():
    spotify = get_spotify()

    def count_artists(playlist_id: str):
        playlist_tracks = spotify.playlist_tracks(playlist_id)
        counter = collections.Counter()
        for playlist_track in spotify.all_items(playlist_tracks):
            if playlist_track.track is None:
                continue
            for artist in playlist_track.track.artists:
                counter += collections.Counter([artist.id])
        return counter

    def get_artist_counters() -> collections.Counter:
        playlists = spotify.followed_playlists()
        print(f'playlists count {playlists.total}')
        counter = collections.Counter()
        for playlist in spotify.all_items(playlists):
            counter += count_artists(playlist.id)
        print('all counts retrieved')
        return counter

    artists = get_artist_counters()

    for artist_id, count in artists.most_common(100):
        artist = spotify.artist(artist_id)
        print(count, artist.id, artist.name)


# END
