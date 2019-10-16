#
# FIXME: remove

import json


def json_dump(obj):
    """dumps json with indent"""
    return json.dumps(obj, indent='  ')


def json_dump_print(obj):
    """prints json with indent"""
    print((json_dump(obj)))
