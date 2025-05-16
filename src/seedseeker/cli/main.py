import sys
from argparse import Action, ArgumentParser, Namespace
from contextlib import nullcontext
from itertools import islice
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


class GeneratorAction(Action):
    """Custom action to parse generator arguments."""

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: list[str],
        option_string: str | None = None,
    ):
        """Parse generator arguments."""
        if len(values) != 3:
            parser.error(
                f"{option_string} requires exactly 3 arguments,"
                f" but {len(values)} were given."
            )
        setattr(namespace, self.dest, values)


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
        nargs="*",
        metavar=("<name>", "<arguments>", "<count>"),
        # action=GeneratorAction,
        help=(
            "Generate a sequence of numbers from a generator with given arguments. "
            "Either takes the values directly, or if none are supplied, reads them "
            "from stdin or file (see -i)"
        ),
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

    parser.add_argument(
        "-i", "--input", metavar="<file>", help="Reads numbers from file"
    )

    parser.add_argument(
        "-o", "--output", metavar="<file>", help="Writes output to file"
    )

    parser.add_argument(
        "-len",
        "--length",
        metavar="<total>",
        help=(
            "Length of the sequence to reverse or predict. Defaults to 1024 or 16"
            " respectively"
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
        generate_numbers(inp, out, args)
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
    sequence = list(islice(map(int, inp), int_or_default(limit, 1024)))

    found = False
    for name, reverser in REVERSERS.items():
        if (state := reverser(iter(sequence))) is not None:
            print(f"{name} {state}", file=out)
            found = True

    if not found:
        print("Error: No matching generator state found", file=sys.stderr)
        sys.exit(1)


def generate_numbers(inp: FileStream, out: TextIO, args: Namespace) -> None:
    """Generate numbers from given generator args."""
    if args.generator:
        name, parameters, count = args.generator

        if name not in GENERATORS:
            print(f"Error: Unknown generator {name}", file=sys.stderr)
            sys.exit(1)

        print(
            *islice(GENERATORS[name].from_string(parameters), int(count)),
            file=out,
            sep="\n",
        )

        return

    for line in inp:
        name, parameters, count = line.split()

        if name not in GENERATORS:
            print(f"Error: Unknown generator {name}", file=sys.stderr)
            sys.exit(1)

        print(
            *islice(GENERATORS[name].from_string(parameters), int(count)),
            file=out,
            sep=";",
        )


def predict_numbers(inp: FileStream, out: TextIO, count: int | None) -> None:
    """Predict numbers from saved states."""
    limit = int_or_default(count, 16)

    for line in inp:
        name, args = line.split()

        if name not in GENERATORS:
            print(f"Error: Unknown reverser {name}", file=sys.stderr)
            sys.exit(1)

        generator_class = GENERATORS[name]

        state = generator_class.state_from_string(args)

        print(*islice(generator_class.from_state(state), limit), file=out, sep=";")
