"""流式文件下载与断点续传工具（替代 _vendor/download.py，默认基于 _request/httpx）。"""

from __future__ import annotations

import errno
from asyncio import to_thread
from collections.abc import AsyncGenerator, Callable, Generator
from os import PathLike, fsdecode, fstat, makedirs
from os.path import abspath, dirname, isdir
from os.path import join as joinpath
from shutil import COPY_BUFSIZE
from typing import Any, NamedTuple, cast

from fundrives.pan115._http import (
    get_filename,
    get_length,
    is_chunked,
    is_range_request,
)
from fundrives.pan115._request import request_async, request_sync
from fundrives.pan115._vendor.asynctools import ensure_aiter, ensure_async
from fundrives.pan115._vendor.filewrap import (
    SupportsWrite,
    bio_chunk_async_iter,
    bio_chunk_iter,
    bio_skip_async_iter,
    bio_skip_iter,
)

__all__ = [
    "DownloadProgress",
    "download",
    "download_async",
    "download_async_iter",
    "download_iter",
]


def _default_iter_bytes(resp: Any) -> Any:
    return bio_chunk_iter(resp, chunksize=COPY_BUFSIZE)


def _default_async_iter_bytes(resp: Any) -> Any:
    return bio_chunk_async_iter(resp, chunksize=COPY_BUFSIZE)


def _default_urlopen(url: str, *, headers: dict[str, str] | None = None) -> Any:
    return request_sync(url, headers=headers, parse=None)


async def _default_async_urlopen(
    url: str, *, headers: dict[str, str] | None = None
) -> Any:
    return await request_async(url, headers=headers, parse=None)


class DownloadProgress(NamedTuple):
    total: int
    downloaded: int
    skipped: int
    last_increment: int = 0
    extra: Any = None

    @property
    def completed(self, /) -> int:
        return self.downloaded + self.skipped

    @property
    def remaining(self, /) -> int:
        return max(0, self.total - self.completed)

    @property
    def ratio(self, /) -> float:
        return self.completed / self.total

    @property
    def task_done(self, /) -> bool:
        return self.completed >= self.total


def _open_dst(
    file: Any, resp: Any, resume: bool
) -> tuple[Any, SupportsWrite[bytes], bool]:
    if hasattr(file, "write"):
        return file, cast(SupportsWrite[bytes], file), False
    path = abspath(fsdecode(file))
    if isdir(path):
        path = joinpath(path, get_filename(resp, "download"))
    mode = "ab" if resume else "wb"
    try:
        fdst = open(path, mode)  # noqa: SIM115
    except FileNotFoundError:
        makedirs(dirname(path), exist_ok=True)
        fdst = open(path, mode)  # noqa: SIM115
    return path, cast(SupportsWrite[bytes], fdst), True


def download_iter(
    url: str | Callable[[], str],
    file: bytes | str | PathLike[Any] | SupportsWrite[bytes] = "",
    resume: bool = False,
    chunksize: int = COPY_BUFSIZE,
    headers: dict[str, str] | Callable[[], dict[str, str]] | None = None,
    urlopen: Callable[..., Any] = _default_urlopen,
    iter_bytes: Callable[[Any], Any] = _default_iter_bytes,
) -> Generator[DownloadProgress]:
    resolved_url = url() if callable(url) else url
    hdrs: dict[str, str] = (
        headers() if callable(headers) else (dict(headers) if headers else {})
    )
    if type(resolved_url) is not str and (
        extra_hdrs := getattr(resolved_url, "headers", None)
    ):
        hdrs.update(extra_hdrs)
    hdrs["Accept-Encoding"] = "identity"

    resp = urlopen(resolved_url, headers=hdrs)
    close_file = False
    fdst: Any = None
    try:
        length = get_length(resp)
        if length == 0 and is_chunked(resp):
            length = None
        target, fdst, close_file = _open_dst(file, resp, resume)
        extra = {"url": resolved_url, "file": target, "resume": resume}

        filesize = 0
        if resume:
            try:
                filesize = fstat(fdst.fileno()).st_size
            except (AttributeError, OSError):
                pass
            else:
                if filesize == length:
                    yield DownloadProgress(length, 0, length, length, extra)
                    return
                if length is not None and filesize > length:
                    raise OSError(
                        errno.EIO,
                        f"file {target!r} is larger than url {resolved_url!r}: "
                        f"{filesize} > {length} (in bytes)",
                    )
        elif length == 0:
            yield DownloadProgress(0, 0, 0, 0, extra)
            return

        if filesize and is_range_request(resp):
            resp.close()
            resp = urlopen(
                resolved_url, headers={**hdrs, "Range": f"bytes={filesize}-"}
            )
            if not is_range_request(resp):
                raise OSError(errno.EIO, f"range request failed: {resolved_url!r}")

        yield DownloadProgress(length or 0, 0, 0, 0, extra)

        length_downloaded = 0
        length_skipped = 0
        if filesize:
            if is_range_request(resp):
                length_skipped = filesize
                yield DownloadProgress(
                    length or length_skipped, 0, length_skipped, length_skipped, extra
                )
            else:
                for skiplen in bio_skip_iter(resp, filesize):
                    length_skipped += skiplen
                    yield DownloadProgress(
                        length or length_skipped, 0, length_skipped, skiplen, extra
                    )

        for chunk in iter_bytes(resp):
            fdst.write(chunk)
            downlen = len(chunk)
            length_downloaded += downlen
            yield DownloadProgress(
                length or (length_skipped + length_downloaded),
                length_downloaded,
                length_skipped,
                downlen,
                extra,
            )
    finally:
        resp.close()
        if close_file and fdst is not None:
            fdst.close()


def download(
    url: str | Callable[[], str],
    file: bytes | str | PathLike[Any] | SupportsWrite[bytes] = "",
    resume: bool = False,
    chunksize: int = COPY_BUFSIZE,
    headers: dict[str, str] | Callable[[], dict[str, str]] | None = None,
    urlopen: Callable[..., Any] = _default_urlopen,
    iter_bytes: Callable[[Any], Any] = _default_iter_bytes,
    make_reporthook: Callable[[int | None], Any] | None = None,
) -> DownloadProgress:
    update: Callable[[int], Any] | None = None
    close: Callable[[], Any] | None = None
    download_gen = download_iter(
        url,
        file,
        resume=resume,
        chunksize=chunksize,
        headers=headers,
        urlopen=urlopen,
        iter_bytes=iter_bytes,
    )
    progress = DownloadProgress(0, 0, 0)
    try:
        if make_reporthook is not None:
            progress = next(download_gen)
            reporthook = make_reporthook(progress.total)
            if isinstance(reporthook, Generator):
                next(reporthook)
                update = reporthook.send
                close = reporthook.close
            else:
                update = reporthook
                close = getattr(reporthook, "close", None)
            if update is not None:
                update(progress.last_increment)
        if update is None:
            for item in download_gen:
                progress = item
        else:
            for progress in download_gen:
                update(progress.last_increment)
        return progress
    finally:
        download_gen.close()
        if close is not None:
            close()


async def download_async_iter(
    url: str | Callable[[], Any],
    file: bytes | str | PathLike[Any] | SupportsWrite[bytes] = "",
    resume: bool = False,
    chunksize: int = COPY_BUFSIZE,
    headers: dict[str, str] | Callable[[], Any] | None = None,
    urlopen: Callable[..., Any] = _default_async_urlopen,
    iter_bytes: Callable[[Any], Any] = _default_async_iter_bytes,
) -> AsyncGenerator[DownloadProgress]:
    resolved_url = await ensure_async(url)() if callable(url) else url
    if callable(headers):
        hdrs: dict[str, str] = await ensure_async(headers)()
    elif headers:
        hdrs = dict(headers)
    else:
        hdrs = {}
    if type(resolved_url) is not str and (
        extra_hdrs := getattr(resolved_url, "headers", None)
    ):
        hdrs.update(extra_hdrs)
    hdrs["Accept-Encoding"] = "identity"

    open_fn = ensure_async(urlopen)
    resp = await open_fn(resolved_url, headers=hdrs)
    close_file = False
    fdst: Any = None
    try:
        length = get_length(resp)
        if length == 0 and is_chunked(resp):
            length = None
        target, fdst, close_file = _open_dst(file, resp, resume)
        extra = {"url": resolved_url, "file": target, "resume": resume}

        filesize = 0
        if resume:
            try:
                filesize = fstat(fdst.fileno()).st_size
            except (AttributeError, OSError):
                pass
            else:
                if filesize == length:
                    yield DownloadProgress(length, 0, length, length, extra)
                    return
                if length is not None and filesize > length:
                    raise OSError(
                        errno.EIO,
                        f"file {target!r} is larger than url {resolved_url!r}: "
                        f"{filesize} > {length} (in bytes)",
                    )
        elif length == 0:
            yield DownloadProgress(0, 0, 0, 0, extra)
            return

        if filesize and is_range_request(resp):
            if hasattr(resp, "aclose"):
                await resp.aclose()
            else:
                await ensure_async(resp.close)()
            resp = await open_fn(
                resolved_url, headers={**hdrs, "Range": f"bytes={filesize}-"}
            )
            if not is_range_request(resp):
                raise OSError(errno.EIO, f"range request failed: {resolved_url!r}")

        yield DownloadProgress(length or 0, 0, 0, 0, extra)

        length_downloaded = 0
        length_skipped = 0
        fdst_write = ensure_async(fdst.write)
        if filesize:
            if is_range_request(resp):
                length_skipped = filesize
                yield DownloadProgress(
                    length or length_skipped, 0, length_skipped, length_skipped, extra
                )
            else:
                async for skiplen in bio_skip_async_iter(resp, filesize):
                    length_skipped += skiplen
                    yield DownloadProgress(
                        length or length_skipped, 0, length_skipped, skiplen, extra
                    )

        async for chunk in ensure_aiter(iter_bytes(resp)):
            await fdst_write(chunk)
            downlen = len(chunk)
            length_downloaded += downlen
            yield DownloadProgress(
                length or (length_skipped + length_downloaded),
                length_downloaded,
                length_skipped,
                downlen,
                extra,
            )
    finally:
        if hasattr(resp, "aclose"):
            await resp.aclose()
        else:
            await ensure_async(resp.close)()
        if close_file and fdst is not None:
            await ensure_async(fdst.close)()


async def download_async(
    url: str | Callable[[], Any],
    file: bytes | str | PathLike[Any] | SupportsWrite[bytes] = "",
    resume: bool = False,
    chunksize: int = COPY_BUFSIZE,
    headers: dict[str, str] | Callable[[], Any] | None = None,
    urlopen: Callable[..., Any] = _default_async_urlopen,
    iter_bytes: Callable[[Any], Any] = _default_async_iter_bytes,
    make_reporthook: Callable[[int | None], Any] | None = None,
) -> DownloadProgress:
    update: Callable[[int], Any] | None = None
    close: Callable[[], Any] | None = None
    download_gen = download_async_iter(
        url,
        file,
        resume=resume,
        chunksize=chunksize,
        headers=headers,
        urlopen=urlopen,
        iter_bytes=iter_bytes,
    )
    progress = DownloadProgress(0, 0, 0)
    try:
        if make_reporthook is not None:
            progress = await anext(download_gen)
            reporthook = make_reporthook(progress.total)
            if isinstance(reporthook, AsyncGenerator):
                await anext(reporthook)
                update = reporthook.asend
                close = reporthook.aclose
            elif isinstance(reporthook, Generator):
                await to_thread(next, reporthook)
                update = ensure_async(reporthook.send)
                close = reporthook.close
            else:
                update = ensure_async(reporthook)
                close = getattr(reporthook, "close", None)
            if update is not None:
                await update(progress.last_increment)
        if update is None:
            async for item in download_gen:
                progress = item
        else:
            async for progress in download_gen:
                await update(progress.last_increment)
        return progress
    finally:
        await download_gen.aclose()
        if close is not None:
            await ensure_async(close)()
