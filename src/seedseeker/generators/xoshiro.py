from collections.abc import Iterator
from typing import NamedTuple, override

from seedseeker.defs import IntegerRNG, InvalidFormatError
from seedseeker.utils.iterator import synchronize


class XoshiroState(NamedTuple):
    """State of a Xoshiro256** PRNG."""

    s0: int
    s1: int
    s2: int
    s3: int

    def __str__(self) -> str:
        """Print state as string."""
        return f"{self.s0};{self.s1};{self.s2};{self.s3}"


class Xoshiro(IntegerRNG[XoshiroState]):
    """Xoshiro256** PRNG."""

    MODULO: int = 2**64

    s0: int
    s1: int
    s2: int
    s3: int

    def __init__(self, seed: tuple[int, int, int, int]) -> None:
        """Create a new Xoshiro256** PRNG from given seed."""
        assert any(x != 0 for x in seed), "Seed can't be all zero"
        self.s0, self.s1, self.s2, self.s3 = seed

    @override
    def __next__(self) -> int:
        """Return the next value."""
        r = (rot((self.s1 * 5) % self.MODULO, 7) * 9) % self.MODULO
        t = (self.s1 << 17) % self.MODULO
        self.s2 ^= self.s0
        self.s3 ^= self.s1
        self.s1 ^= self.s2
        self.s0 ^= self.s3
        self.s2 ^= t
        self.s3 = rot(self.s3, 45)
        return r

    @override
    def state(self) -> XoshiroState:
        """Return the inner state."""
        return XoshiroState(self.s0, self.s1, self.s2, self.s3)

    @override
    @staticmethod
    def from_state(state: XoshiroState) -> "Xoshiro":
        """Create a new Xoshiro256** PRNG from given state."""
        return Xoshiro(state)

    @override
    @staticmethod
    def is_state_equal(state1: XoshiroState, state2: XoshiroState) -> bool:
        """Check if two Xoshiro256** states are equal."""
        return state1 == state2

    @override
    @staticmethod
    def from_string(string: str) -> "Xoshiro":
        """Create generator with states from parameter string."""
        try:
            s0, s1, s2, s3 = map(int, string.split(";"))
        except ValueError as e:
            raise InvalidFormatError("Expected 4 integer parameters") from e
        return Xoshiro(XoshiroState(s0, s1, s2, s3))

    @override
    @staticmethod
    def state_from_string(string: str) -> XoshiroState:
        """Create state from parameter string."""
        try:
            s0, s1, s2, s3 = map(int, string.split(";"))
        except ValueError as e:
            raise InvalidFormatError("Expected 4 integer parameters") from e

        return XoshiroState(s0, s1, s2, s3)


def rot(x: int, k: int, bit_size: int = 64) -> int:
    """
    Rotate integer x left by k bits.

    Wraps around like bit_size wide integers.
    """
    return ((x << k) | (x >> (bit_size - k))) % 2**bit_size


def reverse_xoshiro(gen: Iterator[int]) -> XoshiroState | None:
    """Attempt to reverse-engineer Xoshiro256** parameters."""
    inv9 = pow(9, -1, 2**64)
    inv5 = pow(5, -1, 2**64)

    def helper(x: int) -> int:
        return (rot((x * inv9) % 2**64, 64 - 7) * inv5) % 2**64

    try:
        a = next(gen)
        b = next(gen)
        c = next(gen)
        d = next(gen)
    except StopIteration:
        return None

    # sX is the inital state
    s1 = helper(a)
    s0s2 = s1 ^ helper(b)
    s0s3 = ((s1 << 17) ^ helper(c)) % 2**64

    # tX us the state after one iteration
    t0 = s1 ^ s0s3
    t1 = s1 ^ s0s2
    _t2 = s0s2 ^ (s1 << 17) % 2**64
    t3 = t0 ^ helper(d) ^ (t1 << 17) % 2**64

    s3 = rot(t3, 64 - 45) ^ s1
    s0 = t0 ^ s1 ^ s3
    s2 = t1 ^ s0 ^ s1

    state = XoshiroState(s0, s1, s2, s3)

    # advance to the same position we left the input in
    reversed_gen = Xoshiro.from_state(state)
    _ = next(reversed_gen)
    _ = next(reversed_gen)
    _ = next(reversed_gen)
    _ = next(reversed_gen)

    return synchronize(gen, reversed_gen)
