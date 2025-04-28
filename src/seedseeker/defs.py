from collections.abc import Iterator
from typing import Protocol, Self


class IntegerRNG[StateT](Protocol):
    """Integer random number generator protocol."""

    def __iter__(self) -> Iterator[int]:
        """Return the iterator."""
        return self

    def __next__(self) -> int:
        """Return the next value."""
        raise NotImplementedError

    def state(self) -> StateT:
        """Return the inner state."""
        raise NotImplementedError

    @staticmethod
    def from_state(state: StateT) -> Self:
        """Set the inner state."""
        raise NotImplementedError
