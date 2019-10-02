#

import pprint
import argh
from .. import MusicBrainzSearch


def search_artist(query):
    search = MusicBrainzSearch()
    return pprint.pformat(search.artist(query))


def search_release(query):
    search = MusicBrainzSearch()
    return pprint.pformat(search.release(query))


def search_recording(query):
    search = MusicBrainzSearch()
    return pprint.pformat(search.recording(query))


def search_track(query):
    search = MusicBrainzSearch()
    return pprint.pformat(search.track(query))


def search_url(query):
    search = MusicBrainzSearch()
    return pprint.pformat(search.url(query))


COMMANDS = [
    search_artist,
    search_release,
    search_recording,
    search_track,
    search_url]

# END
