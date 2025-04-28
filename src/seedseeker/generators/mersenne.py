from itertools import islice

from seedseeker.defs import IntegerRNG

MersenneTwisterState = tuple[list[int], int]


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

    state_array: list[int]
    state_index: int

    def __init__(self, seed: int):
        """Create a new Mersenne Twister 19937 PRNG from given seed."""
        assert 0 <= seed < 2**32, "Seed must be between 0 and 2^32"

        self.state_index = 0
        self.state_array = [seed] + [0] * (self.N - 1)

        for i in range(1, self.N):
            seed = self.F * (seed ^ (seed >> (self.W - 2))) % self.MODULO + i
            self.state_array[i] = seed

    def __next__(self):
        """Return the next value."""
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
        return y

    def state(self) -> MersenneTwisterState:
        """Return the inner state."""
        return self.state_array, self.state_index

    @staticmethod
    def from_state(state: MersenneTwisterState) -> "MersenneTwister":
        """Set the inner state."""
        rng = MersenneTwister(0)
        rng.state_array, rng.state_index = state
        return rng


if __name__ == "__main__":
    print(*islice(MersenneTwister(19650218), 100), sep=", ")
