#

import simplejson

def json_dump(obj):
    """dumps json with indent"""
    return simplejson.dumps(obj, indent='  ')


def json_dump_print(obj):
    """prints json with indent"""
    print((json_dump(obj)))
