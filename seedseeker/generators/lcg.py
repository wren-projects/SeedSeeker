import time
from itertools import islice, pairwise
from math import gcd

from defs import IntegerRNG, RealRNG
from mod import Mod
from primes import divisors
from utils import BufferingIterator, CountingIterator, drop

LcgParameters = tuple[int, int, int]


def lcg(m: int, a: int, c: int, x_0: int) -> IntegerRNG:
    """
    Create a Linear Congruential Generator (LCG).

    Uses the formula:
        X_{n+1} = (a * X_n + c) mod m
    """
    assert m > 0
    assert 0 < a < m
    assert 0 <= c < m
    assert 0 <= x_0 < m

    x_n = Mod(x_0, m)
    while True:
        x_n = a * x_n + c
        yield int(x_n)


def lcg_real(m: int, a: int, c: int, x_0: int) -> RealRNG:
    """Create a Linear Congruential Generator (LCG) with real values."""
    yield from (x_n / m for x_n in lcg(m, a, c, x_0))


def reverse_lcg_parameters(lcg: IntegerRNG) -> LcgParameters:
    """Reverse-engineer LCG parameters."""
    # TODO: add more bounds and precondition checks, to prevent both infinite
    # loops and false positive results

    lcg = BufferingIterator(lcg, max_size=3)

    differences = BufferingIterator((b - a for a, b in pairwise(lcg)), max_size=4)
    drop(differences, 4)  # fill the buffer

    guesses: list[int] = []

    while True:
        x1, x2, x3, x4 = differences.buffer

        guess = x4 * x1 - x2 * x3

        if guess > 0:
            guesses.append(guess)

        next(differences)

        if len(guesses) < 3:
            continue

        upper_modulus = gcd(*guesses)

        assert upper_modulus > 0

        a1, a2, a3 = islice(lcg.buffer, 3)

        for modulus in divisors(upper_modulus):
            try:
                inverse_modulus = pow((a2 - a1) % modulus, -1, modulus)
            except ValueError:
                print(f"No inverse of {a2 - a1} mod {modulus}")
                continue

            multiple = ((a3 - a2) * inverse_modulus) % modulus

            if not 0 < multiple < modulus:
                continue

            a1, a2 = islice(lcg.buffer, 2)
            increment = (a2 - a1 * multiple) % modulus

            if not 0 <= increment < modulus:
                continue

            return modulus, multiple, increment


if __name__ == "__main__":
    # ranqd1 parameters
    m = 2**32
    a = 1664525
    c = 1013904223

    seed = time.time_ns() % m

    counted = CountingIterator(lcg(m, a, c, seed))

    print(reverse_lcg_parameters(counted))
    print(f"Done with {len(counted)} values")

    # graph the planar nature of the generator
    #
    # import matplotlib
    # import matplotlib.pyplot as plt
    #
    # matplotlib.use("QtAgg")
    #
    # num_points = 2**16
    # lcg_gen = lcg(m, a, c, seed)
    # values = [next(lcg_gen) for _ in range(num_points)]
    #
    # x_values = values[:-1]
    # y_values = values[1:]
    #
    # plot = plt.subplots()
    #
    # plt.scatter(x_values, y_values, s=1)
    # plt.title("Scatter plot of LCG generated numbers")
    # plt.xlabel("X values")
    # plt.ylabel("Y values")
    # plt.show()
