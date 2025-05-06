from collections.abc import Iterator
from itertools import islice
from typing import override

from randcrack import RandCrack

from seedseeker.defs import IntegerRNG

MersenneTwisterState = tuple[list[int], int]
RandCrackerState = tuple[list[int], int]


class MersenneTwister(IntegerRNG[MersenneTwisterState]):
    """Mersenne Twister 19937 PRNG."""

    N = 624
    M = 397
    W = 32
    R = 31
    UMASK = 0xFFFFFFFF << R
    LMASK = 0xFFFFFFFF >> (W - R)
    A = 0x9908B0DF
    U = 11
    S = 7
    T = 15
    L = 18
    B = 0x9D2C5680
    C = 0xEFC60000
    F = 1812433253
    MODULO = 2**32

    "Class contains state, index and predict."
    "Predict means that Mersenne Class is copy of RandCrack."
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
        if self.rand_crack is None:
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

        return self.rand_crack.predict_getrandbits(32)


    @override
    def state(self) -> MersenneTwisterState | RandCrackerState:
        """Return the inner state."""
        if self.rand_crack is None:
            return self.state_array.copy(), self.state_index

        return (self.rand_crack.mt, self.rand_crack.counter)

    @override
    @staticmethod
    def from_state(state: RandCrackerState) -> "MersenneTwister":
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


def reverse_mersenne(mersenne: Iterator[int]) -> MersenneTwister | None:
    """Find state using RandCrack algorithm from an iterator."""
    predictor = RandCrack()

    for value in islice(mersenne, 624):
        predictor.submit(value)

    return MersenneTwister.from_state((predictor.mt, predictor.counter))


if __name__ == "__main__":
    orig = MersenneTwister(159753478)
    pred = reverse_mersenne(orig)

    if pred is not None:
        print(f"Predicted: {pred.__next__()}")
        print(f"Original: {orig.__next__()}")
