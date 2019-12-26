#

from typing import Generator, Any, Deque

import logging
import collections

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SourcesQueue:
    def __init__(self) -> None:
        self.sources_queue: Deque = collections.deque()

    def add(self, source: Any) -> None:
        self.sources_queue.append(source)

    def generator(self) -> Generator[Any, None, None]:
        while True:
            try:
                source = self.sources_queue.popleft()
            except IndexError:
                logger.debug('No sources left (breaking)')
                break
            # hack, source should always be iterable
            if source is None:
                logger.warning('source is None, should be iterable')
                continue
            yield from source

    def __len__(self) -> int:
        return len(self.sources_queue)


# END
