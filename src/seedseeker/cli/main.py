import argparse
from itertools import islice

from seedseeker.generators import (
    FibonacciRng,
    Lcg,
    MersenneTwister,
    Ran3,
    Xoshiro,
)
from seedseeker.generators import FileStream as FileStreamGenerator

VERSION = "1.0"

GENERATORS = {
    "fibonacci": FibonacciRng,
    "lcg": Lcg,
    "ran3": Ran3,
    "mersenne": MersenneTwister,
    "xoshiro": Xoshiro,
}

DEFAULT_SEQUENCE_LENGTH = 100

def main() -> None:
    """CLI entry point."""
    import sys
    
    parser = argparse.ArgumentParser(description="Tool designed to reverse-engineer the state of PRNG from a sequence of generated values", 
                                     epilog="Please refer to the manpage for user guide, or the provided documentation for implementation details",
                                     )
    gen = parser.add_mutually_exclusive_group()

    gen.add_argument("-g", "--generator", 
                        nargs=3,
                        metavar=("<generator_name>", "<generator_state>", "<sequence_length>"),
                        help="Generates <sequence_length> numbers by generator <generator_name> with state <generator_state>. Generator state is a series of parameters separated by commas")

    gen.add_argument("-fi", "--file-in", 
                        metavar=("<filepath>"),
                        help="Reads numbers from file")

    parser.add_argument("-fo", "--file-out", 
                        metavar=("<filepath>"),
                        help="Writes output to file")

    parser.add_argument("-len", "--length", 
                        metavar=("<total>"),
                        help="Maximal length of the reversed sequence, overriden when -g is used. 0 = unlimited",
                        default=0)

    parser.add_argument("-v", "--version",
                        help="Program version", 
                        action="version", 
                        version=f"SeedSeeker {VERSION}")

    # TODO: Determine if this will be a thing
    # parser.add_argument("-gl", "--generator-list",
    #                     help="Displays a list of all available generators and their state parameters",
    #                     action="version", 
    #                     version=f"{'\n'.join([f"{name}: {generator}" for name, generator in GENERATORS.items()])}")

    args = parser.parse_args()

    inp = FileStreamGenerator()
    out = sys.stdout

    if args.generator is not None:
        args.length = int(args.generator[2])
        
        g = args.generator[0]
        
        if g not in GENERATORS:
            sys.stderr.write(f"Unknown generator: {g}")
            sys.exit(1)
            
        pars = tuple([int(par.strip()) for par in args.generator[1].split(',')])
        inp = GENERATORS[g](*pars)
        
    elif args.file_in is not None:
        inp = FileStreamGenerator(args.file_in)
        
    elif args.generator is None and args.file_in is None and args.length == 0:
        args.length = DEFAULT_SEQUENCE_LENGTH
        
    if args.file_out is not None:
        out = open(args.file_out)
        
    count = None if int(args.length) == 0 else int(args.length)
    
    # TODO: Reversing process
    
    # Temporary
    print(args)
    print()
    print(*islice(inp, count), sep=", ")
