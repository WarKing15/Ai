"""
The LocalFileWorkspace class implements a AbstractFileWorkspace that works with local files.
"""
from __future__ import annotations

import inspect
from pathlib import Path

from .base import AbstractFileWorkspace, AbstractFileWorkspaceConfiguration

LOG =  AFAASLogger(name=__name__)


class AGPTLocalFileWorkspace(AbstractFileWorkspace):
    """A class that represents a file workspace."""

    def __init__(self, config: AbstractFileWorkspaceConfiguration):
        self._root = self._sanitize_path(config.root)
        self._restrict_to_root = config.restrict_to_root
        super().__init__()

    @property
    def root(self) -> Path:
        """The root directory of the file workspace."""
        return self._root

    @property
    def restrict_to_root(self):
        """Whether to restrict generated paths to the root."""
        return self._restrict_to_root

    def initialize(self) -> None:
        self.root.mkdir(exist_ok=True, parents=True)

    def open_file(self, path: str | Path, mode: str = "r"):
        """Open a file in the workspace."""
        full_path = self.get_path(path)
        return open(full_path, mode)

    def read_file(self, path: str | Path, binary: bool = False):
        """Read a file in the workspace."""
        with self.open_file(path, "rb" if binary else "r") as file:
            return file.read()

    async def _write_file(self, path: str | Path, content: str | bytes):
        """Write to a file in the workspace."""
        with self.open_file(path, "wb" if type(content) is bytes else "w") as file:
            file.write(content)

    def list_files(self, path: str | Path = "."):
        """List all files in a directory in the workspace."""
        full_path = self.get_path(path)
        return [str(file) for file in full_path.glob("*") if file.is_file()]

    def delete_file(self, path: str | Path):
        """Delete a file in the workspace."""
        full_path = self.get_path(path)
        full_path.unlink()
