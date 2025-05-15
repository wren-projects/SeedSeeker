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

    @staticmethod
    def is_state_equal(state1: StateT, state2: StateT) -> bool:
        """Check if two states are equal."""
        raise NotImplementedError

    @staticmethod
    def from_string(string: str) -> Self:
        """Create generator with states from parameter string."""
        raise NotImplementedError

    @staticmethod
    def state_from_string(string: str) -> StateT:
        """Create state from parameter string."""
        raise NotImplementedError
