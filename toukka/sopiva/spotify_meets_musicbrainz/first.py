#

import toukka.sopiva.spotify.printer.first

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.metabrainz import musicbrainzngs
from toukka.printer.first import printer


def print_currently_listening():
    spotify = get_spotify()

    currently_playing = spotify.playback_currently_playing()

    if currently_playing.currently_playing_type.name == 'track':
        track = currently_playing.item

    printer(track)
    printer(track.album)
    for artist in track.artists:
        printer(artist)
