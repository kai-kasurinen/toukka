#

from toukka.toukka import Toukka


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
    result = toukka.mb.search_releases(artist=artist, release=album,
                                            limit=5)
    # On success, result is a dictionary with a single key:
    # "release-list", which is a list of dictionaries.
    if not result.get('release-list'):
        print('no release found')
    for (idx, release) in enumerate(result.get('release-list')):
        print("match #{}:".format(idx+1))
        show_release_details(release)
        print()


#

COMMANDS = [search_release]

# END
