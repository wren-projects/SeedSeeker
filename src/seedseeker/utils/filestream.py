from __future__ import annotations

import sys
from collections.abc import Iterator
from typing import Any, TextIO, override


class FileStream(Iterator[int]):
    """Streams numbers from a file or stdin."""

    stream: TextIO | None
    path: str | None

    def __init__(self, path: str | None = None) -> None:
        """Read from file `path` if provided, otherwise from `stdin`."""
        self.path = path
        self.stream = None

    def __enter__(self) -> FileStream:
        """Enter context and open the stream."""
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

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Exit context and close stream."""
        assert self.stream is not None, "Must be used in context"
        if self.path is not None:
            self.stream.close()

    @override
    def __next__(self):
        """Next item."""
        assert self.stream is not None, "Muse be used in context"

        try:
            line = self.stream.readline().strip()
            if not line:
                raise StopIteration
            return int(line)
        except EOFError:
            raise StopIteration from None

    @override
    def __iter__(self) -> Iterator[int]:
        """Return the iterator."""
        return self
