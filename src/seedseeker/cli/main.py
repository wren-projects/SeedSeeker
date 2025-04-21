from itertools import islice

from seedseeker.generators import doom, fibonacci, lcg, mersenne_twister, ran3, xoshiro

GENERATORS = {
    "doom": doom,
    "fibonacci": fibonacci,
    "lcg": lcg,
    "ran3": ran3,
    "mersenne": mersenne_twister,
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
