"""
The FileStorage class provides an interface for interacting with a file storage.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from io import IOBase, TextIOBase
from pathlib import Path
from typing import IO, Any, BinaryIO, Callable, Literal, Optional, TextIO, overload

from autogpt.core.configuration.schema import SystemConfiguration

logger = logging.getLogger(__name__)


class FileStorageConfiguration(SystemConfiguration):
    restrict_to_root: bool = True
    root: Path = Path("/")


class FileStorage(ABC):
    """A class that represents a file storage."""

    on_write_file: Callable[[Path], Any] | None = None
    """
    Event hook, executed after writing a file.

    Params:
        Path: The path of the file that was written, relative to the storage root.
    """

    @property
    @abstractmethod
    def root(self) -> Path:
        """The root path of the file storage."""

    @property
    @abstractmethod
    def restrict_to_root(self) -> bool:
        """Whether to restrict file access to within the storage's root path."""

    @abstractmethod
    def initialize(self) -> None:
        """
        Calling `initialize()` should bring the storage to a ready-to-use state.
        For example, it can create the resource in which files will be stored, if it
        doesn't exist yet. E.g. a folder on disk, or an S3 Bucket.
        """

    @overload
    @abstractmethod
    def open_file(
        self, path: str | Path, binary: Literal[False] = False
    ) -> TextIO | TextIOBase:
        """Returns a readable text file-like object representing the file."""

    @overload
    @abstractmethod
    def open_file(
        self, path: str | Path, binary: Literal[True] = True
    ) -> BinaryIO | IOBase:
        """Returns a readable binary file-like object representing the file."""

    @abstractmethod
    def open_file(self, path: str | Path, binary: bool = False) -> IO | IOBase:
        """Returns a readable file-like object representing the file."""

    @overload
    @abstractmethod
    def read_file(self, path: str | Path, binary: Literal[False] = False) -> str:
        """Read a file in the storage as text."""
        ...

    @overload
    @abstractmethod
    def read_file(self, path: str | Path, binary: Literal[True] = True) -> bytes:
        """Read a file in the storage as binary."""
        ...

    @abstractmethod
    def read_file(self, path: str | Path, binary: bool = False) -> str | bytes:
        """Read a file in the storage."""

    @abstractmethod
    async def write_file(self, path: str | Path, content: str | bytes) -> None:
        """Write to a file in the storage."""

    @abstractmethod
    def list(self, path: str | Path = ".") -> list[Path]:
        """List all files (recursively) in a directory in the storage."""

    @abstractmethod
    def list_folders(self, path: str | Path = ".", recursive: bool = False) -> list[Path]:
        """List all folders in a directory in the storage."""

    @abstractmethod
    def delete_file(self, path: str | Path) -> None:
        """Delete a file in the storage."""

    @abstractmethod
    def exists(self, path: str | Path) -> bool:
        """Check if a file or folder exists in the storage."""

    @abstractmethod
    def make_dir(self, path: str | Path) -> None:
        """Create a directory in the storage if doesn't exist."""

    def get_path(self, relative_path: str | Path) -> Path:
        """Get the full path for an item in the storage.

        Parameters:
            relative_path: The relative path to resolve in the storage.

        Returns:
            Path: The resolved path relative to the storage.
        """
        return self._sanitize_path(relative_path, self.root)

    @staticmethod
    def _sanitize_path(
        relative_path: str | Path,
        root: Optional[str | Path] = None,
        restrict_to_root: bool = True,
    ) -> Path:
        """Resolve the relative path within the given root if possible.

        Parameters:
            relative_path: The relative path to resolve.
            root: The root path to resolve the relative path within.
            restrict_to_root: Whether to restrict the path to the root.

        Returns:
            Path: The resolved path.

        Raises:
            ValueError: If the path is absolute and a root is provided.
            ValueError: If the path is outside the root and the root is restricted.
        """

        # Posix systems disallow null bytes in paths. Windows is agnostic about it.
        # Do an explicit check here for all sorts of null byte representations.

        if "\0" in str(relative_path) or "\0" in str(root):
            raise ValueError("embedded null byte")

        if root is None:
            return Path(relative_path).resolve()

        logger.debug(f"Resolving path '{relative_path}' in storage '{root}'")

        root, relative_path = Path(root).resolve(), Path(relative_path)

        logger.debug(f"Resolved root as '{root}'")

        # Allow absolute paths if they are contained in the storage.
        if (
            relative_path.is_absolute()
            and restrict_to_root
            and not relative_path.is_relative_to(root)
        ):
            raise ValueError(
                f"Attempted to access absolute path '{relative_path}' "
                f"in storage '{root}'."
            )

        full_path = root.joinpath(relative_path).resolve()

        logger.debug(f"Joined paths as '{full_path}'")

        if restrict_to_root and not full_path.is_relative_to(root):
            raise ValueError(
                f"Attempted to access path '{full_path}' outside of storage '{root}'."
            )

        return full_path
