from __future__ import annotations

import sys
from collections.abc import Iterator
from typing import TextIO


class FileStreamGenerator(Iterator[int]):
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

    def __iter__(self) -> Iterator[int]:
        """Return the iterator."""
        return self
