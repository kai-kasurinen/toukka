#

'''spotify player control commands'''

import argh

#from toukka.hub import Toukka
#from toukka.util import json_dump

from toukka.sopiva.spotify.util import get_spotify


def play(uri=None, offset=None, uris=None, device=None):
    ''' Start or resume user's playback.'''
    toukka = Toukka()
    return json_dump(toukka.sp.start_playback(context_uri=uri,
                                              uris=uris,
                                              offset=offset,
                                              device_id=device))


def pause(device=None):
    ''' Pause user's playback.'''
    toukka = Toukka()
    return json_dump(toukka.sp.pause_playback(device_id=device))


@argh.aliases('next')
def next_track(device=None):
    ''' Skip user's playback to next track.'''
    toukka = Toukka()
    return json_dump(toukka.sp.next_track(device_id=device))


@argh.aliases('prev')
def previous_track(device=None):
    ''' Skip user's playback to previous track.'''
    toukka = Toukka()
    return json_dump(toukka.sp.previous_track(device_id=device))


def seek(position: 'position in milliseconds to seek to', device=None):
    ''' Seek to position in current track.'''
    toukka = Toukka()
    return json_dump(toukka.sp.seek_track(position, device_id=device))


def repeat(state: '`track`, `context`, or `off`', device=None):
    ''' Set repeat mode for playback.'''
    toukka = Toukka()
    return json_dump(toukka.sp.repeat(state, device_id=device))


def volume(percent: 'volume between 0 and 100', device=None):
    ''' Set playback volume.'''
    toukka = Toukka()
    return json_dump(toukka.sp.volume(int(percent), device_id=device))


def shuffle(state, device=None):
    ''' Toggle playback shuffling.'''
    toukka = Toukka()
    return json_dump(toukka.sp.shuffle(state, device_id=device))


def devices():
    ''' Get a list of user's available devices.'''
    toukka = Toukka()
    return json_dump(toukka.sp.devices())


def current_playback(market=None):
    ''' Get information about user's current playback.'''
    toukka = Toukka()
    return json_dump(toukka.sp.current_playback(market))


def currently_playing(market=None):
    ''' Get user's currently playing track.'''
    return get_spotify().playback_currently_playing(market=None).pprint(depth=2)


def transfer_playback(device, force_play=True):
    ''' Transfer playback to another device.'''
    toukka = Toukka()
    return json_dump(toukka.sp.transfer_playback(device, force_play=force_play))


COMMANDS = [play,
            pause,
            next_track,
            previous_track,
            seek,
            repeat,
            volume,
            shuffle,
            devices,
            current_playback,
            currently_playing,
            transfer_playback]
