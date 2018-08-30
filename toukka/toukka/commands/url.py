#


from urlobject import URLObject

from toukka import Toukka


def parse_url(url_string):
    url = URLObject(url_string)
    print(url)
    print(url.path.segments)

    if url.hostname == 'musicbrainz.org':
        print('is musicbrainz')
        print('type %s' % url.path.segments[0])
        print('id %s' % url.path.segments[1])
    elif self.url.hostname == 'discogs.com':
        print('is discogs')
    else:
        print('is unknown')


COMMANDS = [parse_url]
