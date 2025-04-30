import itertools
from collections.abc import Iterator

from seedseeker.defs import IntegerRNG

Ran3State = tuple[list[int], int, int]


class Ran3(IntegerRNG[Ran3State]):
    """
    ran3 PRNG.

    Based on the C# implementation

    See:
        https://github.com/wren-projects/SeedSeeker/issues/4
    """

    MAX_INT = 2**31 - 1
    MIN_INT = -(2**31)
    MSEED = 161803398

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

    def state(self) -> Ran3State:
        """Return the inner state."""
        return self.seed_array, self.pointer_a, self.pointer_b

    @staticmethod
    def from_state(state: Ran3State) -> "Ran3":
        """Create a new Ran3 PRNG from the given state."""
        rng = Ran3(0)
        rng.seed_array, rng.pointer_a, rng.pointer_b = state
        return rng

    @staticmethod
    def is_state_equal(state1: Ran3State, state2: Ran3State) -> bool:
        """
        Check if two Ran3 PRNG states are equal.

        This is more complex than a simple
        equality check because the internal state is a circular buffer.
        """
        if ((state1[2] - state2[2]) - (state1[1] - state2[1])) % 55 != 0:
            return False
        print(state1)
        print(state2)

        index1 = state1[1]
        index2 = state2[1]

        for _ in range(55):
            index1 += 1
            index2 += 1
            if index1 >= 56:
                index1 = 1
            if index2 >= 56:
                index2 = 1
            if state1[0][index1] != state2[0][index2]:
                return False
        return True


def reverse_ran3(ran3: Iterator[int]) -> Ran3State:
    """Reverse a ran3 parameters."""
    return [0] + [next(ran3) for _ in range(55)], 55, 21
