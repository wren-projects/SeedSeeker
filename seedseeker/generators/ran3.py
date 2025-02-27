from typing import Iterator
import random


def ran3(seed: int):
    """
    based on the C# implementation
    """
    MAX_INT = 2**32
    MSEED = 161803398

    REAL_SEED = MSEED - abs(seed)
    SeedArray = [0] * 56

    SeedArray[55] = REAL_SEED
    mj = REAL_SEED

    next_seed = 1

    fib = [0, 1]
    while len(fib) < 56:
        fib.append(fib[-1] + fib[-2])

    for i in range(1, 55):
        ii = (21 * i) % 55

        print(next_seed, ((-1) ** i * (fib[i - 1] * REAL_SEED - fib[i])) % MAX_INT)
        SeedArray[ii] = next_seed

        next_seed = mj - next_seed

        if next_seed < 0:
            next_seed += MAX_INT

        mj = SeedArray[ii]

    for k in range(1, 5):
        for i in range(1, 56):
            SeedArray[i] -= SeedArray[1 + (i + 30) % 55]
        if SeedArray[i] < 0:
            SeedArray[i] += MAX_INT

    pointerA = 0
    pointerB = 21
    while True:
        pointerA += 1
        if pointerA >= 56:
            pointerA = 1

        pointerB += 1
        if pointerB >= 56:
            pointerB = 1

        retValue = SeedArray[pointerA] - SeedArray[pointerB]
        if retValue == MAX_INT:
            retValue -= 1
        if retValue < 0:
            retValue += MAX_INT

        SeedArray[pointerA] = retValue
        print(SeedArray)
        yield retValue


def reverseRan3(ran3: Iterator[int]):
    values = [next(ran3) for _ in range(55)]
    return values


if __name__ == "__main__":
    seed = random.randint(0, 2**32)
    PRNG = ran3(seed)
    print(reverseRan3(PRNG))
