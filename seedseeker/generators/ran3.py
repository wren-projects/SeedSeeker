from typing import Iterator
import random
from defs import IntegerRNG


def ran3(seed: int) -> IntegerRNG:
    """
    based on the C# implementation

    See:
        https://github.com/wren-projects/SeedSeeker/issues/4
    """
    MAX_INT = 2**32
    MSEED = 161803398

    REAL_SEED = MSEED - abs(seed)
    seed_array = [0] * 56

    seed_array[55] = REAL_SEED
    mj = REAL_SEED

    next_seed = 1

    for i in range(1, 55):
        ii = (21 * i) % 55

        seed_array[ii] = next_seed

        next_seed = mj - next_seed

        if next_seed < 0:
            next_seed += MAX_INT

        mj = seed_array[ii]

    for _ in range(1, 5):
        for i in range(1, 56):
            seed_array[i] -= seed_array[1 + (i + 30) % 55]
            if seed_array[i] < 0:
                seed_array[i] += MAX_INT

    pointerA = 0
    pointerB = 21
    while True:
        pointerA += 1
        if pointerA >= 56:
            pointerA = 1

        pointerB += 1
        if pointerB >= 56:
            pointerB = 1

        retValue = seed_array[pointerA] - seed_array[pointerB]
        if retValue == MAX_INT:
            retValue -= 1
        if retValue < 0:
            retValue += MAX_INT

        seed_array[pointerA] = retValue
        yield retValue


def reverseRan3(ran3: Iterator[int]) -> list[int]:
    values = [next(ran3) for _ in range(55)]
    return values


if __name__ == "__main__":
    seed = random.randint(0, 2**32)
    PRNG = ran3(seed)
    print(reverseRan3(PRNG))
