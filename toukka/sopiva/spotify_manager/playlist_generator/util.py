#

from typing import Generator, Any

import itertools
import random
import more_itertools


# source: https://stackoverflow.com/questions/21187131/how-to-use-random-shuffle-on-a-generator-python
# modified
def shuffle_generator(generator: Generator, buffer_size: int) -> Generator[Any, None, None]:
    while True:
        buffer = list(itertools.islice(generator, buffer_size))
        if len(buffer) == 0:
            break
        random.shuffle(buffer)
        for item in buffer:
            yield item


# source: https://stackoverflow.com/questions/21187131/how-to-use-random-shuffle-on-a-generator-python
# modified
def scramble_generator(generator: Generator, buffer_size: int) -> Generator[Any, None, None]:
    buf = []
    i = iter(generator)
    while True:
        try:
            e = next(i)
            buf.append(e)
            if len(buf) >= buffer_size:
                choice = random.randint(0, len(buf)-1)
                buf[-1], buf[choice] = buf[choice], buf[-1]
                yield buf.pop()
        except StopIteration:
            random.shuffle(buf)
            yield from buf
            return


# END
