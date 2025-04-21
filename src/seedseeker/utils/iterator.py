from collections import deque
from collections.abc import Iterator


class CountingIterator[T]:
    """An iterator that counts the number of values yielded."""

    def __init__(self, iterator: Iterator[T]):
        """Initialize the iterator."""
        self.iterator = iterator
        self.count = 0

    def __iter__(self):
        """Return the iterator."""
        return self

    def __next__(self):
        """Return the next value and increment the count."""
        self.count += 1
        return next(self.iterator)

    def __len__(self):
        """Return the number of values yielded."""
        return self.count


class BufferingIterator[T](Iterator[T]):
    """
    An iterator that buffers values.

    The buffer is filled lazily as the values are read from the iterator.
    """

    def __init__(self, iterator: Iterator[T], max_size: int = 0):
        """
        Initialize the iterator.

        Max size is the maximum number of values to buffer or 0 for no limit.
        """
        self.iterator = iterator
        self.buffer: deque[T] = deque(maxlen=max_size)

    def __iter__(self):
        """Return the iterator."""
        return self

    def __next__(self):
        """Return the next value."""
        value = next(self.iterator)

        if self.buffer.maxlen and len(self.buffer) == self.buffer.maxlen:
            self.buffer.popleft()

        self.buffer.append(value)

        return value


def drop[T](iterator: Iterator[T], n: int) -> Iterator[T]:
    """
    Drop the first n values from the iterator.

    Changes the iterator in-place but also returns the iterator for convenience.
    If the iterator has fewer than n values, only drop the available values.
    """
    try:
        for _ in range(n):
            next(iterator)
    except StopIteration:
        pass

    return iterator
