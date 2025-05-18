from collections.abc import Iterator
from itertools import islice
from typing import NamedTuple, override

from randcrack import RandCrack

from seedseeker.defs import IntegerRNG, InvalidFormatError
from seedseeker.utils.iterator import CountingIterator


class MersenneTwisterState(NamedTuple):
    """State of Mersenne Twister PRNG."""

    array: list[int]
    pointer: int

    def __str__(self) -> str:
        """Print Mersenne Twister state as string."""
        return f"{self.array};{self.pointer}"


class RandCrackState(NamedTuple):
    """State of RandCrack reverser."""

    mt: list[list[int]]
    counter: int

    def __str__(self) -> str:
        """Print RandCrack state as string."""

        def bits_to_int(bits: list[int]) -> int:
            return int("".join(map(str, bits)), 2)

        hex_encoded = ",".join(f"{bits_to_int(i32):X}" for i32 in self.mt)

        return f"{hex_encoded};{self.counter}"


class MersenneTwister(IntegerRNG[MersenneTwisterState]):
    """Mersenne Twister 19937 PRNG."""

    N: int = 624
    M: int = 397
    W: int = 32
    R: int = 31
    UMASK: int = 0xFFFFFFFF << R
    LMASK: int = 0xFFFFFFFF >> (W - R)
    A: int = 0x9908B0DF
    U: int = 11
    S: int = 7
    T: int = 15
    L: int = 18
    B: int = 0x9D2C5680
    C: int = 0xEFC60000
    F: int = 1812433253
    MODULO: int = 2**32

    state_array: list[int]
    state_index: int
    rand_crack: RandCrack | None

    def __init__(self, seed: int):
        """Create a new Mersenne Twister 19937 PRNG from given seed."""
        assert 0 <= seed < 2**32, "Seed must be between 0 and 2^32"

        self.state_index = 0
        self.state_array = [seed] + [0] * (self.N - 1)
        self.rand_crack = None

        for i in range(1, self.N):
            seed = self.F * (seed ^ (seed >> (self.W - 2))) % self.MODULO + i
            self.state_array[i] = seed

    @override
    def __next__(self) -> int:
        """Return the next value."""
        if self.rand_crack is not None:
            return self.rand_crack.predict_getrandbits(32)

        k = self.state_index
        j = k - (self.N - 1)
        if j < 0:
            j += self.N

        x = (self.state_array[k] & self.UMASK) | (self.state_array[j] & self.LMASK)
        x_a = x >> 1
        if x & 1:  # modulo 2 == 1
            x_a ^= self.A

        j = k - (self.N - self.M)
        if j < 0:
            j += self.N

        x = self.state_array[j] ^ x_a
        self.state_array[k] = x
        k += 1
        if k >= self.N:
            k = 0
        self.state_index = k

        y = x ^ (x >> self.U)
        y ^= (y << self.S) & self.B
        y ^= (y << self.T) & self.C
        y ^= y >> self.L
        return y & 0xFFFFFFFF  # Ensure 32-bit output

    @override
    def state(self) -> MersenneTwisterState | RandCrackState:
        """Return the inner state."""
        if self.rand_crack is None:
            return MersenneTwisterState(self.state_array, self.state_index)

        return RandCrackState(self.rand_crack.mt, self.rand_crack.counter)

    @override
    @staticmethod
    def from_state(state: RandCrackState) -> "MersenneTwister":
        """Set the inner state."""
        rng = MersenneTwister(0)
        rng.rand_crack = RandCrack()
        rng.rand_crack.mt, rng.rand_crack.counter = state
        rng.rand_crack.state = True
        return rng

    @override
    @staticmethod
    def is_state_equal(
        state1: MersenneTwisterState, state2: MersenneTwisterState
    ) -> bool:
        raise NotImplementedError

    @override
    @staticmethod
    def from_string(string: str) -> "MersenneTwister":
        """Create generator with states from parameter string."""
        try:
            seed = int(string)
        except ValueError as e:
            raise InvalidFormatError("Seed must be an integer") from e

        return MersenneTwister(seed)

    @override
    @staticmethod
    def state_from_string(string: str) -> RandCrackState:
        """Create state from parameter string."""
        try:
            array, counter = string.split(";")
        except ValueError as e:
            raise InvalidFormatError("Expected 2 parameters") from e

        def int_to_bits(i: int) -> list[int]:
            return [(i >> b) & 1 for b in reversed(range(32))]

        try:
            array = [int_to_bits(int(i32, 16)) for i32 in array.split(",")]
        except ValueError as e:
            raise InvalidFormatError(
                "Array must be a comma-separated list of hexadecimal integers"
            ) from e

        try:
            counter = int(counter)
        except ValueError as e:
            raise InvalidFormatError("Counter must be an integer") from e

        return RandCrackState(array, counter)


def reverse_mersenne(mersenne: Iterator[int]) -> RandCrackState | None:
    """Find state using RandCrack algorithm from an iterator."""
    predictor = RandCrack()
    counting = CountingIterator(mersenne)

    for value in islice(counting, 624):
        predictor.submit(value)

    if counting.count < 624:
        return None

    for value in counting:
        if value != predictor.predict_getrandbits(32):
            return None

    return RandCrackState(predictor.mt, predictor.counter)
