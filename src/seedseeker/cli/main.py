import sys
from argparse import ArgumentParser, Namespace
from contextlib import nullcontext
from itertools import islice
from typing import TextIO

from seedseeker.defs import InvalidFormatError
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

    command_group = parser.add_mutually_exclusive_group()

    command_group.add_argument(
        "-g",
        "--generator",
        metavar=("<name>", "<arguments>"),
        nargs=2,
        help="Generate a sequence of numbers from a generator with given arguments.",
    )

    command_group.add_argument(
        "-p",
        "--predict",
        metavar="<count>",
        help="Number of values to predict. Reads saved states from input.",
    )

    command_group.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help=(
            "Reverses the given sequence of numbers and prints all matching generator"
            " states"
        ),
    )

    parser.add_argument("-i", "--input", metavar="<file>", help="Reads input from file")

    parser.add_argument(
        "-o", "--output", metavar="<file>", help="Writes output to file"
    )

    parser.add_argument(
        "-l",
        "--length",
        metavar="<total>",
        help=(
            "Length of the sequence to reverse or generate/predict. Defaults to 1024"
            " or 16 respectively"
        ),
    )

    parser.add_argument(
        "-v",
        "--version",
        help="Program version",
        action="version",
        version=f"SeedSeeker {VERSION}",
    )

    args = parser.parse_args()

    try:
        with (
            FileStream(args.input) as inp,
            open(args.output, "w")
            if args.output is not None
            else nullcontext(sys.stdout) as out,
        ):
            run_with_io(inp, out, args)
    except OSError:
        print(
            f"Error: File `{args.output}` does not exist or is not accessible",
            file=sys.stderr,
        )
        sys.exit(2)


def run_with_io(inp: FileStream, out: TextIO, args: Namespace) -> None:
    """Run the program with given IO."""
    if args.generator is not None:
        generate_numbers(out, args)
    elif args.reverse:
        reverse_sequence(inp, out, args.length)
    elif args.predict is not None:
        predict_numbers(inp, out, args.length)
    else:
        print("Error: No command given", file=sys.stderr)
        sys.exit(1)


def int_or_default(value: any, default: int) -> int:
    """Convert value to int if possible, otherwise return default."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def reverse_sequence(inp: FileStream, out: TextIO, limit: str | None) -> None:
    """Reverse the sequence and print all matching generator states."""
    try:
        sequence = list(islice(map(int, inp), int_or_default(limit, 1024)))
    except ValueError as e:
        raise InvalidFormatError("Found non-integer value in input sequence") from e

    found = False
    for name, reverser in REVERSERS.items():
        if (state := reverser(iter(sequence))) is not None:
            print(f"{name} {state}", file=out)
            found = True

    if not found:
        print("Error: No matching generator state found", file=sys.stderr)
        sys.exit(1)


def generate_numbers(out: TextIO, args: Namespace) -> None:
    """Generate numbers from given generator args."""
    name, parameters = args.generator

    count = int_or_default(args.length, 16)

    if name not in GENERATORS:
        print(f"Error: Unknown generator {name}", file=sys.stderr)
        sys.exit(1)

    try:
        print(
            *islice(GENERATORS[name].from_string(parameters), count),
            file=out,
            sep="\n",
        )
    except (InvalidFormatError, AssertionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def predict_numbers(inp: FileStream, out: TextIO, count: int | None) -> None:
    """Predict numbers from saved states."""
    limit = int_or_default(count, 16)

    for line in inp:
        name, args = line.split()

        if name not in GENERATORS:
            print(f"Error: Unknown reverser {name}", file=sys.stderr)
            sys.exit(1)

        generator_class = GENERATORS[name]

        try:
            state = generator_class.state_from_string(args)
        except InvalidFormatError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        print(*islice(generator_class.from_state(state), limit), file=out, sep=";")
