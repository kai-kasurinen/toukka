#

import musicbrainzngs


class MusicBrainz:
    def __init__(self):
        self.mb = musicbrainzngs
        self.mb.set_useragent('invalid', '0')
