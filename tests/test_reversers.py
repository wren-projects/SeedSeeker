import random

import pytest

from seedseeker.generators import (
    FibonacciRng,
    Lcg,
    MersenneTwister,
    Ran3,
    Xoshiro,
    reverse_fibonacci,
    reverse_lcg,
    reverse_mersenne,
    reverse_ran3,
    reverse_xoshiro,
)
from seedseeker.generators.xoshiro import XoshiroState


@pytest.mark.parametrize(
    ("seed", "values_to_consume"),
    [
        (50, 50),
        (random.randint(0, 2**32), 100),
        (random.randint(0, 2**32), 10),
        (random.randint(0, 2**32), 50),
        (random.randint(0, 2**32), 0),
    ],
)
def test_ran3_reverser(seed: int, values_to_consume: int) -> None:
    """
    Test the reverser for a given generator with a random seed and values_to_consume.

    The test will consume values_to_consume values from the generator, then
    reverse-engineer the parameters and compare them with the current state of
    the generator.
    """
    print(seed)
    prng = Ran3(seed)
    [next(prng) for _ in range(values_to_consume)]
    found = reverse_ran3(prng)
    expected = prng.state()
    assert Ran3.is_state_equal(found, expected)


def create_random_fibonaci_test() -> tuple[int, int, int, list[int], int, bool]:
    """
    Create a random test data for the Fibonacci reverser.

    All of these values are randomly generated.
    """
    r = random.randint(1, 100)
    s = random.randint(1, 100)
    m = random.randint(100, 2**32)
    seed = [random.randint(0, m - 1) for _ in range(max(r, s))]
    values_to_consume = random.randint(0, 100)
    overflow = random.choice([True, False])
    return r, s, m, seed, values_to_consume, overflow


@pytest.mark.parametrize(
    ("r", "s", "m", "seed", "values_to_consume", "overflow"),
    [
        (2, 3, 2**32, [4, 5, 6], 40, True),
        (2, 3, 2**32, [4, 5, 6], 40, False),
        (
            20,
            11,
            1643933623,
            [
                793915067,
                1547151479,
                1592074433,
                794215566,
                917692078,
                636848023,
                476578936,
                668106188,
                378291862,
                473622562,
                1162618183,
                414468060,
                41436058,
                1427201453,
                482624327,
                265847987,
                872178836,
                550227192,
                95093415,
                1291944706,
            ],
            1,
            False,
        ),
        create_random_fibonaci_test(),
    ],
)
def test_fibonacci_reverser(
    r: int, s: int, m: int, seed: list[int], values_to_consume: int, overflow: bool
) -> None:
    """
    Test the reverser for a given generator with a random seed and values_to_consume.

    The test will consume values_to_consume values from the generator, then
    reverse-engineer the parameters and compare them with the current state of
    the generator.
    """
    print(r, s, m, seed, values_to_consume, overflow)
    prng = FibonacciRng(r, s, m, seed, overflow)
    [next(prng) for _ in range(values_to_consume)]
    found = reverse_fibonacci(prng)
    assert found is not None
    expected = prng.state()
    assert FibonacciRng.is_state_equal(found, expected)


@pytest.mark.parametrize(
    ("a", "b", "m", "seed", "values_to_consume"),
    [
        (75, 0, 2**16 + 1, random.randint(0, 2**16 + 1), random.randint(0, 100)),
        (1664525, 1013904223, 2**32, random.randint(0, 2**32), random.randint(0, 100)),
        (48271, 0, 2**31 - 1, random.randint(0, 2**31 - 1), random.randint(0, 100)),
        (8121, 28411, 134456, random.randint(0, 134456), random.randint(0, 100)),
        (214013, 2531011, 2**31, random.randint(0, 2**31), random.randint(0, 100)),
    ],
)
def test_lcg_reverser(
    a: int, b: int, m: int, seed: int, values_to_consume: int
) -> None:
    """Test the reverser for a given LCG generator params."""
    prng = Lcg(m, a, b, seed)
    [next(prng) for _ in range(values_to_consume)]
    found = reverse_lcg(prng)
    assert found is not None
    expected = prng.state()
    assert Lcg.is_state_equal(found, expected)


@pytest.mark.parametrize(
    ("seed", "values_to_consume"),
    [
        (
            (
                random.randint(0, 2**64),
                random.randint(0, 2**64),
                random.randint(0, 2**64),
                random.randint(0, 2**64),
            ),
            random.randint(0, 100),
        ),
        ((random.randint(0, 2**64), 0, 0, 0), 50),
    ],
)
def test_xoshiro_reverser(seed: XoshiroState, values_to_consume: int) -> None:
    """Test the reverser for a given Xoshiro generator params."""
    prng = Xoshiro(seed)
    [next(prng) for _ in range(values_to_consume)]
    found = reverse_xoshiro(prng)
    assert found is not None
    expected = prng.state()
    assert Xoshiro.is_state_equal(found, expected)



@pytest.mark.parametrize(
    ("seed", "values_to_consume"),
    [
        (
            random.randint(0, 2**32 - 1),
            random.randint(10, 50),
        ),
        (
            random.randint(0, 2**32 - 1),
            random.randint(10, 50),
        ),
        (
            random.randint(0, 2**32 - 1),
            random.randint(10, 50),
        ),
        (123456789, 100),
    ],
)
def test_reverse_mersenne(seed: int, values_to_consume: int) -> None:
    """Testing Mersenne Twister reverse function."""
    prng = MersenneTwister(seed)
    for _ in range(values_to_consume):
        next(prng)

    found = reverse_mersenne(prng)
    assert found is not None

    randcrack = MersenneTwister.from_state(found)

    for _ in range(10 * values_to_consume):
        original = next(prng)
        predicted = next(randcrack)

        assert original == predicted
