from __future__ import annotations

import os
from typing import Any, Generator, TypeVar
from urllib.parse import SplitResult

from fsspec.implementations.zip import ZipFileSystem

import upath.core


class _ZipAccessor(upath.core._FSSpecAccessor):
    def __init__(self, parsed_url: SplitResult, **kwargs):

        self._fs = ZipFileSystem(f"{parsed_url.netloc}")

    def _format_path(self, path: upath.core.UPath):
        return super()._format_path(path).lstrip("/")


PT = TypeVar("PT", bound="ZipPath")


class ZipPath(upath.core.UPath):
    _default_accessor = _ZipAccessor

    @classmethod
    def _from_parts(
        cls: type[PT],
        args: list[str | os.PathLike],
        url: SplitResult | None = None,
        **kwargs: Any,
    ) -> PT:

        if url is not None:
            entire_url = url.netloc + url.path
            url_parts = entire_url.split("/")

            first_entry_having_extension = next(
                p for p in url_parts if ".zip" in p
            )

            _extension_end = entire_url.index(
                first_entry_having_extension
            ) + len(first_entry_having_extension)

            netloc = entire_url[:_extension_end]
            path = entire_url[_extension_end:]

            url = url._replace(path=path, netloc=netloc)
            args = [path]

        return super()._from_parts(args, url)

    def iterdir(self: PT) -> Generator[PT, None, None]:
        """Iterate over the files in this directory.  Does not yield any
        result for the special paths '.' and '..'.
        """

        if self.is_file():
            raise NotADirectoryError

        for name in self._accessor.listdir(self):
            # fsspec returns dictionaries
            if isinstance(name, dict):
                name = name.get("name")

                if name is not None:
                    name = name.rstrip("/")

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
