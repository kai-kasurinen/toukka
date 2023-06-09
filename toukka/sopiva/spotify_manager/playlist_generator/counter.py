#

import collections


class ItemCounter(collections.Counter):

    def plus(self, key):
        self[key] += 1


# END
