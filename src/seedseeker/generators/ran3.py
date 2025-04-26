import itertools
import random
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

        assert all(self.MIN_INT < a < self.MAX_INT for a in self.seed_array)

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


def reverse_ran3(ran3: Iterator[int]) -> Ran3State:
    """Reverse a ran3 parameters."""
    return [next(ran3) for _ in range(55)], 0, 21


if __name__ == "__main__":
    seed = random.randint(0, 2**32)
    PRNG = Ran3(seed)
    print(reverse_ran3(PRNG))
