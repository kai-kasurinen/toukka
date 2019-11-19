#

from typing import Generator, Any, Deque

import collections


class SourcesQueue:
    def __init__(self) -> None:
        self.sources_queue: Deque = collections.deque()

    def add(self, source) -> None:
        self.sources_queue.append(source)

    def generator(self) -> Generator[Any, None, None]:
        while True:
            try:
                yield from self.sources_queue.popleft()
            except IndexError:
                break

    def __len__(self):
        return len(self.sources_queue)


# END
