from collections import deque
from itertools import islice, pairwise
from math import gcd
from typing import Iterator

from primes import divisors
from defs import IntegerRNG, RealRNG
from utils import BufferingIterator, CountingIterator

# import matplotlib
# import matplotlib.pyplot as plt

# matplotlib.use("QtAgg")

LcgParameters = tuple[int, int, int]


def lcg(m: int, a: int, c: int, x_0: int) -> IntegerRNG:
    assert m > 0
    assert 0 < a < m
    assert 0 <= c < m
    assert 0 <= x_0 < m

    x_n = x_0
    while True:
        x_n = (a * x_n + c) % m
        yield x_n


def lcg_real(m: int, a: int, c: int, x_0: int) -> RealRNG:
    yield from (x_n / m for x_n in lcg(m, a, c, x_0))


def reverse_lcg_parameters(lcg: Iterator[int]) -> LcgParameters:
    # TODO: clean up and add more bounds/precondition checks

    lcg = BufferingIterator(lcg, max_size=3)

    differences = (b - a for a, b in pairwise(lcg))
    active_differences = deque(islice(differences, 4), maxlen=4)
    guesses: list[int] = []

    while True:
        x1, x2, x3, x4 = active_differences

        guess = x4 * x1 - x2 * x3

        if guess:
            guesses.append(guess)

        active_differences.popleft()
        active_differences.append(next(differences))

        if len(guesses) < 3:  # or (upper_modulus := gcd(*guesses)) == 0:
            continue

        upper_modulus = gcd(*guesses)

        assert upper_modulus

        a1, a2, a3 = islice(lcg.saved, 3)

        for modulus in divisors(upper_modulus):
            try:
                inverse_modulus = pow((a2 - a1) % modulus, -1, modulus)
            except ValueError:
                print(f"No inverse of {a2 - a1} mod {modulus}")
                continue

            multiple = ((a3 - a2) * inverse_modulus) % modulus

            if not 0 < multiple < modulus:
                continue

            a1, a2 = islice(lcg.saved, 2)
            increment = (a2 - a1 * multiple) % modulus

            if not 0 <= increment < modulus:
                continue

            return modulus, multiple, increment


if __name__ == "__main__":
    m = 2**31 - 1
    a = 11 * 17 * 71 * 7919
    c = 3**12

    seed = 12**8

    counted = CountingIterator(lcg(m, a, c, seed))

    print(reverse_lcg_parameters(counted))
    print(f"Done with {len(counted)} values")

    # num_points = 2**15
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
