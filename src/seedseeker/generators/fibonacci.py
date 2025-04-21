from __future__ import annotations

from collections import deque
from itertools import islice

from mod import Mod

from seedseeker.defs import IntegerRNG, RealRNG

FibonacciParameters = tuple[int, int, list[int], int, bool]


def fibonacci(
    r: int, s: int, m: int, seed: list[int], with_carry: bool = True
) -> IntegerRNG:
    """
    Create an additive Lagged Fibonacci PRNG.

    Uses the formula:
        X_{n+1} = X_{n-r} + X_{n-s} mod m
    """
    assert len(seed) == max(r, s), f"Seed must be of length max(r, s) ({max(r, s)})"
    queue = deque(Mod(n, m) for n in seed)
    carry = False
    while True:
        value = queue[-r] + queue[-s]

        if carry:
            value += 1
            carry = False
        # Check for "carry" (in mod m) and add carry
        if with_carry and (value < queue[-r] or value < queue[-s]):
            carry = True

        yield int(value)

        queue.append(value)
        queue.popleft()


def fibonacci_real(r: int, s: int, seed: list[int], m: int) -> RealRNG:
    """Create an additive Lagged Fibonacci PRNG with real values."""
    yield from (x_n / m for x_n in fibonacci(r, s, m, seed))


def reverse_fibonacci(
    generator: IntegerRNG, max_param: int = 1000
) -> FibonacciParameters | None:
    """Reverse enginner additive Lagged Fibonacci parameters."""
    # TODO: Handle also the seed
    data = list(islice(generator, max_param + 100))
    output = None
    for r in range(max_param):
        for s in range(1, r):
            assumed_mod = None
            with_carry = False
            for i in range(r, len(data)):
                new_assumed_mod = data[i - r] + data[i - s] - data[i]
                if abs(new_assumed_mod) <= 1:
                    continue

                if assumed_mod is None:
                    assumed_mod = new_assumed_mod
                    continue
                if assumed_mod == new_assumed_mod:
                    continue
                if new_assumed_mod - assumed_mod == 1:
                    assumed_mod = new_assumed_mod
                    with_carry = True
                    continue
                if new_assumed_mod - assumed_mod == -1:
                    with_carry = True
                    continue

                break
            else:
                print(
                    f"Found a good match M = {assumed_mod}, R = {r}, S = {s}, "
                    f"with{'' if with_carry else 'out'} carry"
                )
                assert assumed_mod is not None
                if output is None:
                    output = assumed_mod, r, s, with_carry

    return output


if __name__ == "__main__":
    import random

    r = 3217
    s = 576
    m = 2**32
    carry = True
    seed = [random.randint(0, m) for _ in range(max(s, r))]

    PRNG = fibonacci(r, s, m, seed, carry)
    print(*islice(PRNG, 100), sep=", ")
    print(m, r, s, "with" if carry else "without", "carry")
    print(reverse_fibonacci(PRNG, 5000))
