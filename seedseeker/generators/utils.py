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
        self.saved = deque(maxlen=max_size)

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self.iterator)

        if self.saved.maxlen and len(self.saved) == self.saved.maxlen:
            self.saved.popleft()

        self.saved.append(value)

        return value
