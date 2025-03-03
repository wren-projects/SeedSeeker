from itertools import cycle, islice
from defs import IntegerRNG
from lcg import lcg


def doom() -> IntegerRNG:
    """
    Original Doom's PRNG based on a LCG

    See:
        https://doomwiki.org/wiki/Pseudorandom_number_generator
    """
    m = 1 << 24
    a = 134775813 % m
    c = 1
    seed = 1
    yield from cycle(n >> 16 for n in islice(lcg(m, a, c, seed), 256))


if __name__ == "__main__":
    print(*islice(doom(), 260), sep=", ")
