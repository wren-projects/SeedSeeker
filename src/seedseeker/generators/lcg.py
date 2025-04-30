from collections.abc import Iterator
from itertools import islice, pairwise
from math import gcd

from mod import Mod

from seedseeker.defs import IntegerRNG
from seedseeker.utils.iterator import BufferingIterator, drop
from seedseeker.utils.primes import divisors

LcgState = tuple[int, int, Mod]


class Lcg(IntegerRNG[LcgState]):
    """
    Linear Congruential Generator (LCG).

    Uses the formula: Xₙ₊₁ = (a ⋅ Xₙ + c) mod m
    """

    def __init__(self, m: int, a: int, c: int, x_0: int) -> None:
        """Create a Linear Congruential Generator (LCG)."""
        assert m > 0
        assert 0 < a < m
        assert 0 <= c < m
        assert 0 <= x_0 < m

        self.m = m
        self.a = a
        self.c = c
        self.x_n = Mod(x_0, m)

    def __next__(self) -> int:
        """Return the next value."""
        self.x_n = self.a * self.x_n + self.c
        return int(self.x_n)

    def state(self) -> LcgState:
        """Return the inner state."""
        return self.a, self.c, self.x_n

    @staticmethod
    def from_state(state: LcgState) -> "Lcg":
        """Create a new LCG from given state."""
        rng = Lcg(0, 0, 0, 0)
        rng.a, rng.c, rng.x_n = state
        return rng

    @staticmethod
    def is_state_equal(state1: LcgState, state2: LcgState) -> bool:
        """Check if two LCG states are equal."""
        return state1 == state2


def reverse_lcg(lcg: Iterator[int]) -> LcgState | None:
    """Attempt to reverse-engineer LCG parameters."""
    # TODO: add more bounds and precondition checks, to prevent both infinite
    # loops and false positive results

    buffered_lcg = BufferingIterator(lcg, max_size=3)

    differences = BufferingIterator(
        (b - a for a, b in pairwise(buffered_lcg)), max_size=4
    )
    drop(differences, 4)  # fill the buffer

    guesses: list[int] = []

    while True:
        x1, x2, x3, x4 = differences.buffer

        guess = x4 * x1 - x2 * x3

        if guess > 0:
            guesses.append(guess)

        next(differences)

        if len(guesses) < 30:
            continue

        upper_modulus = gcd(*guesses)

        assert upper_modulus > 0

        a1, a2, a3 = islice(buffered_lcg.buffer, 3)

        for modulus in divisors(upper_modulus):
            try:
                inverse_modulus = pow((a2 - a1) % modulus, -1, modulus)
            except ValueError:
                print(f"No inverse of {a2 - a1} mod {modulus}")
                continue

            multiple = ((a3 - a2) * inverse_modulus) % modulus

            if not 0 < multiple < modulus:
                continue

            a1, a2 = islice(buffered_lcg.buffer, 2)
            increment = (a2 - a1 * multiple) % modulus

            if not 0 <= increment < modulus:
                continue

            return multiple, increment, Mod(a3, modulus)
