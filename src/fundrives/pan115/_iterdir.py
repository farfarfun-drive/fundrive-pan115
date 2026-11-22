"""通用目录树遍历工具（替代 _vendor/iterdir.py 中的 iterdir_generic / walk_generic）。"""

from __future__ import annotations

from collections import deque
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Iterable,
    Iterator,
)
from inspect import isasyncgenfunction, isawaitable
from typing import Any, Literal, cast, overload

from fundrives.pan115._vendor.asynctools import ensure_aiter

__all__ = ["iterdir_generic", "walk_generic"]


def _stop_and_skip(pred: Any, /) -> bool:
    return type(pred) is int and pred == 0


def _stop_after_yield(pred: Any, /) -> bool:
    return type(pred) is int and pred == 1


def _isdir(path: Any, /) -> bool:
    is_dir = getattr(path, "isdir", None)
    if is_dir is None:
        is_dir = getattr(path, "is_dir", None)
    if callable(is_dir):
        is_dir = is_dir()
    return bool(is_dir)


async def _isdir_async(path: Any, /) -> bool:
    is_dir = getattr(path, "isdir", None)
    if is_dir is None:
        is_dir = getattr(path, "is_dir", None)
    if callable(is_dir):
        is_dir = is_dir()
    if isawaitable(is_dir):
        is_dir = await is_dir
    return bool(is_dir)


def _iterdir_bfs[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P]],
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool] | None = None,
    predicate: Callable[[P], Any] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
) -> Iterator[P]:
    if not max_depth or min_depth > max_depth > 0:
        return
    check_dir = _isdir if isdir is None else isdir
    dq: deque[tuple[int, Any]] = deque([(0, top)])
    while dq:
        depth, cur = dq.popleft()
        depth += 1
        can_step_in = max_depth < 0 or depth < max_depth
        try:
            for entry in iterdir(cur):
                pred = True if predicate is None else predicate(entry)
                if _stop_and_skip(pred):
                    continue
                if pred and depth >= min_depth:
                    yield entry
                if can_step_in and not _stop_after_yield(pred) and check_dir(entry):
                    dq.append((depth, entry))
        except OSError as e:
            if callable(onerror):
                onerror(e)
            elif onerror:
                raise


async def _iterdir_bfs_async[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P] | AsyncIterable[P]],
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool | Awaitable[bool]] | None = None,
    predicate: Callable[[P], Any] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
) -> AsyncIterator[P]:
    if not max_depth or min_depth > max_depth > 0:
        return
    check_dir = _isdir_async if isdir is None else isdir
    dq: deque[tuple[int, Any]] = deque([(0, top)])
    while dq:
        depth, cur = dq.popleft()
        depth += 1
        can_step_in = max_depth < 0 or depth < max_depth
        try:
            async for entry in ensure_aiter(iterdir(cur)):
                pred = True if predicate is None else predicate(entry)
                if isawaitable(pred):
                    pred = await pred
                if _stop_and_skip(pred):
                    continue
                if pred and depth >= min_depth:
                    yield entry
                if can_step_in and not _stop_after_yield(pred):
                    is_dir = check_dir(entry)
                    if isawaitable(is_dir):
                        is_dir = await is_dir
                    if is_dir:
                        dq.append((depth, entry))
        except OSError as e:
            if callable(onerror):
                ret = onerror(e)
                if isawaitable(ret):
                    await ret
            elif onerror:
                raise


def _iterdir_dfs[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P]],
    topdown: bool = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool] | None = None,
    predicate: Callable[[P], Any] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
) -> Iterator[P]:
    if not max_depth or min_depth > max_depth > 0:
        return
    check_dir = _isdir if isdir is None else isdir
    if min_depth > 1:
        global_yield = False
        min_depth -= 1
    else:
        global_yield = True
    try:
        max_depth -= max_depth > 0
        for entry in iterdir(top):
            pred = True if predicate is None else predicate(entry)
            if _stop_and_skip(pred):
                continue
            yield_me = global_yield and pred
            if yield_me and topdown:
                yield entry
            if max_depth and not _stop_after_yield(pred) and check_dir(entry):
                yield from _iterdir_dfs(
                    entry,
                    iterdir=iterdir,
                    topdown=topdown,
                    min_depth=min_depth,
                    max_depth=max_depth,
                    isdir=check_dir,
                    predicate=predicate,
                    onerror=onerror,
                )
            if yield_me and not topdown:
                yield entry
    except OSError as e:
        if callable(onerror):
            onerror(e)
        elif onerror:
            raise


async def _iterdir_dfs_async[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P] | AsyncIterable[P]],
    topdown: bool = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool | Awaitable[bool]] | None = None,
    predicate: Callable[[P], Any] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
) -> AsyncIterator[P]:
    if not max_depth or min_depth > max_depth > 0:
        return
    check_dir = _isdir_async if isdir is None else isdir
    if min_depth > 1:
        global_yield = False
        min_depth -= 1
    else:
        global_yield = True
    try:
        max_depth -= max_depth > 0
        async for entry in ensure_aiter(iterdir(top)):
            pred = True if predicate is None else predicate(entry)
            if isawaitable(pred):
                pred = await pred
            if _stop_and_skip(pred):
                continue
            yield_me = global_yield and pred
            if yield_me and topdown:
                yield entry
            if max_depth and not _stop_after_yield(pred):
                is_dir = check_dir(entry)
                if isawaitable(is_dir):
                    is_dir = await is_dir
                if is_dir:
                    async for subentry in _iterdir_dfs_async(
                        entry,
                        iterdir=iterdir,
                        topdown=topdown,
                        min_depth=min_depth,
                        max_depth=max_depth,
                        isdir=check_dir,
                        predicate=predicate,
                        onerror=onerror,
                    ):
                        yield subentry
            if yield_me and not topdown:
                yield entry
    except OSError as e:
        if callable(onerror):
            ret = onerror(e)
            if isawaitable(ret):
                await ret
        elif onerror:
            raise


@overload
def iterdir_generic[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P]],
    topdown: bool | None = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool] | None = None,
    predicate: None | bool | Callable[[P], Any] = None,
    onerror: bool | Callable[[OSError], Any] = False,
    *,
    async_: Literal[False] = False,
) -> Iterator[P]: ...
@overload
def iterdir_generic[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P] | AsyncIterable[P]],
    topdown: bool | None = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool | Awaitable[bool]] | None = None,
    predicate: None | bool | Callable[[P], Any] = None,
    onerror: bool | Callable[[OSError], Any] = False,
    *,
    async_: Literal[True],
) -> AsyncIterator[P]: ...
def iterdir_generic[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P] | AsyncIterable[P]],
    topdown: bool | None = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool | Awaitable[bool]] | None = None,
    predicate: None | bool | Callable[[P], Any] = None,
    onerror: bool | Callable[[OSError], Any] = False,
    *,
    async_: bool = False,
) -> Iterator[P] | AsyncIterator[P]:
    if isasyncgenfunction(iterdir):
        async_ = True
    pred_fn: Callable[[P], Any] | None
    if isinstance(predicate, bool):
        if async_:
            check_dir_a = _isdir_async if isdir is None else isdir
            if predicate:

                async def _not_dir(e: P, /) -> bool:
                    res = check_dir_a(e)
                    if isawaitable(res):
                        res = await res
                    return not res

                pred_fn = _not_dir
            else:
                pred_fn = check_dir_a
        else:
            check_dir_s = cast(Callable[[P], bool], _isdir if isdir is None else isdir)
            pred_fn = (lambda e: not check_dir_s(e)) if predicate else check_dir_s
    else:
        pred_fn = predicate

    if topdown is None:
        if async_:
            return _iterdir_bfs_async(
                top,
                iterdir=iterdir,
                min_depth=min_depth,
                max_depth=max_depth,
                isdir=isdir,
                predicate=pred_fn,
                onerror=onerror,
            )
        return _iterdir_bfs(
            top,
            iterdir=cast(Callable[..., Iterable[P]], iterdir),
            min_depth=min_depth,
            max_depth=max_depth,
            isdir=cast(Callable[[P], bool] | None, isdir),
            predicate=pred_fn,
            onerror=onerror,
        )
    if async_:
        return _iterdir_dfs_async(
            top,
            iterdir=iterdir,
            topdown=topdown,
            min_depth=min_depth,
            max_depth=max_depth,
            isdir=isdir,
            predicate=pred_fn,
            onerror=onerror,
        )
    return _iterdir_dfs(
        top,
        iterdir=cast(Callable[..., Iterable[P]], iterdir),
        topdown=topdown,
        min_depth=min_depth,
        max_depth=max_depth,
        isdir=cast(Callable[[P], bool] | None, isdir),
        predicate=pred_fn,
        onerror=onerror,
    )


def _walk_bfs[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P]],
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
) -> Iterator[tuple[Any, list[P], list[P]]]:
    if not max_depth or min_depth > max_depth > 0:
        return
    check_dir = _isdir if isdir is None else isdir
    dq: deque[tuple[int, Any]] = deque([(0, top)])
    while dq:
        depth, cur = dq.popleft()
        depth += 1
        can_step_in = max_depth < 0 or depth < max_depth
        try:
            files: list[P] = []
            dirs: list[P] = []
            for entry in iterdir(cur):
                if check_dir(entry):
                    if can_step_in:
                        dq.append((depth, entry))
                    dirs.append(entry)
                else:
                    files.append(entry)
        except OSError as e:
            if callable(onerror):
                onerror(e)
            elif onerror:
                raise
        else:
            if depth >= min_depth:
                yield cur, dirs, files


async def _walk_bfs_async[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P] | AsyncIterable[P]],
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool | Awaitable[bool]] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
) -> AsyncIterator[tuple[Any, list[P], list[P]]]:
    if not max_depth or min_depth > max_depth > 0:
        return
    check_dir = _isdir_async if isdir is None else isdir
    dq: deque[tuple[int, Any]] = deque([(0, top)])
    while dq:
        depth, cur = dq.popleft()
        depth += 1
        can_step_in = max_depth < 0 or depth < max_depth
        try:
            files: list[P] = []
            dirs: list[P] = []
            async for entry in ensure_aiter(iterdir(cur)):
                is_dir = check_dir(entry)
                if isawaitable(is_dir):
                    is_dir = await is_dir
                if is_dir:
                    if can_step_in:
                        dq.append((depth, entry))
                    dirs.append(entry)
                else:
                    files.append(entry)
            if depth >= min_depth:
                yield cur, dirs, files
        except OSError as e:
            if callable(onerror):
                ret = onerror(e)
                if isawaitable(ret):
                    await ret
            elif onerror:
                raise


def _walk_dfs[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P]],
    topdown: bool = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
) -> Iterator[tuple[Any, list[P], list[P]]]:
    if not max_depth or min_depth > max_depth > 0:
        return
    check_dir = _isdir if isdir is None else isdir
    if min_depth > 1:
        yield_me = False
        min_depth -= 1
    else:
        yield_me = True
    try:
        files: list[P] = []
        dirs: list[P] = []
        for entry in iterdir(top):
            if check_dir(entry):
                dirs.append(entry)
            else:
                files.append(entry)
    except OSError as e:
        if callable(onerror):
            onerror(e)
        elif onerror:
            raise
    else:
        if yield_me and topdown:
            yield top, dirs, files
        max_depth -= max_depth > 0
        if max_depth:
            for entry in dirs:
                yield from _walk_dfs(
                    entry,
                    iterdir=iterdir,
                    topdown=topdown,
                    min_depth=min_depth,
                    max_depth=max_depth,
                    isdir=check_dir,
                    onerror=onerror,
                )
        if yield_me and not topdown:
            yield top, dirs, files


async def _walk_dfs_async[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P] | AsyncIterable[P]],
    topdown: bool = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool | Awaitable[bool]] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
) -> AsyncIterator[tuple[Any, list[P], list[P]]]:
    if not max_depth or min_depth > max_depth > 0:
        return
    check_dir = _isdir_async if isdir is None else isdir
    if min_depth > 1:
        yield_me = False
        min_depth -= 1
    else:
        yield_me = True
    try:
        files: list[P] = []
        dirs: list[P] = []
        async for entry in ensure_aiter(iterdir(top)):
            is_dir = check_dir(entry)
            if isawaitable(is_dir):
                is_dir = await is_dir
            if is_dir:
                dirs.append(entry)
            else:
                files.append(entry)
    except OSError as e:
        if callable(onerror):
            ret = onerror(e)
            if isawaitable(ret):
                await ret
        elif onerror:
            raise
    else:
        if yield_me and topdown:
            yield top, dirs, files
        max_depth -= max_depth > 0
        if max_depth:
            for entry in dirs:
                async for subentry in _walk_dfs_async(
                    entry,
                    iterdir=iterdir,
                    topdown=topdown,
                    min_depth=min_depth,
                    max_depth=max_depth,
                    isdir=check_dir,
                    onerror=onerror,
                ):
                    yield subentry
        if yield_me and not topdown:
            yield top, dirs, files


@overload
def walk_generic[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P]],
    topdown: bool | None = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
    *,
    async_: Literal[False] = False,
) -> Iterator[tuple[Any, list[P], list[P]]]: ...
@overload
def walk_generic[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P] | AsyncIterable[P]],
    topdown: bool | None = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool | Awaitable[bool]] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
    *,
    async_: Literal[True],
) -> AsyncIterator[tuple[Any, list[P], list[P]]]: ...
def walk_generic[P](
    top: Any,
    /,
    iterdir: Callable[..., Iterable[P] | AsyncIterable[P]],
    topdown: bool | None = True,
    min_depth: int = 1,
    max_depth: int = 1,
    isdir: Callable[[P], bool | Awaitable[bool]] | None = None,
    onerror: bool | Callable[[OSError], Any] = False,
    *,
    async_: bool = False,
) -> (
    Iterator[tuple[Any, list[P], list[P]]] | AsyncIterator[tuple[Any, list[P], list[P]]]
):
    if isasyncgenfunction(iterdir):
        async_ = True
    if topdown is None:
        if async_:
            return _walk_bfs_async(
                top,
                iterdir=iterdir,
                min_depth=min_depth,
                max_depth=max_depth,
                isdir=isdir,
                onerror=onerror,
            )
        return _walk_bfs(
            top,
            iterdir=cast(Callable[..., Iterable[P]], iterdir),
            min_depth=min_depth,
            max_depth=max_depth,
            isdir=cast(Callable[[P], bool] | None, isdir),
            onerror=onerror,
        )
    if async_:
        return _walk_dfs_async(
            top,
            iterdir=iterdir,
            topdown=topdown,
            min_depth=min_depth,
            max_depth=max_depth,
            isdir=isdir,
            onerror=onerror,
        )
    return _walk_dfs(
        top,
        iterdir=cast(Callable[..., Iterable[P]], iterdir),
        topdown=topdown,
        min_depth=min_depth,
        max_depth=max_depth,
        isdir=cast(Callable[[P], bool] | None, isdir),
        onerror=onerror,
    )
