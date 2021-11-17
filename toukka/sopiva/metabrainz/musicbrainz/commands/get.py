#

import pprint
import click

from toukka.sopiva.metabrainz import musicbrainzngs
from toukka.printer.first import printer

from ..cli import cli_root


@cli_root.command()
@click.argument('mbid')
def get_area(mbid):
    printer(musicbrainzngs.get_area_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_artist(mbid):
    printer(musicbrainzngs.get_artist_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_event(mbid):
    printer(musicbrainzngs.get_event_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_instrument(mbid):
    printer(musicbrainzngs.get_instrument_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_label(mbid):
    printer(musicbrainzngs.get_label_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_place(mbid):
    printer(musicbrainzngs.get_place_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_recording(mbid):
    printer(musicbrainzngs.get_recording_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_release(mbid):
    printer(musicbrainzngs.get_release_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_release_group(mbid):
    printer(musicbrainzngs.get_release_group_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_series(mbid):
    printer(musicbrainzngs.get_series_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_work(mbid):
    printer(musicbrainzngs.get_work_by_id(mbid))


@cli_root.command()
@click.argument('mbid')
def get_url(mbid):
    printer(musicbrainzngs.get_url_by_id(mbid, includes=musicbrainzngs.VALID_INCLUDES.get('url')))


#

@cli_root.command()
@click.argument('discid')
def get_discid(discid):
    printer(musicbrainzngs.get_releases_by_discid(discid))


@cli_root.command()
@click.argument('isrc')
def get_isrc(isrc):
    printer(musicbrainzngs.get_recordings_by_isrc(isrc))


@cli_root.command()
@click.argument('iswc')
def get_iswc(iswc):
    printer(musicbrainzngs.get_works_by_iswc(iswc))


# END
