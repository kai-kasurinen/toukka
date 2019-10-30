#

import collections


class SourcesQueue:
    def __init__(self):
        self.sources_queue = collections.deque()

    def add(self, source):
        self.sources_queue.append(source)

    def generator(self):
        while True:
            try:
                yield from self.sources_queue.popleft()
            except IndexError:
                break

    def __len__(self):
        return len(self.sources_queue)


# END
