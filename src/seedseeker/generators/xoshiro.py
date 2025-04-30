from collections.abc import Iterator

from seedseeker.defs import IntegerRNG

XoshiroState = tuple[int, int, int, int]


class Xoshiro(IntegerRNG[XoshiroState]):
    """Xoshiro256** PRNG."""

    MODULO = 2**64

    s0: int
    s1: int
    s2: int
    s3: int

    def __init__(self, seed: XoshiroState) -> None:
        """Create a new Xoshiro256** PRNG from given seed."""
        assert any(x != 0 for x in seed), "Seed can't be all zero"
        self.s0, self.s1, self.s2, self.s3 = seed

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

    def state(self) -> XoshiroState:
        """Return the inner state."""
        return self.s0, self.s1, self.s2, self.s3

    @staticmethod
    def from_state(state: XoshiroState) -> "Xoshiro":
        """Create a new Xoshiro256** PRNG from given state."""
        return Xoshiro(state)

    @staticmethod
    def is_state_equal(state1: XoshiroState, state2: XoshiroState) -> bool:
        """Check if two Xoshiro256** states are equal."""
        return state1 == state2


def rot(x: int, k: int, bit_size: int = 64) -> int:
    """
    Rotate integer x left by k bits.

    Wraps around like bit_size wide integers.
    """
    return ((x << k) | (x >> (bit_size - k))) % 2**bit_size


def reverse_xoshiro(gen: Iterator[int]) -> XoshiroState:
    """Attempt to reverse-engineer Xoshiro256** parameters."""
    inv9 = pow(9, -1, 2**64)
    inv5 = pow(5, -1, 2**64)

    def helper(x: int) -> int:
        return (rot((x * inv9) % 2**64, 64 - 7) * inv5) % 2**64

    a = next(gen)
    b = next(gen)
    c = next(gen)
    d = next(gen)

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

    og_state = [s0, s1, s2, s3]
    gen = Xoshiro.from_state(og_state)
    next(gen)
    next(gen)
    next(gen)
    next(gen)

    return gen.state()
