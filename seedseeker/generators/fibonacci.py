from collections import deque
from itertools import islice

from mod import Mod

from defs import IntegerRNG, RealRNG


def fibonacci(r: int, s: int, seed: list[int], m: int) -> IntegerRNG:
    assert len(seed) == max(r, s), f"Seed must be of length {max(r, s)}"
    queue = deque(Mod(n, m) for n in seed)

    while True:
        value = queue[-r] + queue[-s]
        if value < queue[-r] or value < queue[-s]:
            value += 1
        yield int(value)
        queue.append(value)
        queue.popleft()


def fibonacci_real(r: int, s: int, seed: list[int], m: int) -> RealRNG:
    yield from (x_n / m for x_n in fibonacci(r, s, seed, m))


if __name__ == "__main__":
    r = 7
    s = 10
    seed = [1, 3, 6, 7, 9, 21, 12, 15, 18, 19]
    m = 32

    print(*islice(fibonacci(r, s, seed, m), 100), sep=", ")
