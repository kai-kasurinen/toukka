#

import uuid
# uses https://pypi.org/project/pybase62/
import base62


def id_to_int(id_):
    return base62.decode(id_, charset=base62.CHARSET_INVERTED)


def id_to_uuid(id_):
    u = uuid.UUID(int=id_to_int(id_))

    if u.variant != uuid.RFC_4122:
        raise Exception()
    if u.version != 4:
        raise Exception()

    return u


# END
