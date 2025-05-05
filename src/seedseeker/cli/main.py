from argparse import ArgumentParser
from itertools import islice, tee

from seedseeker.generators import (
    FibonacciRng,
    FileStream,
    Lcg,
    MersenneTwister,
    Ran3,
    Xoshiro,
    reverse_fibonacci,
    reverse_lcg,
    reverse_ran3,
    reverse_xoshiro,
)

VERSION = "1.0"

GENERATORS = {
    "fibonacci": FibonacciRng,
    "lcg": Lcg,
    "ran3": Ran3,
    "mersenne": MersenneTwister,
    "xoshiro": Xoshiro,
}

REVERSERS = {
    "fibonacci": reverse_fibonacci,
    "lcg": reverse_lcg,
    "ran3": reverse_ran3,
    "xoshiro": reverse_xoshiro,
}

DEFAULT_SEQUENCE_LENGTH = 100


def main() -> None:
    """CLI entry point."""
    import sys

    parser = ArgumentParser(
        description="Tool designed to infer the state of PRNG from a sequence of generated values",
        epilog="Please refer to the manpage for user guide, or the provided documentation for implementation details",
    )

    gen = parser.add_mutually_exclusive_group()

    gen.add_argument(
        "-g",
        "--generator",
        nargs=3,
        metavar=("<generator_name>", "<generator_state>", "<sequence_length>"),
        help="Generates <sequence_length> numbers by generator <generator_name> with initial state <generator_state>. Generator state format is specified in documentation",
    )

    gen.add_argument(
        "-fi", "--file-in", metavar=("<filepath>"), help="Reads numbers from file"
    )

    parser.add_argument(
        "-fo", "--file-out", metavar=("<filepath>"), help="Writes output to file"
    )

    parser.add_argument(
        "-len",
        "--length",
        metavar=("<total>"),
        help="Maximal length of the reversed sequence, overriden when -g is used. 0 = unlimited",
        default=0,
    )

    parser.add_argument(
        "-v",
        "--version",
        help="Program version",
        action="version",
        version=f"SeedSeeker {VERSION}",
    )

    # TODO: Determine if this will be a thing
    # parser.add_argument("-gl", "--generator-list",
    #                     help="Displays a list of all available generators and their state parameters",
    #                     action="version",
    #                     version=f"{'\n'.join([f"{name}: {generator}" for name, generator in GENERATORS.items()])}")

    args = parser.parse_args()

    inp = FileStream()
    out = sys.stdout
    err = sys.stderr

    if args.generator is not None:
        args.length = int(args.generator[2])

        g = args.generator[0]

        if g not in GENERATORS:
            sys.stderr.write(f"Unknown generator: {g}")
            sys.exit(1)

        pars = args.generator[1]

        try:
            inp = GENERATORS[g].from_string(pars)

        except SyntaxError:
            err.write(f"Error in syntax of generator parameters {pars}\n")

    elif args.file_in is not None:
        inp = FileStream(args.file_in)

    elif args.generator is None and args.file_in is None and args.length == 0:
        args.length = DEFAULT_SEQUENCE_LENGTH

    if args.file_out is not None:
        out = open(args.file_out)

    count = None if int(args.length) == 0 else int(args.length)

    # TODO: Reversing process

    iterators = tee(inp, len(REVERSERS))

    results = [
        (name, reverser(islice(iterator, count)))
        for iterator, (name, reverser) in zip(iterators, REVERSERS.items(), strict=True)
    ]

    [print(f"{name}: {state}") for name, state in results]

    out.write("Finished")
    out.close()
