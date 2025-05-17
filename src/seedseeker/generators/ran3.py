import itertools
from collections.abc import Iterator
from typing import NamedTuple, override

from seedseeker.defs import IntegerRNG, InvalidFormatError
from seedseeker.utils.iterator import synchronize


class Ran3State(NamedTuple):
    """State of Ran3 PRNG."""

    array: list[int]
    pointer_a: int
    pointer_b: int

    def __str__(self) -> str:
        """Print Ran3 state as string."""
        array = ",".join(map(str, self.array))
        return f"{array};{self.pointer_a};{self.pointer_b}"


class Ran3(IntegerRNG[Ran3State]):
    """
    ran3 PRNG.

    Based on the C# implementation

    See:
        https://github.com/wren-projects/SeedSeeker/issues/4
    """

    MAX_INT: int = 2**31 - 1
    MIN_INT: int = -(2**31)
    MSEED: int = 161803398

    seed_array: list[int]
    pointer_a: int
    pointer_b: int

    def __init__(self, seed: int) -> None:
        """Create a new Ran3 PRNG from the given seed."""
        # protect users from poor seeds (e.g. 0)
        while seed > self.MAX_INT:
            seed -= 2**32
        while seed < self.MIN_INT:
            seed += 2**32

        real_seed = self.MSEED - abs(seed)
        self.seed_array = [0] * 55 + [real_seed]

        self.pointer_a = 0
        self.pointer_b = 21

        mj = real_seed

        mk = 1

        for i in range(1, 55):
            ii = (21 * i) % 55

            self.seed_array[ii] = mk

            mk = mj - mk

            if mk < 0:
                mk += self.MAX_INT

            mj = self.seed_array[ii]

        # iterate over the seed array 4 times
        for _, i in itertools.product(range(4), range(1, 56)):
            self.seed_array[i] -= self.seed_array[1 + (i + 30) % 55]

            # simulate Int32's native overflow
            if self.seed_array[i] < self.MIN_INT:
                self.seed_array[i] += 2**32
            if self.seed_array[i] > self.MAX_INT:
                self.seed_array[i] -= 2**32

            if self.seed_array[i] < 0:
                self.seed_array[i] += self.MAX_INT

        assert all(self.MIN_INT <= a <= self.MAX_INT for a in self.seed_array), (
            "Seed array overflowed"
        )

    @override
    def __next__(self) -> int:
        """Return the next value."""
        self.pointer_a += 1
        if self.pointer_a >= 56:
            self.pointer_a = 1

        self.pointer_b += 1
        if self.pointer_b >= 56:
            self.pointer_b = 1

        value = self.seed_array[self.pointer_a] - self.seed_array[self.pointer_b]

        if value == self.MAX_INT:
            value -= 1
        if value < 0:
            value += self.MAX_INT

        self.seed_array[self.pointer_a] = value

        return value

    @override
    def state(self) -> Ran3State:
        """Return the inner state."""
        return Ran3State(self.seed_array, self.pointer_a, self.pointer_b)

    @override
    @staticmethod
    def from_state(state: Ran3State) -> "Ran3":
        """Create a new Ran3 PRNG from the given state."""
        rng = Ran3(0)
        rng.seed_array, rng.pointer_a, rng.pointer_b = state
        return rng

    @override
    @staticmethod
    def is_state_equal(state1: Ran3State, state2: Ran3State) -> bool:
        """Check if two Ran3 PRNG states are equal."""
        array1, pointer_a1, pointer_b1 = state1
        array2, pointer_a2, pointer_b2 = state2

        # This is more complex than a simple
        # equality check because the internal state is a circular buffer.
        if ((pointer_b1 - pointer_b2) - (pointer_a1 - pointer_a2)) % 55 != 0:
            return False

        for _ in range(55):
            pointer_a1 += 1
            pointer_a2 += 1

            if pointer_a1 >= 56:
                pointer_a1 = 1

            if pointer_a2 >= 56:
                pointer_a2 = 1

            if array1[pointer_a1] != array2[pointer_a2]:
                return False

        return True

    @override
    @staticmethod
    def from_string(string: str) -> "Ran3":
        """Create generator with states from parameter string."""
        try:
            seed = int(string)
        except ValueError as e:
            raise InvalidFormatError("Seed must be an integer") from e

        return Ran3(seed)

    @override
    @staticmethod
    def state_from_string(string: str) -> Ran3State:
        """Create state from parameter string."""
        try:
            array, pointer_a, pointer_b = string.split(";")
        except ValueError as e:
            raise InvalidFormatError("Expected 3 parameters") from e

        try:
            array = list(map(int, array.split(",")))
        except ValueError as e:
            raise InvalidFormatError(
                "Array must be a comma-separated list of integers"
            ) from e

        try:
            pointer_a, pointer_b = map(int, [pointer_a, pointer_b])
        except ValueError as e:
            raise InvalidFormatError("Pointer parameters must be integers") from e

        return Ran3State(array, pointer_a, pointer_b)


def reverse_ran3(gen: Iterator[int]) -> Ran3State | None:
    """Reverse a ran3 parameters."""
    try:
        state = Ran3State([0] + [next(gen) for _ in range(55)], 55, 21)
    except StopIteration:
        return None

    return synchronize(gen, Ran3.from_state(state))
