#

import pprint
import argh
from toukka.toukka import Toukka
from musicbrainzngs import VALID_INCLUDES

def get_area_by_id(area_id):
    '''get area by id'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_area_by_id(area_id)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_artist_by_id(artist_id):
    '''get artist by id'''
    toukka = Toukka()
    includes = ['aliases', 'annotation', 'tags', 'ratings']
    try:
        result = toukka.mbngs.get_artist_by_id(artist_id, includes=includes)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_event_by_id(event_id):
    '''get event by id'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_event_by_id(event_id)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_instrument_by_id(instrument_id):
    '''get instrument by id'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_instrument_by_id(instrument_id)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_label_by_id(label_id):
    '''get label by id'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_instrument_by_id(label_id)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_place_by_id(place_id):
    '''get place by id'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_place_by_id(place_id)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)



def get_recording_by_id(recording_id):
    '''get recording by id'''
    toukka = Toukka()
    includes = [
        'artists',
        'releases',
        'discids',
        'media',
        'artist-credits',
        'isrcs',
        'annotation',
        'aliases',
        'tags',
        #'user-tags',
        'ratings',
        #'user-ratings',
        'area-rels',
        'artist-rels',
        'label-rels',
        'place-rels',
        'event-rels',
        'recording-rels',
        'release-rels',
        'release-group-rels',
        'series-rels',
        'url-rels',
        'work-rels',
        'instrument-rels']

    try:
        result = toukka.mbngs.get_recording_by_id(recording_id, includes=includes)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_recordings_by_isrc(isrc):
    '''get recording by isrc'''
    toukka = Toukka()
    includes = ['artists']
    try:
        result = toukka.mbngs.get_recordings_by_isrc(isrc, includes=includes)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_release_group_by_id(release_group_id):
    '''get release group by id'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_release_group_by_id(release_group_id)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_release_by_id(release_id):
    '''get release by id'''
    toukka = Toukka()
    includes = _get_includes('release')
    try:
        result = toukka.mbngs.get_release_by_id(release_id, includes=includes)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_releases_by_discid(discid):
    '''get releases by discid'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_releases_by_discid(discid)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_series_by_id(series_id):
    '''get series by id'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_series_by_id(series_id)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_work_by_id(work_id):
    '''get work by id'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_work_by_id(work_id)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_works_by_iswc(iswc):
    '''get works by iswc'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_works_by_iswc(iswc)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_url_by_id(iid):
    '''get url by id'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_url_by_id(iid)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_collections():
    '''get collections'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_collections()
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


def get_releases_in_collection(collection):
    '''get releases in collection'''
    toukka = Toukka()
    try:
        result = toukka.mbngs.get_get_releases_in_collection(collection)
    except toukka.mbngs.ResponseError as error:
        raise argh.CommandError(error)
    pprint.pprint(result)


###


def show_release_details(rel):
    """Print some details about a release dictionary to stdout.
    """
    # "artist-credit-phrase" is a flat string of the credited artists
    # joined with " + " or whatever is given by the server.
    # You can also work with the "artist-credit" list manually.
    print("{}, by {}".format(rel['title'], rel["artist-credit-phrase"]))
    if 'date' in rel:
        print("Released {} ({})".format(rel['date'], rel['status']))
    print("MusicBrainz ID: {}".format(rel['id']))


def search_release(artist, album):
    """"""
    toukka = Toukka()

    # Keyword arguments to the "search_*" functions limit keywords to
    # specific fields. The "limit" keyword argument is special (like as
    # "offset", not shown here) and specifies the number of results to
    # return.
    result = toukka.mbngs.search_releases(artist=artist, release=album,
                                            limit=5)
    # On success, result is a dictionary with a single key:
    # "release-list", which is a list of dictionaries.
    if not result.get('release-list'):
        print('no release found')
    for (idx, release) in enumerate(result.get('release-list')):
        print("match #{}:".format(idx+1))
        show_release_details(release)
        print()


def _get_includes(ent):
    i = VALID_INCLUDES.get(ent)
    try:
        i.remove('user-tags')
        i.remove('user-ratings')
    except ValueError:
        pass
    return i

#

COMMANDS = [
    get_area_by_id,
    get_artist_by_id,
    get_event_by_id,
    get_instrument_by_id,
    get_label_by_id,
    get_place_by_id,
    get_recording_by_id,
    get_recordings_by_isrc,
    get_release_group_by_id,
    get_release_by_id,
    get_releases_by_discid,
    get_series_by_id,
    get_work_by_id,
    get_works_by_iswc,
    get_url_by_id,
    get_collections,
    get_releases_in_collection,
    search_release]

# END
