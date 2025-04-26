from itertools import islice

from seedseeker.generators import Lcg, MersenneTwister, fibonacci, ran3, xoshiro

GENERATORS = {
    "fibonacci": fibonacci,
    "lcg": Lcg,
    "ran3": ran3,
    "mersenne": MersenneTwister,
    "xoshiro": xoshiro,
}


def main() -> None:
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: seedseeker <generator>")
        sys.exit(1)

    generator = sys.argv[1]
    if generator not in GENERATORS:
        print(f"Unknown generator: {generator}")
        sys.exit(1)

    args = tuple(map(int, sys.argv[2:]))

    generator = GENERATORS[generator](*args)
    print(*islice(generator, 100), sep=", ")
