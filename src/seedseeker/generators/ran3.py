import itertools
import random
from collections.abc import Iterator

from seedseeker.defs import IntegerRNG

MAX_INT = 2**31 - 1
MIN_INT = -(2**31)
MSEED = 161803398


def ran3(seed: int) -> IntegerRNG:
    """
    Create a ran3 PRNG.

    Based on the C# implementation

    See:
        https://github.com/wren-projects/SeedSeeker/issues/4
    """
    # protect users from poor seeds (e.g. 0)
    real_seed = MSEED - abs(seed)
    seed_array = [0] * 56

    seed_array[55] = real_seed
    mj = real_seed

    mk = 1

    for i in range(1, 55):
        ii = (21 * i) % 55

        seed_array[ii] = mk

        mk = mj - mk

        if mk < 0:
            mk += MAX_INT

        mj = seed_array[ii]

    assert all(MIN_INT < a < MAX_INT for a in seed_array)

    # iterate over the seed array 4 times
    for _, i in itertools.product(range(4), range(1, 56)):
        seed_array[i] -= seed_array[1 + (i + 30) % 55]

        # simulate Int32's native overflow
        if seed_array[i] < MIN_INT:
            seed_array[i] += 2**32
        if seed_array[i] > MAX_INT:
            seed_array[i] -= 2**32

        if seed_array[i] < 0:
            seed_array[i] += MAX_INT

    pointer_a = 0
    pointer_b = 21
    while True:
        pointer_a += 1
        if pointer_a >= 56:
            pointer_a = 1

        pointer_b += 1
        if pointer_b >= 56:
            pointer_b = 1

        return_value = seed_array[pointer_a] - seed_array[pointer_b]

        if return_value == MAX_INT:
            return_value -= 1
        if return_value < 0:
            return_value += MAX_INT

        seed_array[pointer_a] = return_value

        yield return_value


def ran3_real(seed: int) -> Iterator[float]:
    """Create a ran3 PRNG with real values."""
    yield from (x_n / MAX_INT for x_n in ran3(seed))


def reverse_ran3(ran3: IntegerRNG) -> list[int]:
    """Reverse a ran3 parameters."""
    return [next(ran3) for _ in range(55)]


if __name__ == "__main__":
    seed = random.randint(0, 2**32)
    PRNG = ran3(seed)
    print(reverse_ran3(PRNG))
