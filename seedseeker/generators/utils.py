from collections import deque
from typing import Iterator


class CountingIterator[T]:
    def __init__(self, iterator: Iterator[T]):
        self.iterator = iterator
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        return next(self.iterator)

    def __len__(self):
        return self.count


class BufferingIterator[T](Iterator[T]):
    def __init__(self, iterator: Iterator[T], max_size=0):
        self.iterator = iterator
        self.buffer = deque(maxlen=max_size)

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self.iterator)

        if self.buffer.maxlen and len(self.buffer) == self.buffer.maxlen:
            self.buffer.popleft()

        self.buffer.append(value)

        return value


def drop[T](iter: Iterator[T], n: int) -> Iterator[T]:
    for _ in range(n):
        try:
            next(iter)
        except StopIteration:
            break

    return iter
