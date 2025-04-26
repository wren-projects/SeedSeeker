from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from itertools import islice

from mod import Mod

from seedseeker.defs import IntegerRNG

FibonacciState = tuple[int, int, int, list[int], bool, bool]


class FibonacciRng(IntegerRNG[FibonacciState]):
    """
    Additive Lagged Fibonacci PRNG.

    Uses the formula:
        Xₙ₊₁ = Xₙ₋ᵣ + Xₙ₋ₛ mod m
    """

    r: int
    s: int
    m: int
    queue: deque[Mod]
    with_carry: bool
    carry: bool

    def __init__(
        self, r: int, s: int, m: int, seed: list[int], with_carry: bool = True
    ) -> None:
        """Create an additive Lagged Fibonacci PRNG."""
        assert len(seed) == max(r, s), f"Seed must be of length max(r, s) ({max(r, s)})"

        # allow for r, s to be given in any order
        r, s = min(r, s), max(r, s)

        self.r = r
        self.s = s
        self.with_carry = with_carry

        self.queue = deque(Mod(n, m) for n in seed)
        self.carry = False

    def __next__(self) -> int:
        """Return the next value."""
        r, s = self.r, self.s

        value = self.queue[-r] + self.queue[-s] + self.carry

        # Check for "overflow" (in mod m) and set carry accordingly
        overflow = value < self.queue[-r] or value < self.queue[-s]
        self.carry = self.with_carry and overflow

        self.queue.popleft()
        self.queue.append(value)

        return int(value)

    def state(self) -> FibonacciState:
        """Return the inner state."""
        queue = [int(n) for n in self.queue]
        return self.r, self.s, self.m, queue, self.with_carry, self.carry

    @staticmethod
    def from_state(state: FibonacciState) -> FibonacciRng:
        """Create a new FibonacciRng from given state."""
        r, s, m, seed, with_carry, carry = state
        rng = FibonacciRng(r, s, m, seed, with_carry)
        rng.carry = carry
        return rng


def reverse_fibonacci(
    generator: Iterator[int], max_param: int = 1000
) -> FibonacciState | None:
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
                    output = r, s, assumed_mod, [], with_carry, False

    return output


if __name__ == "__main__":
    import random

    r = 3217
    s = 576
    m = 2**32
    carry = True
    seed = [random.randint(0, m) for _ in range(max(s, r))]

    PRNG = FibonacciRng(r, s, m, seed, carry)
    print(*islice(PRNG, 100), sep=", ")
    print(m, r, s, "with" if carry else "without", "carry")
    print(reverse_fibonacci(PRNG, 5000))
