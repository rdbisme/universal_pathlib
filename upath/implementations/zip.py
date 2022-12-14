from __future__ import annotations

import re
from typing import TYPE_CHECKING, TypeVar
from urllib.parse import ParseResult

from fsspec.implementations.zip import ZipFileSystem

import upath.core

if TYPE_CHECKING:
    from urllib.parse import SplitResult


class _ZipAccessor(upath.core._FSSpecAccessor):
    def __init__(self, parsed_url: ParseResult, **kwargs):

        self._fs = ZipFileSystem(f"{parsed_url.netloc}")

    def _format_path(self, path: ZipPath):
        ret = re.sub(rf"^{path._url.netloc}", "", path.path)

        if not (ret):
            return "/"

        return ret.lstrip("/")


PT = TypeVar("PT", bound="ZipPath")
class ZipPath(upath.core.UPath):
    _default_accessor = _ZipAccessor

    @classmethod
    def _from_parts(cls, args, url=None, **kwargs):
        url_parts = url.path.split("/")
        zip_ext_index = (
            next(
                (
                    url_parts.index(part)
                    for part in url_parts
                    if part.split(".")[-1] == "zip"
                )
            )
            + 1
        )

        netloc = url.netloc + "/".join(url_parts[:zip_ext_index])

        path = "/".join(url_parts[zip_ext_index:])

        if path:
            path = "/" + path

        url = url._replace(path=path, netloc=netloc)

        return super()._from_parts(args, url, **kwargs)

    @classmethod
    def _format_parsed_parts(
        cls: type[PT],
        drv: str,
        root: str,
        parts: list[str],
        url: SplitResult | None = None,
        **kwargs: Any,
    ) -> str:
        if parts:
            join_parts = parts[1:] if parts[0] == "/" else parts
        else:
            join_parts = []
        if drv or root:
            path: str = drv + root + cls._flavour.join(join_parts)
        else:
            path = cls._flavour.join(join_parts)
        if not url:
            scheme: str = kwargs.get("scheme", "file")
            netloc: str = kwargs.get("netloc", "")
        else:
            scheme, netloc = url.scheme, url.netloc

        path = path.replace(netloc, "")
        scheme = scheme + ":"
        netloc = "//" + netloc if netloc else ""

        formatted = scheme + netloc + path
        return formatted

    def iterdir(self):
        for name in self._accessor.listdir(self):
            # fsspec returns dictionaries
            if isinstance(name, dict):
                name = name.get("name")
            if name in {".", ".."}:
                # Yielding a path object for these makes little sense
                continue
            # only want the path name with iterdir
            name = name.rstrip("/").split("/")[-1]
            name = self._sub_path(name)
            yield self._make_child_relpath(name)

    def mkdir(
        self, mode: int = ..., parents: bool = ..., exist_ok: bool = ...
    ) -> None:
        raise NotImplementedError
