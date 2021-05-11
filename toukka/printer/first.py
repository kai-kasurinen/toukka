#

import functools
import pprint


@functools.singledispatch
def printer(item, *args, **kwargs):
    print(item)


# END
