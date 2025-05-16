from collections.abc import Iterator
from itertools import islice, pairwise
from math import gcd
from typing import NamedTuple, override

from mod import Mod

from seedseeker.defs import IntegerRNG
from seedseeker.utils.iterator import BufferingIterator, drop, synchronize
from seedseeker.utils.primes import divisors


class LcgState(NamedTuple):
    """State of a LCG."""

    a: int
    c: int
    x_n: Mod

    def __str__(self) -> str:
        """Print LCG state as string."""
        return f"{self.x_n.modulus};{self.a};{self.c};{int(self.x_n)}"


class Lcg(IntegerRNG[LcgState]):
    """
    Linear Congruential Generator (LCG).

    Uses the formula: Xₙ₊₁ = (a ⋅ Xₙ + c) mod m
    """

    m: int
    a: int
    c: int
    x_n: Mod

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

    @override
    def __next__(self) -> int:
        """Return the next value."""
        self.x_n = self.a * self.x_n + self.c
        return int(self.x_n)

    @override
    def state(self) -> LcgState:
        """Return the inner state."""
        return LcgState(self.a, self.c, self.x_n)

    @override
    @staticmethod
    def from_state(state: LcgState) -> "Lcg":
        """Create a new LCG from given state."""
        a, c, x_n = state
        return Lcg(x_n.modulus, a, c, int(x_n))

    @override
    @staticmethod
    def is_state_equal(state1: LcgState, state2: LcgState) -> bool:
        """Check if two LCG states are equal."""
        return state1 == state2

    @override
    @staticmethod
    def from_string(string: str) -> "Lcg":
        """Create generator with states from parameter string."""
        m, a, c, x_0 = map(int, string.split(";"))
        return Lcg(m, a, c, x_0)

    @override
    @staticmethod
    def state_from_string(string: str) -> LcgState:
        """Create state from parameter string."""
        m, a, c, x_0 = map(int, string.split(";"))
        return LcgState(a, c, Mod(x_0, m))


def reverse_lcg(gen: Iterator[int]) -> LcgState | None:
    """Attempt to reverse-engineer LCG parameters."""
    buffered_lcg = BufferingIterator(gen, max_size=3)

    differences = BufferingIterator(
        (b - a for a, b in pairwise(buffered_lcg)), max_size=4
    )
    drop(differences, 4)  # fill the buffer

    if len(differences.buffer) < 4:
        return None

    guesses: list[int] = []

    while True:
        x1, x2, x3, x4 = differences.buffer

        guess = x4 * x1 - x2 * x3

        if guess > 0:
            guesses.append(guess)

        try:
            next(differences)
            if len(guesses) < 30:
                continue
        except StopIteration:
            if len(guesses) < 8:
                return None

        upper_modulus = gcd(*guesses)

        if upper_modulus <= 1:
            # not an LCG sequence
            return None

        a1, a2, a3 = islice(buffered_lcg.buffer, 3)

        for modulus in divisors(upper_modulus):
            try:
                inverse_modulus = pow((a2 - a1) % modulus, -1, modulus)
            except ValueError:
                continue

            multiple = ((a3 - a2) * inverse_modulus) % modulus

            if not 0 < multiple < modulus:
                continue

            a1, a2 = islice(buffered_lcg.buffer, 2)
            increment = (a2 - a1 * multiple) % modulus

            if not 0 <= increment < modulus:
                continue

            guessed_gen = Lcg.from_state(
                LcgState(multiple, increment, Mod(a3, modulus))
            )
            return synchronize(gen, guessed_gen)
