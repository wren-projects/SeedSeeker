from __future__ import annotations

import sys
from collections.abc import Iterator
from typing import TextIO


class FileStream(Iterator[int]):
    """Streams numbers from a filestream."""

    stream: TextIO | None
    path: str | None

    def __init__(self, path: str | None = None) -> None:
        """Read from file on `path` if provided, otherwise read from `stdin`."""
        self.path = path

    def __enter__(self) -> FileStream:
        """Enter context and open stream."""
        if self.path is None:
            self.stream = sys.stdin
        else:
            try:
                self.stream = open(self.path)
            except OSError:
                print(
                    f"Error: File `{self.path}` does not exist or is not accessible",
                    file=sys.stderr,
                )
                sys.exit(2)

        return self

    def __exit__(self, exc_type: type, exc_value: any, traceback: any) -> None:
        """Exit context and close stream."""
        if self.path is not None:
            self.stream.close()

    def __next__(self):
        """Next item."""
        try:
            return int(self.stream.readline().strip())
        except EOFError as err:
            raise StopIteration from err

    def __iter__(self) -> Iterator[int]:
        """Return the iterator."""
        return self
