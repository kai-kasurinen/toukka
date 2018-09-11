#

import re

# https://github.com/ybayle/ISRC/blob/master/isrc.py#L146
def is_isrc_valid(isrc):
    """Description of validISRC
    Return True if isrc provided is valid, False otherwise
    TODOs
        Take into account ISO 3166-1 alpha 2 Code defined by
        http://isrc.ifpi.org/downloads/ISRC_Bulletin-2015-01.pdf
    """
    if len(isrc) == 12:
        pattern = re.compile("[a-zA-Z]{2}[a-zA-Z0-9]{3}[0-9]{7}")
        if pattern.match(isrc):
            return True
            # year checking, bad year not make isrc invalid
            # example: TCADU1828857
            #
            #int_isrc = int(isrc[5:7])
            #if int_isrc >= 40 or int_isrc <= 16:
            #    return True
    return False

