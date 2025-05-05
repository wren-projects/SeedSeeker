from __future__ import annotations
from seedseeker.defs import IntegerRNG
import sys
from typing import TextIO


FileStreamState = tuple[bool]


class FileStreamGenerator(IntegerRNG[FileStreamState]):
    """Streams numbers from a filestream."""

    stream: TextIO
    path: str

    def __init__(self, path: str = "") -> None:
        """Read from file on `path` if provided, otherwise read from `stdin`."""
        self.path = path

        if path == "":
            self.stream = sys.stdin

        else:
            try:
                self.stream = open(path)

            except OSError:
                sys.stderr.write(
                    f"Error: File `{path}` does not exist or it is not accessible"
                )
                sys.exit(2)

    def __next__(self):
        """Next item."""
        try:
            return int(self.stream.readline().strip())

        except EOFError as err:
            if self.path != "":
                self.stream.close()

            raise StopIteration from err

    def state(self) -> FileStreamState:
        """Return the inner state."""
        raise NotImplementedError

    @staticmethod
    def from_state(state: FileStreamState) -> FileStreamGenerator:
        """Set the inner state."""
        raise NotImplementedError

    @staticmethod
    def is_state_equal(state1: FileStreamState, state2: FileStreamState) -> bool:
        """Check if two states are equal."""
        raise NotImplementedError

    @staticmethod
    def from_string(string: str) -> FileStreamGenerator:
        """Create generator with states from parameter string."""
        raise NotImplementedError
