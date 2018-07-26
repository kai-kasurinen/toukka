#


def _get_flags(dict, needed):
    return [key for key, value in dict.items() if key in needed and value is True]


def _list_to_string(list, sep=', '):
    return sep.join(list)
