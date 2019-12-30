#

'''spotify player control commands'''

import click

from typing import Union

from toukka.sopiva.spotify.util import get_spotify
from toukka.sopiva.spotify.printer.first import printer
from toukka.sopiva.spotify.cli import cli_root

# NOTE: most of current player commands needs premium account
# NOTE: .. so not tested


@cli_root.group()
def playback():
    pass


@playback.command()
@click.option('--context-uri')
@click.option('--track-ids')
@click.option('--offset')
@click.option('--position-ms')
@click.option('--device-id')
def start(context_uri: str = None,
          track_ids: list = None,
          offset: Union[int, str] = None,
          position_ms: int = None,
          device_id: str = None
          ):
    return get_spotify().playback_start(**locals())


@playback.command()
@click.option('--device-id')
def pause(device_id=None):
    return get_spotify().playback_pause(**locals())


@playback.command()
@click.option('--device-id')
def resume(device_id=None):
    return get_spotify().playback_resume(**locals())


@playback.command()
@click.option('--device-id')
def next(device_id=None):
    return get_spotify().playback_next(**locals())


@playback.command()
@click.option('--device-id')
def previous(device_id=None):
    return get_spotify().playback_next(**locals())


@playback.command()
@click.argument('position_ms')
@click.option('--device-id')
def seek(position_ms: int, device_id=None):
    return get_spotify().playback_seek(locals())


@playback.command()
@click.argument('state')
@click.option('--device-id')
def repeat(state: str, device_id=None):
    return get_spotify().playback_repeat(**locals())


@playback.command()
@click.argument('percent')
@click.option('--device-id')
def volume(percent: int, device_id=None):
    return get_spotify().playback_volume(locals())


@playback.command()
@click.argument('state')
@click.option('--device-id')
def shuffle(state: bool, device_id=None):
    return get_spotify().playback_shuffle(state, device_id=device_id)


@playback.command()
def devices():
    printer(get_spotify().playback_devices())


@playback.command()
def current_playback(market=None):
    printer(get_spotify().playback(**locals()))


@playback.command()
def currently_playing(market=None):
    ''' Get user's currently playing track.'''
    spotify = get_spotify()
    playing = spotify.playback_currently_playing(market=market)
    printer(playing)


@playback.command()
@click.option('--device-id')
def transfer_playback(device_id, force_play: bool = False):
    return get_spotify().playback_transfer(device_id, force_play=force_play)


@playback.command()
def recently_played():
    spotify = get_spotify()
    paging = spotify.playback_recently_played()
    for played in spotify.all_items(paging):
        printer(played)
# END
