# This file is part of the musicbrainzngs library
# Copyright (C) Alastair Porter, Adrian Sampson, and others
# This file is distributed under a BSD-2-Clause type license.
# See the COPYING file for more information.


LUCENE_SPECIAL = r'([+\-&|!(){}\[\]\^"~*?:\\\/])'

# Constants for validation.

RELATABLE_TYPES = ['area', 'artist', 'label', 'place', 'event', 'recording', 'release', 'release-group', 'series', 'url', 'work', 'instrument']
RELATION_INCLUDES = [entity + '-rels' for entity in RELATABLE_TYPES]
TAG_INCLUDES = ["tags", "user-tags"]
RATING_INCLUDES = ["ratings", "user-ratings"]

VALID_INCLUDES = {
    'area': ["aliases", "annotation"] + RELATION_INCLUDES,
    'artist': [
        "recordings", "releases", "release-groups", "works", # Subqueries
        "various-artists", "discids", "media", "isrcs",
        "aliases", "annotation"
    ] + RELATION_INCLUDES + TAG_INCLUDES + RATING_INCLUDES,
    'annotation': [

    ],
    'instrument': ["aliases", "annotation"
    ] + RELATION_INCLUDES + TAG_INCLUDES,
    'label': [
        "releases", # Subqueries
        "discids", "media",
        "aliases", "annotation"
    ] + RELATION_INCLUDES + TAG_INCLUDES + RATING_INCLUDES,
    'place' : ["aliases", "annotation"] + RELATION_INCLUDES + TAG_INCLUDES,
    'event' : ["aliases"] + RELATION_INCLUDES + TAG_INCLUDES + RATING_INCLUDES,
    'recording': [
        "artists", "releases", # Subqueries
        "discids", "media", "artist-credits", "isrcs",
        "work-level-rels", "annotation", "aliases"
    ] + TAG_INCLUDES + RATING_INCLUDES + RELATION_INCLUDES,
    'release': [
        "artists", "labels", "recordings", "release-groups", "media",
        "artist-credits", "discids", "isrcs",
        "recording-level-rels", "work-level-rels", "annotation", "aliases"
    ] + TAG_INCLUDES + RELATION_INCLUDES,
    'release-group': [
        "artists", "releases", "discids", "media",
        "artist-credits", "annotation", "aliases"
    ] + TAG_INCLUDES + RATING_INCLUDES + RELATION_INCLUDES,
    'series': [
        "annotation", "aliases"
    ] + RELATION_INCLUDES,
    'work': [
        "aliases", "annotation"
    ] + TAG_INCLUDES + RATING_INCLUDES + RELATION_INCLUDES,
    'url': RELATION_INCLUDES,
    'discid': [ # Discid should be the same as release
        "artists", "labels", "recordings", "release-groups", "media",
        "artist-credits", "discids", "isrcs",
        "recording-level-rels", "work-level-rels", "annotation", "aliases"
    ] + RELATION_INCLUDES,
    'isrc': ["artists", "releases", "isrcs"],
    'iswc': ["artists"],
    'collection': ['releases'],
}
VALID_BROWSE_INCLUDES = {
    'artist': ["aliases"] + TAG_INCLUDES + RATING_INCLUDES + RELATION_INCLUDES,
    'event': ["aliases"] + TAG_INCLUDES + RATING_INCLUDES + RELATION_INCLUDES,
    'label': ["aliases"] + TAG_INCLUDES + RATING_INCLUDES + RELATION_INCLUDES,
    'recording': ["artist-credits", "isrcs"] + TAG_INCLUDES + RATING_INCLUDES + RELATION_INCLUDES,
    'release': ["artist-credits", "labels", "recordings", "isrcs",
                "release-groups", "media", "discids"] + RELATION_INCLUDES,
    'place': ["aliases"] + TAG_INCLUDES + RELATION_INCLUDES,
    'release-group': ["artist-credits"] + TAG_INCLUDES + RATING_INCLUDES + RELATION_INCLUDES,
    'url': RELATION_INCLUDES,
    'work': ["aliases", "annotation"] + TAG_INCLUDES + RATING_INCLUDES + RELATION_INCLUDES,
}

#: These can be used to filter whenever releases are includes or browsed
VALID_RELEASE_TYPES = [
    "nat",
    "album", "single", "ep", "broadcast", "other", # primary types
    "compilation", "soundtrack", "spokenword", "interview", "audiobook",
    "live", "remix", "dj-mix", "mixtape/street", # secondary types
]
#: These can be used to filter whenever releases or release-groups are involved
VALID_RELEASE_STATUSES = ["official", "promotion", "bootleg", "pseudo-release"]
VALID_SEARCH_FIELDS = {
    'annotation': [
        'entity', 'name', 'text', 'type'
    ],
    'area': [
        'aid', 'alias', 'area', 'areaaccent', 'begin', 'comment', 'end',
        'ended', 'iso', 'iso1', 'iso2', 'iso3', 'sortname', 'tag', 'type'
    ],
    'artist': [
        'alias', 'area', 'arid', 'artist', 'artistaccent', 'begin', 'beginarea',
        'comment', 'country', 'end', 'endarea', 'ended', 'gender',
        'ipi', 'isni', 'primary_alias', 'sortname', 'tag', 'type'
    ],
    'event': [
        'aid', 'alias', 'area', 'arid', 'artist', 'begin', 'comment', 'eid',
        'end', 'ended', 'event', 'eventaccent', 'pid', 'place', 'tag', 'type'
    ],
    'instrument': [
        'alias', 'comment', 'description', 'iid', 'instrument',
        'instrumentaccent', 'tag', 'type'
    ],
    'label': [
        'alias', 'area', 'begin', 'code', 'comment', 'country', 'end', 'ended',
        'ipi', 'label', 'labelaccent', 'laid', 'release_count', 'sortname',
        'tag', 'type'
    ],
    'place': [
        'address', 'alias', 'area', 'begin', 'comment', 'end', 'ended', 'lat', 'long',
        'pid', 'place', 'placeaccent', 'type'
    ],
    'recording': [
        'alias', 'arid', 'artist', 'artistname', 'comment', 'country',
        'creditname', 'date', 'dur', 'format', 'isrc', 'number', 'position',
        'primarytype', 'qdur', 'recording', 'recordingaccent', 'reid',
        'release', 'rgid', 'rid', 'secondarytype', 'status', 'tag', 'tid',
        'tnum', 'tracks', 'tracksrelease', 'type', 'video'],

    'release-group': [
        'alias', 'arid', 'artist', 'artistname', 'comment', 'creditname',
        'primarytype', 'reid', 'release', 'releasegroup', 'releasegroupaccent',
        'releases', 'rgid', 'secondarytype', 'status', 'tag', 'type'
    ],
    'release': [
        'alias', 'arid', 'artist', 'artistname', 'asin', 'barcode', 'catno',
        'comment', 'country', 'creditname', 'date', 'discids', 'discidsmedium',
        'format', 'label', 'laid', 'lang', 'mediums', 'primarytype', 'quality',
        'reid', 'release', 'releaseaccent', 'rgid', 'script', 'secondarytype',
        'status', 'tag', 'tracks', 'tracksmedium', 'type'
    ],
    'series': [
        'alias', 'comment', 'orderingattribute', 'series', 'seriesaccent',
        'sid', 'tag', 'type'
    ],
    'work': [
        'alias', 'arid', 'artist', 'comment', 'iswc', 'lang', 'recording',
        'recording_count', 'rid', 'tag', 'type', 'wid', 'work', 'workaccent'
    ]
}

