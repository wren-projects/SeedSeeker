from collections import deque
from itertools import islice

from mod import Mod

from defs import IntegerRNG, RealRNG


def fibonacci(
    r: int, s: int, seed: list[int], m: int, withCarry: bool = True
) -> IntegerRNG:
    assert len(seed) == max(r, s), f"Seed must be of length max(r, s) ({max(r, s)})"
    queue = deque(Mod(n, m) for n in seed)
    carry = False
    while True:
        value = queue[-r] + queue[-s]

        if carry:
            value += 1
            carry = False
        # Check for "carry" (in mod m) and add carry
        if withCarry and (value < queue[-r] or value < queue[-s]):
            carry = True

        yield int(value)

        queue.append(value)
        queue.popleft()


def fibonacci_real(r: int, s: int, seed: list[int], m: int) -> RealRNG:
    yield from (x_n / m for x_n in fibonacci(r, s, seed, m))


def reverse_fibonacci(
    generator: IntegerRNG, maxParam: int = 1000
) -> None | tuple[int, int, int, bool]:
    """
    reverses configuration fibonacci PRNG that relies on addion of 2 elements

    Configuration consists of M, R, S, C in Fibonacci PRNG given by the formula:
    a(i) = (a(i-R) + a(i-S))%M

    Sometimes, a carry is added to the formula. C is a boolean representing if the PRNG uses carry.
    """
    data = list(islice(generator, maxParam + 100))
    output = None
    for r in range(maxParam):
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
                    f"Found a good match M = {assumed_mod}, R = {r}, S = {s}, with{'' if with_carry else 'out'} carry"
                )
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

    PRNG = fibonacci(r, s, seed, m, carry)
    print(*islice(PRNG, 10000), sep=", ")
    print(m, r, s, "with" if carry else "without", "carry")
    print(reverse_fibonacci(PRNG, 5000), sep=", ")
