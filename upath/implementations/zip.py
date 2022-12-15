from __future__ import annotations

import re
from typing import TYPE_CHECKING, Generator, TypeVar
from urllib.parse import ParseResult

from fsspec.implementations.zip import ZipFileSystem

import upath.core

if TYPE_CHECKING:
    from urllib.parse import SplitResult


class _ZipAccessor(upath.core._FSSpecAccessor):
    def __init__(self, parsed_url: ParseResult, **kwargs):

        self._fs = ZipFileSystem(f"{parsed_url.netloc}")

    def _format_path(self, path: ZipPath):
        return super()._format_path(path).lstrip("/")


PT = TypeVar("PT", bound="ZipPath")
class ZipPath(upath.core.UPath):
    _default_accessor = _ZipAccessor

    def iterdir(self: PT) -> Generator[PT, None, None]:
        """Iterate over the files in this directory.  Does not yield any
        result for the special paths '.' and '..'.
        """
        if self.is_file():
            raise NotADirectoryError

        for name in self._accessor.listdir(self):
            # fsspec returns dictionaries
            if isinstance(name, dict):
                name = name.get("name").rstrip("/")

            if name == self.name: 
                continue

            if name in {".", ".."}:
                # Yielding a path object for these makes little sense
                continue
            # only want the path name with iterdir
            name = self._sub_path(name)
            yield self._make_child_relpath(name)

    def mkdir(
        self, mode: int = ..., parents: bool = ..., exist_ok: bool = ...
    ) -> None:
        raise NotImplementedError
