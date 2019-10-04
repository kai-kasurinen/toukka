#

"""Pandas loves Spotify"""

import pandas

from toukka.hub import Toukka
from toukka.utils import json_dump, json_dump_print


def panda_playlist(uri):
    """experimental pandas"""

    toukka = Toukka()
    playlist = toukka.sp.get_playlist_by_uri(uri)
    playlist_tracks = toukka.sp.aggregate_paging_results(playlist['tracks'])

    tracks = []
    for playlist_track in playlist_tracks:
        track = playlist_track['track']
        tracks.append(
            {
                "artist": track['artists'][0]['name'],
                "name": track['name'],
                "uri": track['uri']
            })


    data = pandas.DataFrame(tracks)
    print(data)


#COMMANDS = [panda_playlist]
COMMANDS = []

# END
