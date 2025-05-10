import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Iterator
from contextlib import nullcontext
from itertools import islice, tee
from typing import TextIO

from seedseeker.generators import (
    FibonacciRng,
    Lcg,
    MersenneTwister,
    Ran3,
    Xoshiro,
    reverse_fibonacci,
    reverse_lcg,
    reverse_mersenne,
    reverse_ran3,
    reverse_xoshiro,
)
from seedseeker.utils.filestream import FileStream

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
    "mersenne": reverse_mersenne,
}


def main() -> None:
    """CLI entry point."""
    parser = ArgumentParser(
        description=(
            "Tool designed to infer the state of PRNG from a sequence of generated "
            "values"
        ),
        epilog=(
            "Please refer to the manpage for user guide, or the provided "
            "documentation for implementation details"
        ),
    )

    gen = parser.add_mutually_exclusive_group()

    gen.add_argument(
        "-g",
        "--generator",
        nargs=3,
        metavar=("<generator_name>", "<generator_state>", "<sequence_length>"),
        help=(
            "Generates <sequence_length> numbers by generator <generator_name> with "
            "initial state <generator_state>. Generator state format is specified in "
            "documentation"
        ),
    )

    gen.add_argument(
        "-fi", "--file-in", metavar="<filepath>", help="Reads numbers from file"
    )

    parser.add_argument(
        "-fo", "--file-out", metavar="<filepath>", help="Writes output to file"
    )

    parser.add_argument(
        "-len",
        "--length",
        metavar="<total>",
        help="Maximal length of the reversed sequence, overriden when -g is used.",
        default=1024,
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
    #                     help=("Displays a list of all available generators"
    #                     " and their state parameters"),
    #                     action="version",
    #                     version=f"{'\n'.join([f"{name}: {generator}" for
    #                       name, generator in GENERATORS.items()])}")

    args = parser.parse_args()

    if args.generator is not None:
        return run_from_generator(args)

    try:
        with (
            FileStream(args.file_in) as inp,
            open(args.file_out, "w")
            if args.file_out is not None
            else nullcontext(sys.stdout) as out,
        ):
            run_reversers(inp, out, int(args.length))
    except OSError:
        print(
            f"Error: File `{args.file_out}` does not exist or is not accessible",
            file=sys.stderr,
        )
        sys.exit(2)


def run_from_generator(args: Namespace) -> None:
    """Run all reversers on sequence from given generator."""
    generator, parameters, count = args.generator

    if generator not in GENERATORS:
        print(f"Error: Unknown generator {generator}", file=sys.stderr)
        sys.exit(1)

    try:
        inp = GENERATORS[generator].from_string(parameters)
    except SyntaxError:
        print(f"Error in syntax of generator parameters {parameters}", file=sys.stderr)
        sys.exit(1)

    with (
        open(args.file_out, "w")
        if args.file_out is not None
        else nullcontext(sys.stdout) as out
    ):
        run_reversers(inp, out, int(count))


def run_reversers(inp: Iterator[int], out: TextIO, count: int) -> None:
    """Run all reversers on given input sequence and print the results."""
    input_iterators = tee(inp, len(REVERSERS))

    limited_iterators = [islice(iterator, count) for iterator in input_iterators]

    results = [
        (name, reverser(iterator))
        for iterator, (name, reverser) in zip(
            limited_iterators, REVERSERS.items(), strict=True
        )
    ]

    for name, result in results:
        print(f"{name}: {result}", file=out)
