import random

from seedseeker.defs import IntegerRNG, RealRNG

XoshiroParameters = tuple[int, int, int, int]


def rot(x: int, k: int, bit_size: int = 64) -> int:
    """
    Rotate x by k bits.

    Assumes modulo 2**bit_size.
    """
    return ((x << k) | (x >> (bit_size - k))) % 2**bit_size


def xoshiro(seed: XoshiroParameters) -> IntegerRNG:
    """Create a Xoshiro256** PRNG."""
    assert any(x != 0 for x in seed), "Seed can't be all zero"

    s0, s1, s2, s3 = seed

    while True:
        r = (rot((s1 * 5) % 2**64, 7) * 9) % 2**64
        t = (s1 << 17) % 2**64
        s2 ^= s0
        s3 ^= s1
        s1 ^= s2
        s0 ^= s3
        s2 ^= t
        s3 = rot(s3, 45)
        yield r


def xoshiro_real(seed: XoshiroParameters) -> RealRNG:
    """Create a Xoshiro256** PRNG with real values."""
    yield from (x_n / 2**64 for x_n in xoshiro(seed))


def reverse_xoshiro_parameters(gen: IntegerRNG) -> XoshiroParameters:
    """Reverse-engineer Xoshiro256** parameters."""
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
    return s0, s1, s2, s3


if __name__ == "__main__":

    def rand_u64() -> int:
        """Generate a random 64-bit unsigned integer."""
        return random.randint(0, 2**64 - 1)

    parameters = (rand_u64(), rand_u64(), rand_u64(), rand_u64())
    generator = xoshiro(parameters)

    reverse_parameters = reverse_xoshiro_parameters(generator)

    print(parameters)
    print(reverse_parameters)
    assert parameters == reverse_parameters
