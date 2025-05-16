import random
from collections.abc import Iterator
from itertools import islice

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
from seedseeker.utils.iterator import drop

GENERATOR_LIMIT = 1000


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
    prng = Ran3(seed)
    _ = drop(prng, values_to_consume)
    found = reverse_ran3(islice(prng, GENERATOR_LIMIT))
    assert found is not None
    expected = prng.state()
    assert Ran3.is_state_equal(found, expected)


@pytest.mark.parametrize(
    ("prng"),
    [
        (drop(MersenneTwister(0), 50)),
        (Lcg(2**32, 11, 0, 100)),
        (
            drop(
                Xoshiro(
                    (
                        2802778124827647829,
                        1070886523979781234,
                        8009364533937910363,
                        5869548737676381262,
                    )
                ),
                50,
            )
        ),
        (islice(Ran3(100), 10)),
        (islice(FibonacciRng(2, 3, 2**32, [4, 5, 6], False), 10)),
        (iter(())),
    ],
)
def test_ran3_reverser_negative(prng: Iterator[int]) -> None:
    """Test the reverser with another generator and check that it fails."""
    assert reverse_ran3(islice(prng, GENERATOR_LIMIT)) is None


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
        (2, 3, 2**32, 0, 40, False),
        (2, 3, 2**32, 10000, 40, False),
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
    prng = FibonacciRng(r, s, m, seed, overflow)
    _ = drop(prng, values_to_consume)

    found = reverse_fibonacci(islice(prng, GENERATOR_LIMIT))
    assert found is not None

    expected = prng.state()
    assert FibonacciRng.is_state_equal(found, expected)


@pytest.mark.parametrize(
    ("prng"),
    [
        (drop(MersenneTwister(0), 50)),
        (islice(Lcg(100, 21, 7, 11), 101)),
        (
            drop(
                Xoshiro(
                    (
                        2802778124827647829,
                        1070886523979781234,
                        8009364533937910363,
                        5869548737676381262,
                    )
                ),
                50,
            )
        ),
        (islice(FibonacciRng(2, 3, 2**32, [4, 5, 6], False), 2)),
        (Ran3(100)),
        (iter(())),
    ],
)
def test_fibonacci_reverser_negative(prng: Iterator[int]) -> None:
    """Test the reverser with another generator and check that it fails."""
    assert reverse_fibonacci(islice(prng, GENERATOR_LIMIT)) is None


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
    _ = drop(prng, values_to_consume)

    found = reverse_lcg(islice(prng, GENERATOR_LIMIT))
    assert found is not None

    expected = prng.state()
    assert Lcg.is_state_equal(found, expected)


@pytest.mark.parametrize(
    ("prng"),
    [
        (drop(MersenneTwister(0), 50)),
        (Ran3(100)),
        (
            drop(
                Xoshiro(
                    (
                        2802778124827647829,
                        1070886523979781234,
                        8009364533937910363,
                        5869548737676381262,
                    )
                ),
                50,
            )
        ),
        (islice(Lcg(2**32, 11, 0, 100), 10)),
        (islice(FibonacciRng(2, 3, 2**32, [4, 5, 6], False), 10)),
        (iter(())),
    ],
)
def test_lcg_reverser_negative(prng: Iterator[int]) -> None:
    """Test the reverser with another generator and check that it fails."""
    assert reverse_lcg(islice(prng, GENERATOR_LIMIT)) is None


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
    _ = drop(prng, values_to_consume)

    found = reverse_xoshiro(islice(prng, GENERATOR_LIMIT))
    assert found is not None

    expected = prng.state()
    assert Xoshiro.is_state_equal(found, expected)


@pytest.mark.parametrize(
    ("prng"),
    [
        (drop(MersenneTwister(0), 50)),
        (Ran3(100)),
        (FibonacciRng(2, 3, 2**32, [4, 5, 6], False)),
        (islice(Lcg(2**32, 11, 0, 100), 10)),
        (
            islice(
                drop(
                    Xoshiro(
                        (
                            2802778124827647829,
                            1070886523979781234,
                            8009364533937910363,
                            5869548737676381262,
                        )
                    ),
                    50,
                ),
                3,
            )
        ),
        (iter(())),
    ],
)
def test_xoshiro_reverser_negative(prng: Iterator[int]) -> None:
    """Test the reverser with another generator and check that it fails."""
    assert reverse_xoshiro(islice(prng, GENERATOR_LIMIT)) is None


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
    _ = drop(prng, values_to_consume)

    found = reverse_mersenne(islice(prng, GENERATOR_LIMIT))
    assert found is not None

    randcrack = MersenneTwister.from_state(found)

    for _ in range(10 * values_to_consume):
        original = next(prng)
        predicted = next(randcrack)

        assert original == predicted


@pytest.mark.parametrize(
    ("prng"),
    [
        (Lcg(2**32, 11, 0, 100)),
        (Ran3(100)),
        (FibonacciRng(2, 3, 2**32, [4, 5, 6], False)),
        (islice(drop(MersenneTwister(0), 50), 10)),
        (
            islice(
                drop(
                    Xoshiro(
                        (
                            2802778124827647829,
                            1070886523979781234,
                            8009364533937910363,
                            5869548737676381262,
                        )
                    ),
                    50,
                ),
                3,
            )
        ),
        (iter(())),
    ],
)
def test_mersenne_reverser_negative(prng: Iterator[int]) -> None:
    """Test the reverser with another generator and check that it fails."""
    assert reverse_mersenne(islice(prng, GENERATOR_LIMIT)) is None
