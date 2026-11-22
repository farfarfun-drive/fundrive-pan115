"""文件流摘要与 eD2k 哈希计算（替代 _vendor/hashtools.py 和 _vendor/ed2k.py）。"""

from __future__ import annotations

from binascii import crc32
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Buffer,
    Callable,
    Iterable,
    Iterator,
    Sized,
)
from hashlib import new as hash_new
from inspect import isawaitable
from os import fstat
from typing import Any, Final, Protocol, runtime_checkable

from Crypto.Hash.MD4 import MD4Hash

from fundrives.pan115._vendor.asynctools import ensure_aiter, ensure_async
from fundrives.pan115._vendor.filewrap import (
    SupportsRead,
    SupportsReadinto,
    bio_chunk_async_iter,
    bio_chunk_iter,
    bio_skip_async_iter,
    bio_skip_iter,
    bytes_async_iter,
    bytes_async_iter_skip,
    bytes_iter,
    bytes_iter_skip,
    bytes_to_chunk_async_iter,
    bytes_to_chunk_iter,
)

__all__ = [
    "Ed2kHash",
    "HashObj",
    "ed2k_hash",
    "ed2k_hash_async",
    "file_digest",
    "file_digest_async",
    "file_mdigest",
    "file_mdigest_async",
]

MD4_BLOCK_SIZE: Final = 1024 * 9500
MD4_EMPTY_HASH: Final = b"1\xd6\xcf\xe0\xd1j\xe91\xb7<Y\xd7\xe0\xc0\x89\xc0"


def _buf_len(b: Buffer, /) -> int:
    return len(b) if isinstance(b, Sized) else len(memoryview(b))


def _slicable(b: Buffer, /) -> bytes | bytearray | memoryview:
    return b if isinstance(b, (bytes, bytearray, memoryview)) else memoryview(b)


@runtime_checkable
class HashObj(Protocol):
    def update(self, data: Any, /) -> Any: ...
    def digest(self, /) -> bytes: ...
    def hexdigest(self, /) -> str: ...


# ---------------------------------------------------------------------------
# eD2k 哈希（替代 _vendor/ed2k.py）
# ---------------------------------------------------------------------------


class Ed2kHash:
    def __init__(self, b: Buffer = b"", /):
        self.block_hashes = bytearray()
        self._last_hashobj = MD4Hash()
        self._remainder = 0
        self.update(b)

    def update(self, b: Buffer, /) -> None:
        size = _buf_len(b)
        if not size:
            return
        m = memoryview(b)
        start = 0
        if self._remainder:
            start = MD4_BLOCK_SIZE - self._remainder
            self._last_hashobj.update(m[:start])
            self.block_hashes[-16:] = self._last_hashobj.digest()
        last_start = start
        if start < size:
            for pos in range(start, size, MD4_BLOCK_SIZE):
                last_start = pos
                self._last_hashobj = MD4Hash(m[pos : pos + MD4_BLOCK_SIZE])
                self.block_hashes += self._last_hashobj.digest()
        self._remainder = (size - last_start) % MD4_BLOCK_SIZE

    def digest(self, /) -> bytes:
        block_hashes = self.block_hashes
        if not self._remainder:
            block_hashes = block_hashes + MD4_EMPTY_HASH
        return MD4Hash(block_hashes).digest()

    def hexdigest(self, /) -> str:
        return self.digest().hex()


def ed2k_hash(file: Buffer | SupportsRead[Buffer]) -> tuple[int, str]:
    if hasattr(file, "getbuffer"):
        file = file.getbuffer()
    chunk_iter: Iterator[Buffer] = (
        bytes_to_chunk_iter(file, chunksize=MD4_BLOCK_SIZE)
        if isinstance(file, Buffer)
        else bio_chunk_iter(file, chunksize=MD4_BLOCK_SIZE, can_buffer=True)
    )
    block_hashes = bytearray()
    filesize = 0
    for chunk in chunk_iter:
        buf = _slicable(chunk)
        block_hashes += MD4Hash(buf).digest()
        filesize += len(buf)
    if not filesize % MD4_BLOCK_SIZE:
        block_hashes += MD4_EMPTY_HASH
    return filesize, MD4Hash(block_hashes).hexdigest()


async def ed2k_hash_async(
    file: Buffer | SupportsRead[Buffer] | SupportsRead[Awaitable[Buffer]],
) -> tuple[int, str]:
    if hasattr(file, "getbuffer"):
        file = file.getbuffer()
    chunk_iter: AsyncIterator[Buffer] = (
        bytes_to_chunk_async_iter(file, chunksize=MD4_BLOCK_SIZE)
        if isinstance(file, Buffer)
        else bio_chunk_async_iter(file, chunksize=MD4_BLOCK_SIZE, can_buffer=True)
    )
    block_hashes = bytearray()
    filesize = 0
    async for chunk in chunk_iter:
        buf = _slicable(chunk)
        block_hashes += MD4Hash(buf).digest()
        filesize += len(buf)
    if not filesize % MD4_BLOCK_SIZE:
        block_hashes += MD4_EMPTY_HASH
    return filesize, MD4Hash(block_hashes).hexdigest()


# ---------------------------------------------------------------------------
# 文件多算法摘要（替代 _vendor/hashtools.py）
# ---------------------------------------------------------------------------


def _file_size(file: Any) -> int:
    try:
        return fstat(file.fileno()).st_size
    except (AttributeError, OSError):
        try:
            return len(file)
        except TypeError as exc:
            raise ValueError(f"can't get file size: {file!r}") from exc


def _resolve_range(file: Any, start: int, stop: int | None) -> tuple[int, int | None]:
    length = -1

    def get_length() -> int:
        nonlocal length
        if length < 0:
            length = _file_size(file)
        return length

    if start < 0:
        start = max(0, start + get_length())
    if stop is not None and stop < 0:
        stop += get_length()
    return start, stop


def file_digest(
    file: Buffer | SupportsRead[Buffer] | SupportsReadinto | Iterable[Buffer],
    digest: Any = "md5",
    /,
    start: int = 0,
    stop: int | None = None,
    chunksize: int = 1 << 16,
    callback: Callable[[int], Any] | None = None,
) -> tuple[int, Any]:
    total, (result,) = file_mdigest(
        file,
        digest,
        start=start,
        stop=stop,
        chunksize=chunksize,
        callback=callback,
    )
    return total, result


def file_mdigest(
    file: Buffer | SupportsRead[Buffer] | SupportsReadinto | Iterable[Buffer],
    digest: Any = "md5",
    /,
    *digests: Any,
    start: int = 0,
    stop: int | None = None,
    chunksize: int = 1 << 16,
    callback: Callable[[int], Any] | None = None,
) -> tuple[int, list[Any]]:
    results: list[Any] = []

    def make_updater(alg: Any, /) -> Callable[[Any], Any]:
        if alg == "crc32":
            idx = len(results)
            results.append(0)

            def _upd_crc(chunk: Any, /) -> int:
                val = crc32(chunk, results[idx])
                results[idx] = val
                return val

            return _upd_crc
        if alg == "ed2k":
            hashobj: Any = Ed2kHash()
        elif isinstance(alg, str):
            hashobj = hash_new(alg)
        elif isinstance(alg, HashObj):
            hashobj = alg
        else:
            hashfunc = alg()
            if isinstance(hashfunc, HashObj):
                hashobj = hashfunc
            else:
                idx = len(results)
                results.append(hashfunc(b""))

                def _upd_acc(chunk: Any, /) -> Any:
                    val = hashfunc(chunk, results[idx])
                    results[idx] = val
                    return val

                return _upd_acc
        results.append(hashobj)
        return hashobj.update

    updaters = [make_updater(digest), *(make_updater(d) for d in digests)]
    if hasattr(file, "getbuffer"):
        file = file.getbuffer()

    b_it: Iterable[Buffer]
    if isinstance(file, Buffer):
        sliced = _slicable(file)[start:stop]
        if not sliced:
            return 0, results
        if callback is not None:
            callback(start)
        b_it = bytes_to_chunk_iter(sliced, chunksize=chunksize)
    elif isinstance(file, (SupportsRead, SupportsReadinto)):
        start, stop = _resolve_range(file, start, stop)
        if stop is not None and (stop <= 0 or start >= stop):
            return 0, results
        if start:
            for _ in bio_skip_iter(file, start, callback=callback):
                pass
        b_it = (
            bio_chunk_iter(file, stop - start, chunksize=chunksize, can_buffer=True)
            if stop
            else bio_chunk_iter(file, chunksize=chunksize, can_buffer=True)
        )
    else:
        if start < 0 or (stop is not None and stop < 0):
            raise ValueError(
                "negative indices should not be used when using `Iterable[Buffer]`"
            )
        if stop and start >= stop:
            return 0, results
        b_it = file
        if start:
            b_it = bytes_iter_skip(b_it, start, callback=callback)
        if stop:
            b_it = bytes_iter(b_it, stop - start)

    length = 0
    for chunk in b_it:
        buf = _slicable(chunk)
        for upd in updaters:
            upd(buf)
        size = len(buf)
        length += size
        if callback is not None:
            callback(size)
    return length, results


async def file_digest_async(
    file: Buffer
    | SupportsRead[Buffer]
    | SupportsReadinto
    | Iterable[Buffer]
    | AsyncIterable[Buffer],
    digest: Any = "md5",
    /,
    start: int = 0,
    stop: int | None = None,
    chunksize: int = 1 << 16,
    callback: Callable[[int], Any] | None = None,
) -> tuple[int, Any]:
    total, (result,) = await file_mdigest_async(
        file,
        digest,
        start=start,
        stop=stop,
        chunksize=chunksize,
        callback=callback,
    )
    return total, result


async def file_mdigest_async(
    file: Buffer
    | SupportsRead[Buffer]
    | SupportsReadinto
    | Iterable[Buffer]
    | AsyncIterable[Buffer],
    digest: Any = "md5",
    /,
    *digests: Any,
    start: int = 0,
    stop: int | None = None,
    chunksize: int = 1 << 16,
    callback: Callable[[int], Any] | None = None,
) -> tuple[int, list[Any]]:
    results: list[Any] = []

    async def make_updater(alg: Any, /) -> Callable[[Any], Awaitable[Any]]:
        if alg == "crc32":
            idx = len(results)
            results.append(0)

            async def _upd_crc(chunk: Any, /) -> int:
                val = crc32(chunk, results[idx])
                results[idx] = val
                return val

            return _upd_crc
        if alg == "ed2k":
            hashobj: Any = Ed2kHash()
        elif isinstance(alg, str):
            hashobj = hash_new(alg)
        elif isinstance(alg, HashObj):
            hashobj = alg
        else:
            hashfunc = alg()
            if isinstance(hashfunc, HashObj):
                hashobj = hashfunc
            else:
                init = hashfunc(b"")
                if isawaitable(init):
                    init = await init
                idx = len(results)
                results.append(init)

                async def _upd_acc(chunk: Any, /) -> Any:
                    val = hashfunc(chunk, results[idx])
                    if isawaitable(val):
                        val = await val
                    results[idx] = val
                    return val

                return _upd_acc
        results.append(hashobj)
        return ensure_async(hashobj.update)

    updaters = [
        await make_updater(digest),
        *[await make_updater(d) for d in digests],
    ]
    acallback = ensure_async(callback) if callback is not None else None
    if hasattr(file, "getbuffer"):
        file = file.getbuffer()

    b_it: AsyncIterator[Buffer]
    if isinstance(file, Buffer):
        sliced = _slicable(file)[start:stop]
        if not sliced:
            return 0, results
        if acallback is not None:
            await acallback(start)
        b_it = bytes_to_chunk_async_iter(sliced, chunksize=chunksize)
    elif isinstance(file, (SupportsRead, SupportsReadinto)):
        start, stop = _resolve_range(file, start, stop)
        if stop is not None and (stop <= 0 or start >= stop):
            return 0, results
        if start:
            async for _ in bio_skip_async_iter(file, start, callback=acallback):
                pass
        b_it = (
            bio_chunk_async_iter(
                file, stop - start, chunksize=chunksize, can_buffer=True
            )
            if stop
            else bio_chunk_async_iter(file, chunksize=chunksize, can_buffer=True)
        )
    else:
        if start < 0 or (stop is not None and stop < 0):
            raise ValueError(
                "negative indices should not be used when using `Iterable[Buffer]`"
            )
        if stop and start >= stop:
            return 0, results
        b_it = ensure_aiter(file)
        if start:
            b_it = await bytes_async_iter_skip(b_it, start, callback=acallback)
        if stop:
            b_it = bytes_async_iter(b_it, stop - start)

    length = 0
    async for chunk in b_it:
        buf = _slicable(chunk)
        for upd in updaters:
            await upd(buf)
        size = len(buf)
        length += size
        if acallback is not None:
            await acallback(size)
    return length, results
