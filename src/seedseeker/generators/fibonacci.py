from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from itertools import islice
from sys import stderr
from typing import NamedTuple, override

from mod import Mod

from seedseeker.defs import IntegerRNG
from seedseeker.generators.lcg import Lcg
from seedseeker.utils.iterator import BufferingIterator, CountingIterator, drop


class FibonacciState(NamedTuple):
    """State of an additive Lagged Fibonacci PRNG."""

    r: int
    s: int
    m: int
    seed: list[int]
    carry: bool | None

    def __str__(self) -> str:
        """Print state as string."""
        return f"{self.r};{self.s};{self.m};{self.seed};{self.carry}"


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
    carry: bool | None

    DEFAULT_SEED: int = 19780503

    def __init__(
        self, r: int, s: int, m: int, seed: list[int] | int = 0, with_carry: bool = True
    ) -> None:
        """Create an additive Lagged Fibonacci PRNG."""
        if isinstance(seed, int):
            assert seed >= 0, "Seed must be non-negative"
            seed = seed % 2147483563 if seed != 0 else FibonacciRng.DEFAULT_SEED
            seed = list(islice(Lcg(2147483563, 40014, 0, seed), max(r, s)))
        else:
            assert len(seed) == max(r, s), (
                f"Seed must be of length max(r, s) ({max(r, s)})"
            )
            assert all(n >= 0 for n in seed), "All seed values must be non-negative"

        # allow for r, s to be given in any order
        r, s = min(r, s), max(r, s)

        self.r = r
        self.s = s
        self.m = m

        self.queue = deque(Mod(n, m) for n in seed)
        self.carry = False if with_carry else None

    @override
    def __next__(self) -> int:
        """Return the next value."""
        r, s = self.r, self.s

        value = self.queue[-r] + self.queue[-s] + int(self.carry is True)

        if self.carry is not None:
            # Check for "overflow" (in mod m) and set carry accordingly
            self.carry = value < self.queue[-r] or value < self.queue[-s]

        self.queue.popleft()
        self.queue.append(value)

        return int(value)

    @override
    def state(self) -> FibonacciState:
        """Return the inner state."""
        queue = [int(n) for n in self.queue]
        return FibonacciState(self.r, self.s, self.m, queue, self.carry)

    @override
    @staticmethod
    def from_state(state: FibonacciState) -> FibonacciRng:
        """Create a new FibonacciRng from given state."""
        r, s, m, seed, carry = state
        rng = FibonacciRng(r, s, m, seed, carry is not None)
        rng.carry = carry
        return rng

    @override
    @staticmethod
    def is_state_equal(state1: FibonacciState, state2: FibonacciState) -> bool:
        """Check if two FibonacciRng states are equal."""
        return state1 == state2

    @override
    @staticmethod
    def from_string(string: str) -> FibonacciRng:
        """Create generator with states from parameter string."""
        params = string.split(";")

        if len(params) < 4:
            raise SyntaxError

        r, s, m = map(int, params[:3])

        try:
            seed = int(params[3])
        except ValueError:
            seed = list(map(int, params[3].strip("[]").split(",")))

        carry = True

        if len(params) >= 5:
            carry_param = params[4]

            match carry_param.lower():
                case "false":
                    carry = False
                case "true":
                    carry = True
                case _:
                    stderr.write(
                        f"Warning: Invalid carry value {carry_param}, setting to True"
                    )
                    carry = True

        return FibonacciRng(r, s, m, seed, carry)

    @override
    @staticmethod
    def state_from_string(string: str) -> FibonacciState:
        # f"{self.r};{self.s};{self.m};{self.seed};{self.carry}"
        r, s, m, seed, carry = string.split(";")

        r, s, m = map(int, [r, s, m])
        seed = list(map(int, seed.strip("[]").split(",")))

        match carry:
            case "False":
                carry = False
            case "True":
                carry = True
            case _:
                carry = None

        return FibonacciState(r, s, m, seed, carry)


# upper bound on the parameter r
MAX_LAG = 1000
VALUES_NEEDED = 5


def reverse_fibonacci(generator: Iterator[int]) -> FibonacciState | None:
    """Reverse enginner additive Lagged Fibonacci parameters."""
    counting = CountingIterator(generator)
    buff = BufferingIterator(counting)
    drop(buff, MAX_LAG + VALUES_NEEDED)
    data = list(buff.buffer)

    for s in range(counting.count - VALUES_NEEDED):
        for r in range(1, s):
            assumed_mod = None
            with_carry = False

            for i in range(s, len(data)):
                new_assumed_mod = data[i - s] + data[i - r] - data[i]
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
                if assumed_mod is None:
                    # probably not an additive lagged fibonacci sequence
                    return None

                carry = data[-1 - s] + data[-1 - r] >= assumed_mod

                return FibonacciState(
                    r, s, assumed_mod, data[-max(s, r) :], carry if with_carry else None
                )

    return None
